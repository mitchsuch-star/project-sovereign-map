"""
Command Executor for Project Sovereign
Executes parsed commands against game state with region conquest

Includes Disobedience System (Phase 2):
- Checks for marshal objections before executing orders
- Handles major objections by pausing execution for player choice
- Updates vindication tracker after battles

TODO (Future): Multi-Army Battles
- Support 3+ marshals vs 2+ enemies in same region
- Multi-step commands (e.g., "Ney and Davout, attack Wellington")
- Combined strength calculations with command bonuses
- Coordinated attacks with flanking bonuses
"""
import random
from typing import Dict, List, Optional, Tuple
from backend.models.world_state import (
    WorldState,
    INFANTRY_RECRUIT_AMOUNT, CAVALRY_RECRUIT_AMOUNT, ARTILLERY_RECRUIT_AMOUNT,
    INFANTRY_RECRUIT_GOLD_COST_BASE, CAVALRY_RECRUIT_GOLD_COST_BASE, ARTILLERY_RECRUIT_GOLD_COST_BASE,
    INFANTRY_BASE_REGEN,
)
from backend.models.marshal import Stance, StrategicOrder
from backend.models.region import CHARGE_BLOCKED_TERRAIN, TERRAIN_DEFENSE_BONUS
from backend.game_logic.combat import CombatResolver
from backend.game_logic.turn_manager import TurnManager
from backend.utils.fuzzy_matcher import FuzzyMatcher
# V2a Objection System imports
from backend.commands.objection_v2 import (
    ConcernLevel, evaluate_situation, evaluate_strategic_situation,
    apply_mood_variance,
    get_trust_tier, get_objection_tone, get_insist_penalty,
    calculate_trust_gain, COMPROMISE_TRUST_GAIN,
    concern_to_legacy_severity,
)


# Player-readable display names for internal action strings.
# Internal action names must NEVER reach the frontend raw — always translate first.
_ACTION_DISPLAY_NAMES = {
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
}


# Actions that consume Admin AP instead of CP (Phase 6.2.B)
ADMIN_ACTIONS = {"recruit", "build", "repair"}


def _action_display_name(action: str) -> str:
    """Translate internal action name to player-readable text."""
    return _ACTION_DISPLAY_NAMES.get(action, action.replace("_", " "))


def _proposal_display_name(proposal_type: str) -> str:
    """Translate internal proposal_type to player-readable text."""
    from backend.game_logic.diplomatic_dialogue import PROPOSAL_TYPE_DISPLAY
    return PROPOSAL_TYPE_DISPLAY.get(proposal_type, proposal_type.replace("_", " ").title())


class CommandExecutor:
    """
    Executes validated commands and returns results.
    Handles smart command routing based on game state.
    """

    def __init__(self):
        """Initialize the command executor."""
        self.combat_resolver = CombatResolver()
        self.fuzzy_matcher = FuzzyMatcher()
        print("Command Executor initialized")

    def _fuzzy_match_marshal(self, marshal_name: str, world: WorldState) -> Tuple[Optional[object], Optional[Dict]]:
        """
        Try to find marshal with fuzzy matching for typo tolerance.

        Returns:
            Tuple of (marshal_object, error_dict)
            - If exact match or auto-correct: (marshal, None)
            - If suggestion or error: (None, error_dict)
        """
        # Try exact match first
        marshal = world.get_marshal(marshal_name)
        if marshal:
            return (marshal, None)

        # Get all marshal names for fuzzy matching (player + enemy)
        all_marshals = list(world.marshals.keys())

        if not all_marshals:
            return (None, {
                "success": False,
                "message": "No marshals available"
            })

        # Try fuzzy match
        result = self.fuzzy_matcher.match_with_context(marshal_name, all_marshals)

        if result["action"] == "exact" or result["action"] == "auto_correct":
            # Exact match or high confidence - use corrected name
            marshal = world.get_marshal(result["match"])
            return (marshal, None)
        elif result["action"] == "suggest":
            # Medium confidence - ask for confirmation
            return (None, {
                "success": False,
                "message": f"Marshal '{marshal_name}' not found. Did you mean '{result['match']}'?",
                "suggestion": result["match"],
                "score": int(result["score"] * 100)
            })
        else:
            # Low confidence - show suggestions
            suggestions_text = ", ".join(result["suggestions"][:3]) if result["suggestions"] else "none"
            return (None, {
                "success": False,
                "message": f"Marshal '{marshal_name}' not found. Available: {suggestions_text}",
                "suggestions": result["suggestions"]
            })

    def _fuzzy_match_region(self, region_name: str, world: WorldState) -> Tuple[Optional[object], Optional[Dict]]:
        """
        Try to find region with fuzzy matching for typo tolerance.

        Returns:
            Tuple of (region_object, error_dict)
            - If exact match or auto-correct: (region, None)
            - If suggestion or error: (None, error_dict)
        """
        # Try exact match first
        region = world.get_region(region_name)
        if region:
            return (region, None)

        # Get all region names for fuzzy matching
        all_regions = list(world.regions.keys())

        if not all_regions:
            return (None, {
                "success": False,
                "message": "No regions available"
            })

        # Try fuzzy match
        result = self.fuzzy_matcher.match_with_context(region_name, all_regions)

        if result["action"] == "exact" or result["action"] == "auto_correct":
            # Exact match or high confidence - use corrected name
            region = world.get_region(result["match"])
            return (region, None)
        elif result["action"] == "suggest":
            # Medium confidence - ask for confirmation
            return (None, {
                "success": False,
                "message": f"Region '{region_name}' not found. Did you mean '{result['match']}'?",
                "suggestion": result["match"],
                "score": int(result["score"] * 100)
            })
        else:
            # Low confidence - show suggestions
            suggestions_text = ", ".join(result["suggestions"][:3]) if result["suggestions"] else "none"
            return (None, {
                "success": False,
                "message": f"Region '{region_name}' not found. Nearby: {suggestions_text}",
                "suggestions": result["suggestions"]
            })

    # ════════════════════════════════════════════════════════════════════════════════
    # MULTI-MARSHAL COORDINATION (Phase 7, Session 57+)
    # Combined arms detection, coordination bonuses, dedicated support, adjacent support.
    # Session 57: Combined arms only. Later sessions add other coordination sources.
    # ════════════════════════════════════════════════════════════════════════════════

    def _count_unit_types(self, region: str, nation: str, world: WorldState) -> int:
        """
        Count distinct unit types among eligible same-nation marshals in a region.

        Eligible: alive (strength > 0), not broken, not retreating, not recovering.
        Garrison detachments do NOT count (region property, not marshal).
        Fortified marshals DO count — their presence matters.

        Returns 1-3 (infantry, cavalry, artillery).
        """
        types_seen = set()
        for m in world.marshals.values():
            if m.location != region or m.nation != nation:
                continue
            if m.strength <= 0:
                continue
            if getattr(m, 'broken', False):
                continue
            if getattr(m, 'retreated_this_turn', False):
                continue
            if getattr(m, 'retreat_recovery', 0) > 0:
                continue
            # Determine unit type
            if getattr(m, 'artillery', False):
                types_seen.add('artillery')
            elif getattr(m, 'cavalry', False):
                types_seen.add('cavalry')
            else:
                types_seen.add('infantry')
        return len(types_seen)

    def _get_combined_arms_bonus(self, type_count: int) -> tuple:
        """
        Get combined arms attack/defense bonus from unit type diversity.

        Returns (attack_bonus, defense_bonus) as floats.
        1 type = (0.0, 0.0), 2 types = (0.10, 0.05), 3 types = (0.20, 0.10).
        """
        if type_count >= 3:
            return (0.20, 0.10)
        elif type_count >= 2:
            return (0.10, 0.05)
        return (0.0, 0.0)

    # Relationship → coordination scaling factors (§3 of MULTI_MARSHAL_SPEC)
    _RELATIONSHIP_SCALING = {-2: 0.0, -1: 0.50, 0: 1.0, 1: 1.25, 2: 1.50}

    def _calculate_per_ally_coordination(self, marshal, allies) -> tuple:
        """
        Calculate per-ally relationship-scaled coordination bonus.

        Each eligible ally contributes:
        - Attack: +3% × relationship_scaling (0.0 to 1.5)
        - Defense: +5% × relationship_scaling (0.0 to 1.5)

        Fortification rule:
        - Fortified non-artillery: defense coordination ONLY (no attack contribution)
        - Fortified artillery: BOTH attack and defense

        Returns:
            (total_atk, total_def) as floats (e.g. 0.03 = 3%)
        """
        total_atk = 0.0
        total_def = 0.0

        for ally in allies:
            rel = marshal.get_relationship(ally.name)
            scale = self._RELATIONSHIP_SCALING.get(rel, 1.0)

            is_fortified_non_artillery = (
                getattr(ally, 'fortified', False)
                and not getattr(ally, 'artillery', False)
            )
            # Attack coordination: skip fortified non-artillery
            if not is_fortified_non_artillery:
                total_atk += 0.03 * scale

            # Defense coordination: all eligible allies contribute
            total_def += 0.05 * scale

        return (total_atk, total_def)

    def _count_adjacent_allies(self, region_name, nation, world, exclude_names=None):
        """Count eligible same-nation marshals in regions adjacent to the battle region.

        Adjacent support is ATTACK-ONLY (A-M2). +2% per adjacent ally.
        Fortified and HOLD marshals count (physically present).
        NOT relationship-scaled (purely positional).

        Args:
            region_name: The battle region
            nation: The nation to filter for
            world: WorldState
            exclude_names: Set of marshal names to exclude (used by S61 reinforcement)

        Returns:
            tuple: (count of adjacent allies, list of adjacent ally names)
        """
        if exclude_names is None:
            exclude_names = set()

        region = world.get_region(region_name)
        if not region:
            return (0, [])

        adjacent_allies = []
        for m in world.marshals.values():
            if (m.nation == nation
                    and m.name not in exclude_names
                    and m.location in region.adjacent_regions
                    and m.location != region_name
                    and m.strength > 0
                    and not getattr(m, 'broken', False)
                    and not getattr(m, 'retreated_this_turn', False)
                    and getattr(m, 'retreat_recovery', 0) == 0):
                adjacent_allies.append(m.name)

        return (len(adjacent_allies), adjacent_allies)

    def _calculate_coordination_context(self, primary, world: WorldState,
                                         reinforcement_results=None,
                                         exclude_from_adjacent=None) -> dict:
        """
        Calculate coordination bonuses for primary marshal and same-nation allies.

        Session 57: Combined arms detection.
        Session 58: Per-ally relationship-scaled coordination bonuses.
        Session 59: Dedicated coordination bonus.
        Session 60: Adjacent support bonus (attack-only per A-M2).
        Session 61a: reinforcement_results parameter for A-C2 SUPPORT timing.

        Each eligible marshal gets their OWN coordination total based on their
        individual relationships (asymmetric — A→B may differ from B→A).

        Sets transient fields on each eligible marshal:
        - total_coordination_attack_bonus / total_coordination_defense_bonus (capped)
        - _display_combined_arms_atk / _display_combined_arms_def (for battle report)
        - _display_coordination_atk / _display_coordination_def (for battle report)
        - _display_adjacent_atk (for battle report, attack-only)

        Returns context dict for debugging/display.
        """
        region = primary.location
        nation = primary.nation

        # Count distinct unit types among eligible same-nation marshals in region
        type_count = self._count_unit_types(region, nation, world)
        combined_arms_atk, combined_arms_def = self._get_combined_arms_bonus(type_count)

        # Adjacent support (S60) — ATTACK ONLY per A-M2, calculated ONCE (shared value)
        adj_count, adj_names = self._count_adjacent_allies(
            region, nation, world, exclude_names=exclude_from_adjacent)
        adjacent_atk = adj_count * 0.02  # +2% per adjacent ally, no defense component

        # Find all eligible same-nation marshals in region
        eligible = [m for m in world.marshals.values()
                    if m.location == region and m.nation == nation
                    and m.strength > 0
                    and not getattr(m, 'broken', False)
                    and not getattr(m, 'retreated_this_turn', False)
                    and getattr(m, 'retreat_recovery', 0) == 0]

        # Each marshal gets their OWN coordination based on their relationships
        for m in eligible:
            allies_for_m = [a for a in eligible if a.name != m.name]
            coord_atk, coord_def = self._calculate_per_ally_coordination(m, allies_for_m)

            # Dedicated coordination bonus (S59): +5%/+5% flat if qualified
            dedicated_atk = 0.0
            dedicated_def = 0.0
            if allies_for_m and self._has_dedicated_support(m, allies_for_m, world, reinforcement_results):
                dedicated_atk = 0.05
                dedicated_def = 0.05

            # Sum all coordination sources — adjacent is attack-only (A-M2)
            raw_atk = combined_arms_atk + coord_atk + dedicated_atk + adjacent_atk
            raw_def = combined_arms_def + coord_def + dedicated_def  # NO adjacent_def

            # Hard cap
            capped_atk = min(raw_atk, 0.25)
            capped_def = min(raw_def, 0.20)

            m.total_coordination_attack_bonus = capped_atk
            m.total_coordination_defense_bonus = capped_def
            m._display_combined_arms_atk = combined_arms_atk
            m._display_combined_arms_def = combined_arms_def
            m._display_coordination_atk = coord_atk
            m._display_coordination_def = coord_def
            m._display_dedicated_atk = dedicated_atk
            m._display_dedicated_def = dedicated_def
            m._display_adjacent_atk = adjacent_atk

        return {
            "type_count": type_count,
            "combined_arms_atk": combined_arms_atk,
            "combined_arms_def": combined_arms_def,
            "adjacent_count": adj_count,
            "adjacent_names": adj_names,
            "adjacent_atk": adjacent_atk,
            "capped_atk": min(combined_arms_atk, 0.25) if not eligible else getattr(primary, 'total_coordination_attack_bonus', 0.0),
            "capped_def": min(combined_arms_def, 0.20) if not eligible else getattr(primary, 'total_coordination_defense_bonus', 0.0),
            "eligible_marshals": [m.name for m in eligible],
        }

    def _has_dedicated_support(self, marshal, same_region_allies, world,
                               reinforcement_results=None) -> bool:
        """Check if marshal qualifies for +5%/+5% dedicated coordination bonus.

        Path A: Co-location with any ally for 2+ consecutive turns (both player and AI).
        Path B: An ally has an active SUPPORT order targeting this marshal (immediate, one-directional per A-D3).
        Path B2: An ally arrived via SUPPORT this battle (A-C2 safety net — order not yet cleared).
        """
        # Path A: Co-location duration (2+ turns with any ally here)
        for ally in same_region_allies:
            start_turn = marshal.co_location_turns.get(ally.name)
            if start_turn is not None and world.current_turn - start_turn >= 2:
                return True

        # Path B: Active SUPPORT order from an ally targeting THIS marshal (A-D3: one-directional)
        for ally in same_region_allies:
            order = getattr(ally, 'strategic_order', None)
            if (order
                    and order.command_type == "SUPPORT"
                    and order.target == marshal.name):
                return True

        # Path B2: Arrived via SUPPORT this battle (A-C2 safety net)
        if reinforcement_results:
            ally_names = {a.name for a in same_region_allies}
            for result in reinforcement_results:
                if (result.get("arrived_via_support")
                        and result["marshal"] in ally_names):
                    return True

        return False

    # ════════════════════════════════════════════════════════════════════════════════
    # REINFORCEMENT SYSTEM (Phase 7, Session 61a)
    # Adjacent marshals physically relocate to the battle region before combat.
    # ════════════════════════════════════════════════════════════════════════════════

    def _is_reinforcement_eligible(self, marshal, primary, battle_region, nation, world):
        """Check all 11 eligibility rules for adjacent reinforcement.

        A marshal can reinforce if ALL conditions are met.
        Rules are from MULTI_MARSHAL_SPEC §7 + amendments.
        """
        region = world.get_region(battle_region)
        if not region:
            return False

        # Not the primary combatant
        if marshal.name == primary.name:
            return False
        # Rule 1: Same nation
        if marshal.nation != nation:
            return False
        # Rule 2: Adjacent region (not same region, not distant)
        if marshal.location not in region.adjacent_regions:
            return False
        # Rule 3: strength > 0
        if marshal.strength <= 0:
            return False
        # Rule 4: NOT broken
        if getattr(marshal, 'broken', False):
            return False
        # Rule 5: NOT retreated_this_turn
        if getattr(marshal, 'retreated_this_turn', False):
            return False
        # Rule 6: retreat_recovery == 0
        if getattr(marshal, 'retreat_recovery', 0) != 0:
            return False
        # Rule 7: NOT fortified
        if getattr(marshal, 'fortified', False):
            return False
        # Rule 8: NOT on HOLD
        if getattr(marshal, 'holding_position', False):
            return False
        # Rule 9: NOT engaged (no enemy in their region)
        marshal_region_enemies = [
            m for m in world.marshals.values()
            if m.location == marshal.location
            and m.nation != nation
            and m.strength > 0
        ]
        if marshal_region_enemies:
            return False
        # Rule 10: NOT drilling
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return False
        # Rule 11: NOT already reinforced this turn
        if getattr(marshal, 'reinforced_this_turn', False):
            return False
        # Rule 12: NOT moved_this_turn — troops cannot force-march twice (A-D2)
        if getattr(marshal, 'moved_this_turn', False):
            return False
        # Rule 15: NOT in square formation (can't march while formed square)
        if getattr(marshal, 'square_formation', False):
            return False
        # Rule 13: Hostile without SUPPORT cannot auto-reinforce (A-D4)
        # Hostile auto-reinforcement is net-negative: converts +2% adjacent to 0% coordination
        rel = marshal.get_relationship(primary.name)
        if rel == -2:  # Hostile
            order = getattr(marshal, 'strategic_order', None)
            has_support_for_primary = (
                order is not None
                and order.command_type == "SUPPORT"
                and order.target == primary.name
            )
            if not has_support_for_primary:
                return False

        return True

    def _calculate_arrival_score(self, reinforcing_marshal, primary_combatant, world):
        """Calculate deterministic base + components + random variance.

        Formula from MULTI_MARSHAL_SPEC §7:
        score = 50 + logistics*5 + relationship_mod + terrain_mod + personality_mod + support_bonus + variance
        """
        import random

        base = 50

        logistics = reinforcing_marshal.skills.get("logistics", 5)
        logistics_bonus = logistics * 5

        rel = reinforcing_marshal.get_relationship(primary_combatant.name)
        RELATIONSHIP_MOD = {-2: -20, -1: -10, 0: 0, 1: +10, 2: +20}
        rel_mod = RELATIONSHIP_MOD.get(rel, 0)

        departing_region = world.get_region(reinforcing_marshal.location)
        terrain = departing_region.terrain if departing_region else "plains"
        TERRAIN_PENALTY = {
            "plains": 0, "forest": -10, "hills": -5,
            "mountains": -20, "urban": 0, "river_crossing": -5,
        }
        terrain_mod = TERRAIN_PENALTY.get(terrain, 0)

        PERSONALITY_MOD = {
            "aggressive": +5, "cautious": -5, "literal": 0,
            "balanced": 0, "loyal": +3,
        }
        personality_mod = PERSONALITY_MOD.get(
            getattr(reinforcing_marshal, 'personality', 'balanced'), 0
        )

        # SUPPORT order targeting combatant: +10
        support_bonus = 0
        order = getattr(reinforcing_marshal, 'strategic_order', None)
        if (order
                and order.command_type == "SUPPORT"
                and order.target == primary_combatant.name):
            support_bonus = 10

        variance = random.randint(-8, 8)

        return base + logistics_bonus + rel_mod + terrain_mod + personality_mod + support_bonus + variance

    def _calculate_reinforcements(self, primary, defender, battle_region, nation, world):
        """Check adjacent marshals for reinforcement arrival.

        Returns list of result dicts with arrival/failure info.
        Handles: Grouchy Rule, arrival score, variable threshold (A-I4),
        fumble roll (I3), near-miss tracking (N3).
        """
        import random

        reinforcement_results = []
        region = world.get_region(battle_region)
        if not region:
            return reinforcement_results

        # Find eligible adjacent marshals
        candidates = []
        for m in world.marshals.values():
            if not self._is_reinforcement_eligible(m, primary, battle_region, nation, world):
                continue
            candidates.append(m)

        for candidate in candidates:
            # ═══ THE GROUCHY RULE ═══
            # Check personality BEFORE calculating arrival score
            if candidate.personality == "literal":
                has_relevant_order = False
                order = getattr(candidate, 'strategic_order', None)
                if order:
                    if (order.command_type == "SUPPORT"
                            and order.target == primary.name):
                        has_relevant_order = True
                    elif order.command_type == "PURSUE":
                        # A-D1: Region-match — if pursue target is in battle region, it counts
                        pursue_target = world.marshals.get(order.target)
                        if pursue_target and pursue_target.location == battle_region:
                            has_relevant_order = True

                if not has_relevant_order:
                    reinforcement_results.append({
                        "marshal": candidate.name,
                        "arrived": False,
                        "score": None,
                        "threshold": None,
                        "reason": "literal_personality",
                        "near_miss": False,
                        "near_miss_reason": "",
                        "has_explicit_order": False,
                        "message": (
                            f"{candidate.name} continues to follow standing orders. "
                            f"The sound of cannon fire grows louder behind him."
                        ),
                    })
                    continue

            # ═══ ARRIVAL SCORE ═══
            score = self._calculate_arrival_score(candidate, primary, world)

            # ═══ VARIABLE THRESHOLD (A-I4) ═══
            order = getattr(candidate, 'strategic_order', None)
            has_explicit_order = False
            if order is not None:
                if order.command_type == "SUPPORT" and order.target == primary.name:
                    has_explicit_order = True
                elif order.command_type == "PURSUE":
                    # A-D1: Region-match for PURSUE threshold too
                    pursue_tgt = world.marshals.get(order.target)
                    if pursue_tgt and pursue_tgt.location == battle_region:
                        has_explicit_order = True
            threshold = 60 if has_explicit_order else 65
            arrived = score > threshold

            # ═══ FUMBLE ROLL (I3) ═══
            near_miss = False
            near_miss_reason = ""
            if arrived and score > 80:
                if random.randint(1, 20) == 1:  # 5% chance
                    arrived = False
                    near_miss = True
                    near_miss_reason = "Even the best-laid plans can go awry at the crucial moment."

            if arrived:
                reason = "arrived"
            elif near_miss:
                reason = "fate_intervened"
            else:
                reason = "low_score"

            reinforcement_results.append({
                "marshal": candidate.name,
                "arrived": arrived,
                "score": int(score),
                "threshold": int(threshold),
                "reason": reason,
                "near_miss": near_miss,
                "near_miss_reason": near_miss_reason,
                "has_explicit_order": has_explicit_order,
            })

        return reinforcement_results

    # Transient coordination field names for cleanup after combat (D5 + X1)
    _COORDINATION_FIELDS = [
        'total_coordination_attack_bonus', 'total_coordination_defense_bonus',
        '_display_combined_arms_atk', '_display_combined_arms_def',
        '_display_coordination_atk', '_display_coordination_def',
        '_display_dedicated_atk', '_display_dedicated_def',
        '_display_adjacent_atk',
        'overwatch_penalty',  # Session 68: enemy artillery suppression (transient)
    ]

    def _clear_coordination_fields(self, regions: set, world: WorldState) -> None:
        """Clear all transient coordination fields from marshals in the given regions."""
        for m in world.marshals.values():
            if m.location in regions:
                for attr in self._COORDINATION_FIELDS:
                    if hasattr(m, attr):
                        setattr(m, attr, 0.0)

    def _calculate_overwatch(self, attacker, atk_participants, defender_region_name: str, world: WorldState) -> int:
        """Count enemy artillery in defender's region, apply overwatch penalty to all attackers.

        Session 68: Artillery Overwatch — enemy artillery passively debuffs attackers
        by -3% per gun (capped at 3 guns = -9% max).

        Sets transient `overwatch_penalty` on each attacking participant.
        Returns the count of eligible overwatch artillery (for reporting).
        """
        enemy_artillery_count = 0
        overwatch_artillery_names = []
        for m in world.marshals.values():
            if (m.location == defender_region_name
                    and m.nation != attacker.nation
                    and getattr(m, 'artillery', False)
                    and m.strength > 0
                    and not getattr(m, 'broken', False)
                    and not getattr(m, 'retreated_this_turn', False)
                    and getattr(m, 'retreat_recovery', 0) == 0
                    and not getattr(m, 'moved_this_turn', False)):
                enemy_artillery_count += 1
                overwatch_artillery_names.append(m.name)

        capped = min(enemy_artillery_count, 3)  # -9% max
        penalty = capped * 0.03

        if penalty > 0:
            # Apply to ALL attacking participants — the guns suppress the entire assault
            all_attackers = [attacker] + [p for p in (atk_participants or []) if p.name != attacker.name]
            for combatant in all_attackers:
                combatant.overwatch_penalty = penalty
            print(f"  [OVERWATCH] {capped} enemy artillery in {defender_region_name}: "
                  f"-{int(penalty * 100)}% attack ({', '.join(overwatch_artillery_names[:3])})")

        return capped

    # ════════════════════════════════════════════════════════════════════════════
    # CASUALTY DISTRIBUTION (Phase 7, Session 62)
    # Distributes raw casualties proportionally among participating marshals.
    # ════════════════════════════════════════════════════════════════════════════

    def _get_casualty_participants(self, primary, battle_region: str, nation: str,
                                    world: WorldState) -> list:
        """Get participating marshals for casualty distribution.

        Includes:
        - Primary combatant (always)
        - Same-nation allies in region: alive, not broken/retreating/recovering
        - Hostile+SUPPORT marshals (D3: participating for casualties, 0% coordination)

        Excludes:
        - Hostile marshals WITHOUT active SUPPORT order targeting primary (Non-Participating)

        Must be called BEFORE strategic orders are cleared so SUPPORT detection works.
        """
        participants = [primary]

        for m in world.marshals.values():
            if m.name == primary.name:
                continue
            if m.location != battle_region or m.nation != nation:
                continue
            if m.strength <= 0:
                continue
            if getattr(m, 'broken', False):
                continue
            if getattr(m, 'retreated_this_turn', False):
                continue
            if getattr(m, 'retreat_recovery', 0) > 0:
                continue

            # Hostile without SUPPORT = Non-Participating (D3/X4)
            rel = m.get_relationship(primary.name)
            if rel == -2:
                order = getattr(m, 'strategic_order', None)
                has_support = (
                    order is not None
                    and getattr(order, 'command_type', None) == "SUPPORT"
                    and getattr(order, 'target', None) == primary.name
                )
                if not has_support:
                    continue

            participants.append(m)

        return participants

    # Artillery takes 50% of proportional casualties when fighting
    # alongside non-artillery units (positioned behind front lines).
    ARTILLERY_CASUALTY_FACTOR = 0.5

    def _distribute_casualties(self, raw_casualties: int, participants: list) -> dict:
        """Distribute casualties proportionally among participating marshals.

        Returns: dict of marshal_name -> int(casualties)

        Rules:
        - Proportional by strength fraction: marshal_strength / total_strength * raw_casualties
        - Round DOWN each marshal's share (int())
        - Artillery rear-position advantage: when fighting alongside non-artillery
          units, artillery takes 50% of proportional share (the saved casualties
          are redistributed to front-line troops via the remainder mechanism)
        - Assign remainder to strongest non-artillery marshal (or strongest overall)
        - Share capped at marshal's current strength (can't go below 0)
        """
        if not participants:
            return {}

        # Filter out dead participants
        active = [p for p in participants if p.strength > 0]
        if not active:
            return {}

        total_strength = sum(p.strength for p in active)
        if total_strength <= 0:
            return {}

        # Sort by strength descending (strongest first for remainder assignment)
        sorted_active = sorted(active, key=lambda p: p.strength, reverse=True)

        # Artillery casualty reduction: only when fighting with non-artillery allies
        has_non_artillery = any(not getattr(p, 'artillery', False) for p in active)

        # Compute proportional shares (round down)
        shares = {}
        for p in sorted_active:
            fraction = p.strength / total_strength
            raw_share = int(raw_casualties * fraction)
            # Artillery positioned behind lines takes fewer casualties
            if getattr(p, 'artillery', False) and has_non_artillery:
                raw_share = int(raw_share * self.ARTILLERY_CASUALTY_FACTOR)
            shares[p.name] = raw_share

        # Assign remainder to strongest non-artillery marshal (artillery is
        # behind the lines so excess casualties fall on front-line troops).
        # Fall back to strongest overall if all participants are artillery.
        assigned = sum(shares.values())
        remainder = raw_casualties - assigned
        if remainder > 0:
            non_artillery = [p for p in sorted_active if not getattr(p, 'artillery', False)]
            remainder_target = non_artillery[0] if non_artillery else sorted_active[0]
            shares[remainder_target.name] += remainder

        # Cap each share at marshal's current strength.
        # NOTE (W-2): If capping reduces a share, the excess is NOT redistributed.
        # This means sum(shares) may be < raw_casualties in edge cases where a
        # small marshal would be killed multiple times over.  Acceptable: the
        # "lost" casualties represent overkill on a destroyed unit.
        for p in sorted_active:
            shares[p.name] = min(shares[p.name], p.strength)

        return shares

    def _fuzzy_match_enemy(self, enemy_name: str, world: WorldState, attacker_nation: str = None) -> Tuple[Optional[object], Optional[Dict]]:
        """
        Try to find enemy marshal with fuzzy matching for typo tolerance.

        TODO (1805): At 80+ regions, fuzzy matching should be filtered by known
        marshals (from intel store) — player typing "attack Kutuzov" when Kutuzov
        was never scouted should fail or warn. On 13 regions this is acceptable
        since players know all marshal names. See FOG_OF_WAR_SPEC.md §5.1.

        Args:
            enemy_name: Name of the target marshal
            world: WorldState instance
            attacker_nation: Optional nation of the attacker. If provided, finds
                           enemies of that nation. If None, uses player perspective.

        Returns:
            Tuple of (marshal_object, error_dict)
            - If exact match or auto-correct: (marshal, None)
            - If suggestion or error: (None, error_dict)
        """
        # Try exact match first
        if attacker_nation:
            # Nation-aware lookup (for enemy AI)
            enemy = world.get_enemy_by_name_for_nation(enemy_name, attacker_nation)
            all_enemies = [m.name for m in world.get_enemies_of_nation(attacker_nation)]
        else:
            # Player-centric lookup (original behavior)
            enemy = world.get_enemy_by_name(enemy_name)
            all_enemies = [m.name for m in world.get_enemy_marshals() if m.strength > 0]

        if enemy:
            return (enemy, None)

        if not all_enemies:
            return (None, {
                "success": False,
                "message": "No enemies available"
            })

        # Try fuzzy match
        result = self.fuzzy_matcher.match_with_context(enemy_name, all_enemies)

        if result["action"] == "exact" or result["action"] == "auto_correct":
            # Exact match or high confidence - use corrected name
            if attacker_nation:
                enemy = world.get_enemy_by_name_for_nation(result["match"], attacker_nation)
            else:
                enemy = world.get_enemy_by_name(result["match"])
            return (enemy, None)
        elif result["action"] == "suggest":
            # Medium confidence - ask for confirmation
            return (None, {
                "success": False,
                "message": f"Enemy '{enemy_name}' not found. Did you mean '{result['match']}'?",
                "suggestion": result["match"],
                "score": int(result["score"] * 100)
            })
        else:
            # Low confidence - show suggestions
            suggestions_text = ", ".join(result["suggestions"][:3]) if result["suggestions"] else "none"
            return (None, {
                "success": False,
                "message": f"Enemy '{enemy_name}' not found. Available: {suggestions_text}",
                "suggestions": result["suggestions"]
            })

    def _execute_end_turn(self, command: Dict, game_state: Dict) -> Dict:
        """
        End turn early, skipping remaining actions.

        Uses TurnManager to:
        1. Process autonomous marshals
        2. Process ENEMY AI TURNS (all enemy nations take actions)
        3. Process tactical states (drill, fortify, retreat)
        4. Advance turn
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        # Phase 8 Session 3: Block end-turn if blocking diplomatic dialogue pending
        if (world.pending_diplomatic_dialogue
                and world.pending_diplomatic_dialogue.get("blocking")):
            dialogue = world.pending_diplomatic_dialogue
            option_labels = [f"[{i+1}] {o['label']}" for i, o in enumerate(dialogue.get("options", []))]
            options_text = "  ".join(option_labels)
            return {
                "success": False,
                "message": f"You must respond to the diplomatic matter before ending the turn. {options_text}",
                "awaiting_diplomatic_response": True,
                "diplomatic_dialogue": dialogue,
            }

        # V2a: Capture mild concerns BEFORE end_turn clears them
        # (advance_turn resets mild_concerns_this_turn at start)
        saved_mild_concerns = [c.copy() for c in world.mild_concerns_this_turn]

        # Capture gold spending BEFORE advance_turn clears it
        saved_gold_spent = world.gold_spent_this_turn.copy()

        # Use TurnManager to process everything including ENEMY AI
        turn_manager = TurnManager(world, executor=self)
        turn_result = turn_manager.end_turn(game_state)  # Pass game_state for enemy AI

        # Build message — enemy phase text and turn events removed from terminal
        # (enemy phase shown in popup dialog, turn events absorbed into Morning Dispatch)
        message = f"Turn {turn_result['turn_ended']} ended. Turn {turn_result['next_turn']} begins!"

        enemy_phase = turn_result.get("enemy_phase")
        tactical_events = turn_result.get("tactical_events", [])

        # Add Independent Command Report to message (Phase 2.5)
        # NOTE: Action names must be player-readable — never show raw internal names
        # like "stance_change" or "fortify". Use _action_display_name() to translate.
        independent_report = turn_result.get("independent_command_report", [])
        if independent_report:
            message += "\n\n═══ INDEPENDENT COMMAND REPORT ═══"
            for entry in independent_report:
                marshal_name = entry.get("marshal", "Unknown")
                action = entry.get("action", "wait")
                target = entry.get("target")
                turns_left = entry.get("turns_remaining", 0)
                perf = entry.get("performance", {})

                action_str = _action_display_name(action)
                if target:
                    action_str += f" {target}"

                perf_parts = []
                if perf.get("battles_won", 0) > 0:
                    perf_parts.append(f"{perf['battles_won']}W")
                if perf.get("battles_lost", 0) > 0:
                    perf_parts.append(f"{perf['battles_lost']}L")
                if perf.get("regions_captured", 0) > 0:
                    perf_parts.append(f"{perf['regions_captured']} captured")
                perf_str = f" ({', '.join(perf_parts)})" if perf_parts else ""

                if entry.get("autonomy_ended"):
                    end_result = entry.get("end_result", {})
                    message += f"\n{marshal_name}: {action_str}{perf_str} - AUTONOMY ENDED ({end_result.get('tier', 'unknown')})"
                else:
                    message += f"\n{marshal_name}: {action_str}{perf_str} - {turns_left} turn{'s' if turns_left != 1 else ''} remaining"

        # ════════════════════════════════════════════════════════════
        # FINANCIAL SUMMARY (Phase 6.2.G)
        # Show income/upkeep/net after turn processing
        # ════════════════════════════════════════════════════════════
        nation = world.player_nation
        income_data = world.calculate_turn_income(nation)
        upkeep_data = world.calculate_turn_upkeep(nation)
        # Admin bonus was already applied during process_income_phase in advance_turn
        # Use 0 here since AP was already consumed/saved
        treasury = world.nation_gold.get(nation, 0)

        # Add financial report to message
        income_val = income_data["income"]
        upkeep_val = upkeep_data["total"]
        spent_val = saved_gold_spent.get(nation, 0)
        net_val = income_val - upkeep_val
        net_sign = "+" if net_val >= 0 else ""
        spent_str = f" | Spent: {spent_val}g" if spent_val > 0 else ""
        message += f"\n\nIncome: {income_val}g | Upkeep: {upkeep_val}g | Net: {net_sign}{net_val}g{spent_str} | Treasury: {treasury:,}g"

        if world.nation_bankruptcy_turns.get(nation, 0) > 0:
            bk_turns = world.nation_bankruptcy_turns[nation]
            message += f"\nWARNING: Bankrupt for {bk_turns} turn{'s' if bk_turns > 1 else ''}!"

        # Build turn_end event for Godot's _display_turn_change
        bk_turns = int(world.nation_bankruptcy_turns.get(nation, 0))
        turn_end_event = {
            "type": "turn_end",
            "old_turn": int(turn_result.get("turn_ended", world.current_turn - 1)),
            "new_turn": int(turn_result.get("next_turn", world.current_turn)),
            "income": int(income_data.get("income", 0)),
            "upkeep": int(upkeep_val),
            "spent": int(spent_val),
            "net": int(net_val),
            "treasury": int(treasury),
            "bankruptcy_turns": bk_turns,
        }
        events = [turn_end_event] + turn_result.get("events", [])

        # Hoist battle_report from tactical events (e.g. auto-charge) to result level
        # so Godot's _display_berthier_report() can find it at response.battle_report
        tactical_battle_report = None
        tactical_redemption = None
        for te in tactical_events:
            if te.get("battle_report") and not tactical_battle_report:
                # Use first battle report found (auto-charge is typically the only one)
                tactical_battle_report = te["battle_report"]
            if te.get("redemption_event") and not tactical_redemption:
                tactical_redemption = te["redemption_event"]

        # Build result with all data for frontend
        result = {
            "success": True,
            "message": message,
            "events": events,
            "tactical_events": tactical_events,  # Full event objects, not just messages
            "enemy_phase": enemy_phase,
            "new_state": game_state
        }
        if tactical_battle_report:
            result["battle_report"] = tactical_battle_report
        if tactical_redemption:
            result["redemption_event"] = tactical_redemption

        # Add Independent Command Report for autonomous marshals (Phase 2.5)
        if turn_result.get("show_independent_command_report"):
            result["show_independent_command_report"] = True
            result["independent_command_report"] = turn_result.get("independent_command_report", [])

        # Add Strategic Order Reports (Phase 5.2-C)
        strategic_reports = turn_result.get("strategic_reports", [])
        if strategic_reports:
            result["strategic_reports"] = strategic_reports

        # V2a: Include saved mild concerns (captured before advance_turn cleared them)
        if saved_mild_concerns:
            result["mild_concerns"] = saved_mild_concerns

        # Phase 6.2.F: Occupation may complete during turn resolution, triggering capture choice
        if world.pending_capture_choice:
            result["pending_capture_choice"] = True
            result["capture_data"] = world.pending_capture_choice

        # Morning Dispatch — Berthier's turn-start briefing (Phase 6.5)
        # Tactical events absorbed into dispatch's TURN EVENTS section
        from backend.game_logic.dispatch import build_morning_dispatch
        result["morning_dispatch"] = build_morning_dispatch(world, tactical_events)

        # Autosave at start of new turn (non-blocking — don't fail if autosave fails)
        from backend.save_manager import autosave
        autosave_result = autosave(world)
        if not autosave_result["success"]:
            print(f"Autosave warning: {autosave_result['message']}")

        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # V2a OBJECTION SYSTEM HELPERS
    # ═══════════════════════════════════════════════════════════════════════════

    def _generate_mild_concern_message(self, marshal, action: str, order: Dict) -> str:
        """
        Generate flavor text for MILD concerns (turn log display).

        Args:
            marshal: The marshal with the concern
            action: The action being ordered
            order: Full order dict

        Returns:
            Flavor message string
        """
        personality = getattr(marshal, 'personality', 'balanced').lower()

        # Personality-specific mild concern messages
        if personality == 'aggressive':
            if action in ('defend', 'fortify', 'hold', 'wait'):
                return f"{marshal.name} grumbles about defensive orders but complies."
            elif action == 'retreat':
                return f"{marshal.name} bristles at the retreat order but obeys."
            elif action == 'drill':
                return f"{marshal.name} would rather be fighting but begins drill exercises."

        elif personality == 'cautious':
            if action == 'attack':
                return f"{marshal.name} notes the risks but prepares the attack."
            elif action == 'move':
                return f"{marshal.name} expresses caution about the route but proceeds."
            elif action == 'stance_change':
                return f"{marshal.name} hesitates at the aggressive posture but complies."

        # Default mild message
        return f"{marshal.name} hesitates briefly but follows orders."

    def _generate_objection_message(
        self,
        marshal,
        action: str,
        order: Dict,
        concern: 'ConcernLevel',
        tone: str
    ) -> str:
        """
        Generate objection message for MODERATE+ concerns based on tone.

        Args:
            marshal: The marshal objecting
            action: The action being ordered
            order: Full order dict
            concern: ConcernLevel (MODERATE, STRONG, EXTREME)
            tone: Tone string from trust tier ("defiant", "challenging", "firm", "respectful")

        Returns:
            Objection message string
        """
        personality = getattr(marshal, 'personality', 'balanced').lower()

        # Tone modifiers for message prefix
        tone_prefix = {
            "defiant": f"{marshal.name} refuses outright:",
            "challenging": f"{marshal.name} challenges the order:",
            "firm": f"{marshal.name} firmly objects:",
            "respectful": f"{marshal.name} respectfully raises concerns:",
        }
        prefix = tone_prefix.get(tone, f"{marshal.name} objects:")

        # Personality + action specific messages
        if personality == 'aggressive':
            if action in ('defend', 'fortify', 'hold', 'wait'):
                if concern == ConcernLevel.EXTREME:
                    return f"{prefix} 'We outnumber them! Let me attack!'"
                elif concern == ConcernLevel.STRONG:
                    return f"{prefix} 'Sire, we have the advantage. Let me strike!'"
                else:
                    return f"{prefix} 'I would rather attack than sit idle.'"
            elif action == 'retreat':
                return f"{prefix} 'Retreat? We can still fight!'"

        elif personality == 'cautious':
            if action == 'attack':
                if concern == ConcernLevel.EXTREME:
                    return f"{prefix} 'This is suicide! The odds are hopeless!'"
                elif concern == ConcernLevel.STRONG:
                    return f"{prefix} 'Sire, the enemy is too strong. We need reinforcements.'"
                else:
                    return f"{prefix} 'The odds are not in our favor. Perhaps we should reconsider.'"
            elif action == 'move':
                return f"{prefix} 'That route passes through enemy territory. It is dangerous.'"

        # Default objection message
        return f"{prefix} 'I have concerns about this order, Sire.'"

    def _apply_grouchy_ambiguity_buff(self, marshal, ambiguity: int, strategic_score: int, action: str):
        """
        Apply combat buff to literal marshals based on order clarity.
        Phase 5.2: Ambiguity thresholds → combat bonus on attack AND defense.
        Also triggers Precision Execution if conditions met.
        """
        COMBAT_ACTIONS = ["attack", "charge", "defend", "fortify"]

        # Ambiguity-scaled combat buff (attack + defense)
        if ambiguity <= 20:
            bonus = 15
        elif ambiguity <= 40:
            bonus = 10
        elif ambiguity <= 60:
            bonus = 5
        else:
            bonus = 0

        if bonus > 0 and action in COMBAT_ACTIONS:
            marshal.strategic_combat_bonus = bonus
            marshal.strategic_defense_bonus = bonus

        # Precision Execution: ambiguity <= 20 AND strategic_score > 60
        if ambiguity <= 20 and strategic_score > 60:
            marshal.precision_execution_active = True
            marshal.precision_execution_turns = 3

    def _execute_status(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute status command — returns Berthier's Intelligence Report (Session 34A).

        Reads the intel store and produces a fog-filtered status view.
        Free action (0 AP cost).
        """
        from backend.intel_report import generate_intel_report
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state"}

        report = generate_intel_report(world)
        return {
            "success": True,
            "free_action": True,
            "message": report["report_text"],
            "intel_report": report,
        }

    def _execute_help(self, command: Dict, game_state: Dict) -> Dict:
        """
        Display help text with available commands and examples.

        MAINTENANCE NOTE: When adding new actions to parser.py valid_actions,
        update this help text to document them! Keep help in sync with:
        - parser.py: valid_actions list
        - executor.py: _execute_* methods
        - personality.py: PERSONALITY_TRIGGERS (for objection info)
        """
        help_text = """═══════════════════════════════════════
           COMMAND REFERENCE
═══════════════════════════════════════

MILITARY COMMANDS:
  attack     - Engage enemy forces or capture region
               "Ney, attack Wellington" / "attack" (nearest)

  defend     - Take defensive position (+30% bonus)
               "Davout, defend" / "hold" (alias)

  move       - Move to adjacent region
               "Grouchy, move to Belgium"

  retreat    - Fall back toward Paris (FREE action)
               "Ney, retreat" - Aggressive marshals may object!

  recruit    - Raise 10,000 troops (costs 200 gold)
               "recruit" / "Ney, recruit"

  bombardment - Artillery fires on adjacent region (max 2/turn)
               "Drouot, bombard Rhineland" / "Drouot, attack Rhineland"
               Cannot attack after moving. Terrain affects damage.

  garrison   - Leave detachment to defend a region (2 AP)
               "garrison" - Detaches troops in current region
               Max 3 garrisons per nation. Fights to destruction.

TACTICAL COMMANDS:
  fortify    - Dig in for +50% defense (2 turns)
               "Davout, fortify" - Cannot move/attack while fortified

  unfortify  - Abandon fortifications (immediate)
               "Davout, unfortify" - Lose defense bonus

  drill      - Train troops for +1 Shock skill (2 turns)
               "Ney, drill" - Locked on turn 2, cannot receive orders

  scout      - Reconnaissance of nearby regions
               "scout Rhineland" / "Davout, scout" (area scan)

  form square - Infantry forms anti-cavalry square (1 AP)
               "Ney, form square" - Cavalry attacks deal -40% damage.
               WARNING: Artillery deals +50% damage to squares!
               Breaks automatically when given any other order.

  break square - Return to line formation (FREE action)
               "Ney, break square"

STANCE COMMANDS:
  aggressive - +15% attack, -10% defense
               "Ney, aggressive" / "Ney, go aggressive"

  defensive  - -10% attack, +15% defense
               "Davout, defensive" / "Davout, be defensive"

  neutral    - Balanced (default, FREE to return)
               "Ney, neutral" / "Ney, return to neutral"

STRATEGIC COMMANDS (2 AP, multi-turn):
  march      - Move to distant region over multiple turns
               "Ney, march to Bavaria" / "move to Bavaria"
  pursue     - Chase an enemy marshal across the map
               "Ney, pursue Wellington"
  support    - March to reinforce an allied marshal
               "Ney, support Davout" / "Ney, reinforce Davout"
  hold       - Hold position and auto-bombard (artillery)
               "Drouot, hold Rhineland"
  cancel     - Cancel a strategic order (1 AP)
               "cancel Ney" / "halt Ney" / "stop Ney"

ECONOMY COMMANDS (Admin AP):
  build      - Build at a city you control (1 Admin AP)
               "build fortification at Lyon"
               "build market at Paris"
               "build stables at Lyon" (cavalry recruitment)
  repair     - Repair damage or buildings (1 Admin AP, 150 gold)
               "repair Lyon" / "repair market at Lyon"
  recruit    - Raise troops (1 Admin AP, 200-400 gold)
               "recruit" / "recruit for Ney" / "recruit at Paris"
               Infantry: 10k troops. Cavalry: 5k. Artillery: 3k.

FREE ACTIONS (cost 0):
  help       - Display this help text
  end turn   - Skip remaining actions, advance turn
  wait       - Marshal passes turn (no action taken)
  retreat    - Fall back toward friendly territory
  hold       - Alias for defend (or strategic HOLD with region)
  economy    - Show treasury, income, upkeep breakdown
               Also: "treasury" / "finances"

DIPLOMACY (via Talleyrand):
  propose    - Propose treaty to a nation (2 DP)
               "Talleyrand, propose peace with Prussia"
               "Talleyrand, propose alliance with Saxony"
  assess     - Threat assessment (free, no DP cost)
               "Talleyrand, assess Austria"
  improve    - Start relations mission (1 DP/turn)
               "Talleyrand, improve relations with Austria"
  declare war - Declare war on a nation (1 DP)
               "declare war on Prussia"
  break treaty - Break existing treaty (1 DP)
               "break treaty with Austria"
  ultimatum  - Coercive demand (2 DP)
               "ultimatum to Prussia"
  ally with  - Propose alliance (2 DP)
               "ally with Prussia"

  Press D for Diplomatic Ledger.
  Nations: Britain, Prussia, Austria, Saxony.

MARSHAL ABILITIES:

  NEY (Aggressive, Cavalry):
    • +15% attack always, +5% more in aggressive stance
    • Cavalry Charge: Attack enemies 2 regions away
    • Fighting Retreat: Attack during retreat (+10% bonus)
    • Restlessness: Objects after 3+ turns defensive
    • Fortify capped at 10% (impatient)

  DAVOUT (Cautious, Infantry, "Iron Marshal"):
    • +20% defense in defensive stance
    • Free Unfortify: Break camp at no action cost
    • Counter-Punch: Free attack after defending
    • Fortify: +3%/turn (max 20%), +5% instant
    • Scout Range: +1 region

  GROUCHY (Literal):
    • Immovable: +15% defense when holding position
    • Use "hold" command to activate
    • Lost when Grouchy moves

  DROUOT (Precise, Artillery):
    • Cannot attack after moving (must stay put)
    • Bombardment: Fire on adjacent regions (max 2/turn)
    • No advance on victory (holds position)
    • Exempt from exhaustion penalties
    • 2x fort degradation (siege breaker)

DEBUG COMMANDS (for testing):
  /debug counter_punch <marshal> - Enable free attack
  /debug restless <marshal>      - Trigger restlessness
  /debug cavalry <marshal>       - Toggle 2-tile attacks
  /debug hold <marshal>          - Enable Immovable

RETREAT RECOVERY (3 turns):
  After retreating, marshals are demoralized.
  BLOCKED: attack, fortify, drill, scout
  ALLOWED: move, recruit, defend, wait, change stance

═══════════════════════════════════════"""

        return {
            "success": True,
            "message": help_text,
            "events": [{
                "type": "help",
                "command": "help"
            }],
            "new_state": game_state
        }

    def execute(self, parsed_command: Dict, game_state: Dict) -> Dict:
        """Execute a command against the current game state."""
        # Clear transient square-break notification (set by _auto_break_square)
        self._pending_square_break_msg = ""

        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # ============================================================
        # DISOBEDIENCE CHECK: Is there a pending objection?
        # ============================================================

        if world.pending_objection is not None:
            return {
                "success": False,
                "message": "A marshal is awaiting your response! Use /respond_to_objection to continue.",
                "awaiting_response": True,
                "objection": world.pending_objection,
                "choices": ["trust", "insist", "compromise"] if world.pending_objection.get("alternative") else ["trust", "insist"]
            }

        # ============================================================
        # CAPTURE CHOICE CHECK (Phase 6.2.E): Plunder or Secure?
        # ============================================================
        if world.pending_capture_choice is not None:
            return {
                "success": False,
                "message": "You must decide how to handle the captured region first! Choose 'plunder' or 'secure'.",
                "pending_capture_choice": True,
                "capture_data": world.pending_capture_choice
            }

        # ============================================================
        # DIPLOMATIC DIALOGUE CHECK (Phase 8 Session 3)
        # WARNING: This guard blocks ALL commands when dialogue is
        # pending. Dialogue responses (accept/reject/etc.) are routed
        # BEFORE executor.execute() in main.py's command endpoint.
        # If adding new dialogue response types, update the keyword
        # list in main.py (_DIALOGUE_RESPONSE_KEYWORDS). Cheat
        # commands also cannot pass this guard — test via
        # _execute_cheat() directly. See DIPLOMACY_AUDIT.md §1.
        # ============================================================
        command = parsed_command.get("command", {})
        action = command.get("action", "unknown")

        # Cheat commands bypass dialogue guard
        if world.pending_diplomatic_dialogue is not None and action != "cheat":
            dialogue = world.pending_diplomatic_dialogue
            option_labels = [f"[{i+1}] {o['label']}" for i, o in enumerate(dialogue.get("options", []))]
            options_text = "  ".join(option_labels)
            return {
                "success": False,
                "message": f"Talleyrand awaits your response regarding {dialogue.get('target_nation', 'diplomacy')}. {options_text}",
                "awaiting_diplomatic_response": True,
                "diplomatic_dialogue": dialogue,
            }

        # ════════════════════════════════════════════════════════════
        # META-COMMANDS: save/load — no AP cost, bypass all checks
        # Handled before marshal resolution, AP checks, objection checks.
        # ════════════════════════════════════════════════════════════
        if action == "meta_command":
            raw_cmd = (command.get("raw_command") or parsed_command.get("raw_command", "")).strip()
            cmd_lower = raw_cmd.lower()
            if cmd_lower.startswith("save"):
                save_name = raw_cmd[4:].strip() or f"Save - Turn {world.current_turn}"
                from backend.save_manager import save_game
                result = save_game(world, save_name=save_name)
                return {**result, "new_state": game_state}
            elif cmd_lower == "load":
                from backend.save_manager import list_saves
                saves = list_saves()
                save_list = "\n".join(
                    f"  {s['filename']}: {s['metadata'].get('save_name', '?')} (Turn {s['metadata'].get('turn', '?')})"
                    for s in saves
                ) or "  No saves found."
                return {
                    "success": True,
                    "message": f"Available saves:\n{save_list}\n\nUse the load menu to load a save.",
                    "new_state": game_state,
                    "show_load_dialog": True
                }
            # Unknown meta command — fall through to normal processing

        # ════════════════════════════════════════════════════════════
        # STRATEGIC FIELDS PROPAGATION: Copy strategic flags into command dict
        # so they survive objection storage (original_order = command)
        # and can be used for post-objection routing
        # ════════════════════════════════════════════════════════════
        if parsed_command.get("is_strategic"):
            command["is_strategic"] = True
            command["strategic_type"] = parsed_command.get("strategic_type")

        # ════════════════════════════════════════════════════════════
        # STRATEGIC EXECUTION FLAG (Phase 5.2-C)
        # When set, skip action cost + objections (marshal's own decision)
        # ════════════════════════════════════════════════════════════
        is_strategic_execution = command.get("_strategic_execution", False)
        is_sortie = command.get("_sortie", False)
        self._current_sortie = is_sortie  # Expose to _execute_attack

        # ============================================================
        # ACTION ECONOMY: Check if player has actions remaining
        # ============================================================

        # Actions don't apply to status queries or help
        # retreat is FREE (costs 0 actions - strategic withdrawal)
        # debug is FREE (for testing abilities)
        # economy/treasury/finances are FREE information commands (Phase 6.2.G)
        # R72: Vassal commands (invest_vassal, change_autonomy, make_vassal) are free — they cost DP/gold, not military AP
        free_actions = ["status", "help", "end_turn", "unknown", "retreat", "debug", "economy", "treasury", "finances", "break_square", "diplomatic_proposal", "diplomatic_mission", "diplomatic_feasibility", "diplomatic_advisory", "diplomatic_error", "diplomatic_break", "diplomatic_downgrade", "diplomatic_declare_war", "diplomatic_ultimatum", "invest_vassal", "change_autonomy", "make_vassal", "release_vassal"]

        # Check if action costs points
        action_costs_point = action not in free_actions

        # Strategic execution is always free (cost paid upfront when order issued)
        if is_strategic_execution:
            action_costs_point = False

        # Check if this is a player action (enemy AI has separate action budget)
        is_player_action_check = True
        early_marshal_name = command.get("marshal")
        if early_marshal_name:
            early_marshal = world.get_marshal(early_marshal_name)
            if early_marshal and early_marshal.nation != world.player_nation:
                is_player_action_check = False  # Enemy AI - skip player action check

        # Track whether this is an admin action (uses admin AP pool)
        is_admin_action = action in ADMIN_ACTIONS and is_player_action_check

        if action_costs_point and is_player_action_check:
            if is_admin_action:
                # Admin actions use admin AP pool
                if world.admin_actions_remaining < 1:
                    return {
                        "success": False,
                        "message": f"No administrative actions remaining this turn. (Military commands: {int(world.actions_remaining)} remaining)",
                        "actions_remaining": int(world.actions_remaining),
                        "action_summary": world.get_action_summary()
                    }
            else:
                # Military/tactical actions use CP pool
                # Determine how many actions this command needs
                required_actions = world.get_action_cost(action)
                if (not is_strategic_execution and
                        parsed_command.get("is_strategic") and
                        parsed_command.get("strategic_type")):
                    # Strategic commands cost 2 (1 for literal personality)
                    marshal_for_cost = world.get_marshal(command.get("marshal", ""))
                    is_literal = marshal_for_cost and getattr(marshal_for_cost, 'personality', '') == 'literal'
                    required_actions = 1 if is_literal else 2

                if world.actions_remaining < required_actions:
                    return {
                        "success": False,
                        "message": f"Not enough actions! Need {required_actions}, have {world.actions_remaining}.",
                        "actions_remaining": int(world.actions_remaining),
                        "action_summary": world.get_action_summary()
                    }

        # ============================================================
        # OCCUPATION BLOCKING CHECK (Phase 6.2.F)
        # Marshals securing a fortress can only status/help/end_turn/wait/retreat
        # ============================================================
        if early_marshal_name and not is_strategic_execution:
            occ_marshal = world.get_marshal(early_marshal_name) if early_marshal_name else None
            if occ_marshal and getattr(occ_marshal, 'occupation_region', None):
                allowed_during_occupation = {"status", "help", "end_turn", "wait", "retreat", "economy", "treasury", "finances"}
                if action not in allowed_during_occupation:
                    return {
                        "success": False,
                        "message": f"{occ_marshal.name} is securing the fortress at {occ_marshal.occupation_region}. "
                                   f"Only wait, retreat, or end turn allowed during occupation."
                    }

        # ============================================================
        # FORTIFIED CHECK (universal — applies to strategic execution too)
        # A fortified marshal physically cannot move or attack.
        # ============================================================
        if is_strategic_execution and action in ['attack', 'move']:
            strat_marshal_name = command.get("marshal")
            if strat_marshal_name:
                strat_marshal = world.get_marshal(strat_marshal_name)
                if strat_marshal and getattr(strat_marshal, 'fortified', False):
                    return {
                        "success": False,
                        "message": f"{strat_marshal_name} is fortified at {strat_marshal.location} and cannot {action}. "
                                  f"Order 'unfortify' first to make the army mobile.",
                        "fortified": True,
                        "suggestion": f"Try: '{strat_marshal_name}, unfortify' to abandon fortified position"
                    }

        # ============================================================
        # DISOBEDIENCE SYSTEM: Check for marshal objection
        # ============================================================

        # Track mild objections to prepend to result message
        mild_message = None

        # Only check objection for orders that involve a marshal
        marshal_name = command.get("marshal")
        command_type = command.get("type", "specific")

        # Determine if this order should trigger objection check
        # Note: fortify added for aggressive marshals who object to defensive preparation
        # Note: stance_change added for personality conflicts with stance orders
        # Note: retreat added for aggressive marshals who object to fleeing
        # Note: drill, wait, hold added - aggressive marshals object to these (especially with enemy nearby)
        objection_actions = ["attack", "defend", "move", "scout", "recruit", "fortify", "stance_change", "retreat", "drill", "wait", "hold", "form_square"]

        # Phase M: Strategic commands use strategic objection, not tactical
        is_strategic_command = parsed_command.get("is_strategic", False)

        should_check_objection = (
            action in objection_actions and
            marshal_name is not None and
            not is_strategic_execution and  # Phase 5.2-C: marshal can't object to own decision
            not is_strategic_command  # Phase M: strategic objection handled separately
        )

        if should_check_objection:
            marshal = world.get_marshal(marshal_name)
            if marshal and marshal.nation == world.player_nation:
                # ═══════════════════════════════════════════════════════════
                # AUTONOMOUS CHECK: Cannot command autonomous marshals (Phase 2.5)
                # Autonomous marshals use Enemy AI decision tree at turn start.
                # Player cannot issue orders until autonomy period ends.
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'autonomous', False) and not is_strategic_execution:
                    reason = getattr(marshal, 'autonomy_reason', 'granted autonomy')
                    turns = marshal.autonomy_turns

                    # Build performance summary
                    wins = getattr(marshal, 'autonomous_battles_won', 0)
                    losses = getattr(marshal, 'autonomous_battles_lost', 0)
                    captures = getattr(marshal, 'autonomous_regions_captured', 0)

                    perf_parts = []
                    if wins > 0:
                        perf_parts.append(f"{wins} battle{'s' if wins != 1 else ''} won")
                    if losses > 0:
                        perf_parts.append(f"{losses} battle{'s' if losses != 1 else ''} lost")
                    if captures > 0:
                        perf_parts.append(f"{captures} region{'s' if captures != 1 else ''} captured")

                    if perf_parts:
                        perf_str = f" ({', '.join(perf_parts)})"
                    else:
                        perf_str = ""

                    return {
                        "success": False,
                        "message": f"{marshal_name} is acting independently{perf_str}. {turns} turn{'s' if turns != 1 else ''} remaining.",
                        "autonomous": True,
                        "autonomy_turns": turns,
                        "autonomy_reason": reason,
                        "performance": {
                            "battles_won": wins,
                            "battles_lost": losses,
                            "regions_captured": captures
                        }
                    }

                # ═══════════════════════════════════════════════════════════
                # STRATEGIC OVERRIDE CHECK (Phase 5.2-C)
                # Override commands silently cancel active strategic orders
                # Non-override commands execute alongside strategic orders
                # ═══════════════════════════════════════════════════════════
                if marshal.in_strategic_mode and not is_strategic_execution:
                    strategic_override_actions = [
                        "attack", "move", "defend", "fortify", "drill", "retreat"
                    ]
                    if action in strategic_override_actions:
                        old_order = marshal.strategic_order
                        marshal.strategic_order = None
                        # Clear holding_position if HOLD was active
                        if old_order and old_order.command_type == "HOLD":
                            marshal.holding_position = False
                            marshal.hold_region = ""
                        print(f"[STRATEGIC] {marshal.name}'s strategic order "
                              f"cancelled by player {action} command")

                # ═══════════════════════════════════════════════════════════
                # DRILLING CHECK: Cannot order while drilling/drill-locked
                # Also blocks stance_change during any drilling state
                # (Skipped for strategic execution — executor handles state)
                # ═══════════════════════════════════════════════════════════
                is_drilling = getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)
                if is_drilling and not is_strategic_execution:
                    # Drilling-locked blocks ALL orders
                    if getattr(marshal, 'drilling_locked', False):
                        return {
                            "success": False,
                            "message": f"{marshal_name} is locked in drill exercises and cannot receive orders. "
                                      f"Training completes turn {marshal.drill_complete_turn}.",
                            "drilling_locked": True,
                            "complete_turn": int(marshal.drill_complete_turn)
                        }
                    # Regular drilling blocks stance_change
                    if action == 'stance_change':
                        return {
                            "success": False,
                            "message": f"{marshal_name} is engaged in drill exercises and cannot change stance.",
                            "drilling": True,
                            "suggestion": "Wait for drill to complete, or cancel with different orders."
                        }

                # ═══════════════════════════════════════════════════════════
                # FORTIFIED CHECK: Cannot move or attack while fortified
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'fortified', False) and action in ['attack', 'move']:
                    return {
                        "success": False,
                        "message": f"{marshal_name} is fortified at {marshal.location} and cannot {action}. "
                                  f"Order 'unfortify' first to make the army mobile.",
                        "fortified": True,
                        "suggestion": f"Try: '{marshal_name}, unfortify' to abandon fortified position"
                    }

                # ═══════════════════════════════════════════════════════════
                # DEFEND NO-OP: Already defensive + fortified = no action needed
                # Pre-validated here to avoid showing an objection then telling
                # the player the action is pointless.
                # ═══════════════════════════════════════════════════════════
                if action == 'defend' and getattr(marshal, 'stance', None) == Stance.DEFENSIVE and getattr(marshal, 'fortified', False):
                    return {
                        "success": False,
                        "message": f"{marshal_name} is already defending and fortified at {marshal.location}. No further defensive action needed.",
                    }

                # ═══════════════════════════════════════════════════════════
                # RETREAT STATE: Simplified - No personality objections during recovery
                # Certain actions blocked, others allowed without objection dialog
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'retreating', False) and not is_strategic_execution:
                    recovery_turns = getattr(marshal, 'retreat_recovery_turns', 3)

                    # Actions allowed during retreat (no objections, just execute)
                    allowed_during_retreat = ['move', 'wait', 'recruit', 'retreat']

                    # Stance changes: defensive/neutral allowed, aggressive blocked
                    if action == 'stance_change':
                        target_stance = (command.get('target_stance') or command.get('target') or '').lower()
                        if target_stance in ['aggressive', 'attack', 'offense']:
                            return {
                                "success": False,
                                "message": f"{marshal_name} is recovering from retreat and cannot adopt aggressive stance. "
                                          f"Recovery: {recovery_turns} turn(s) remaining.",
                                "retreating": True,
                                "recovery_turns": recovery_turns
                            }
                        # Defensive/neutral stance allowed - skip objection check
                        should_check_objection = False

                    # Block attack, fortify, drill, scout during retreat
                    elif action in ['attack', 'fortify', 'drill', 'scout']:
                        action_display = action.replace('_', ' ')
                        return {
                            "success": False,
                            "message": f"{marshal_name} is recovering from retreat and cannot {action_display}. "
                                      f"Recovery: {recovery_turns} turn(s) remaining.",
                            "retreating": True,
                            "recovery_turns": recovery_turns
                        }

                    # Defend action during retreat - convert to defensive posture, no objection
                    elif action == 'defend':
                        # Allow defend but skip objection - marshal is already in survival mode
                        should_check_objection = False

                    # All other allowed actions - skip objection check entirely
                    elif action in allowed_during_retreat:
                        should_check_objection = False

                # ═══════════════════════════════════════════════════════════
                # BROKEN STATE: Army shattered from surrounded forced retreat
                # Can ONLY recruit - all other actions blocked for 4 turns
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'broken', False):
                    recovery_stage = getattr(marshal, 'broken_recovery', 0)
                    turns_remaining = 4 - recovery_stage  # 4 turns total recovery

                    # ONLY recruit is allowed when broken
                    if action != 'recruit':
                        return {
                            "success": False,
                            "message": f"💀 {marshal_name}'s army is BROKEN and scattered! "
                                      f"Only recruitment is possible while rebuilding. "
                                      f"Recovery: {turns_remaining} turn(s) remaining.",
                            "broken": True,
                            "broken_recovery": recovery_stage,
                            "turns_remaining": turns_remaining
                        }
                    else:
                        # Recruit is allowed - skip objection check
                        should_check_objection = False

                # ═══════════════════════════════════════════════════════════
                # ALREADY-DEFENDED CHECK - Validation BEFORE objection
                # Don't fire objection for defend when already fortified
                # ═══════════════════════════════════════════════════════════
                current_stance = getattr(marshal, 'stance', None)
                if action == 'defend' and current_stance == Stance.DEFENSIVE:
                    if getattr(marshal, 'fortified', False):
                        current_bonus = int(getattr(marshal, 'defense_bonus', 0) * 100)
                        return {
                            "success": False,
                            "message": f"{marshal.name} is already defending and fortified at {marshal.location} (+{current_bonus}% defense). "
                                      f"No further defensive action needed.",
                        }

                # ═══════════════════════════════════════════════════════════
                # ALREADY-IN-STANCE CHECK - Validation BEFORE objection
                # No point objecting to a stance change that's a no-op.
                # ═══════════════════════════════════════════════════════════
                if action == 'stance_change' and current_stance:
                    target_stance_raw = (command.get('target_stance') or command.get('target') or '').lower()
                    stance_map = {
                        "neutral": Stance.NEUTRAL, "defensive": Stance.DEFENSIVE,
                        "defense": Stance.DEFENSIVE, "defend": Stance.DEFENSIVE,
                        "aggressive": Stance.AGGRESSIVE, "attack": Stance.AGGRESSIVE,
                        "offense": Stance.AGGRESSIVE,
                    }
                    target = stance_map.get(target_stance_raw)
                    if target and current_stance == target:
                        return {
                            "success": False,
                            "message": f"{marshal.name} is already in {current_stance.value.upper()} stance."
                        }

                # ═══════════════════════════════════════════════════════════
                # AGGRESSIVE STANCE CHECK - Validation BEFORE objection
                # Cannot fortify or drill while in aggressive stance
                # ═══════════════════════════════════════════════════════════
                if current_stance and current_stance.value == "aggressive":
                    blocked_while_aggressive = ['fortify', 'drill']
                    if action in blocked_while_aggressive:
                        return {
                            "success": False,
                            "message": f"{marshal_name} cannot {action} while in AGGRESSIVE stance. "
                                      f"The troops are ready to attack, not dig trenches!",
                            "stance": "aggressive",
                            "suggestion": f"Change stance first: '{marshal_name} defensive' or '{marshal_name} neutral'"
                        }

                # ═══════════════════════════════════════════════════════════
                # ALREADY-FORTIFIED CHECK - Validation BEFORE objection
                # Objection evaluation must run AFTER action validation —
                # no point objecting to an action that would fail anyway.
                # ═══════════════════════════════════════════════════════════
                if action == 'fortify' and getattr(marshal, 'fortified', False):
                    current_bonus = int(getattr(marshal, 'defense_bonus', 0) * 100)
                    return {
                        "success": False,
                        "message": f"{marshal.name} is already fortified at {marshal.location} (+{current_bonus}% defense)."
                    }

                # ═══════════════════════════════════════════════════════════
                # ALREADY-DRILLING CHECK - Validation BEFORE objection
                # Same principle: don't object to a redundant drill order.
                # ═══════════════════════════════════════════════════════════
                if action == 'drill' and (getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)):
                    return {
                        "success": False,
                        "message": f"{marshal.name} is already engaged in drill exercises."
                    }

                # ═══════════════════════════════════════════════════════════
                # RETREAT DANGER CHECK - Validation BEFORE objection (BUG-010)
                # Cannot retreat if not actually in danger
                # ═══════════════════════════════════════════════════════════
                if action == 'retreat':
                    if not world.is_in_danger(marshal_name):
                        return {
                            "success": False,
                            "message": f"{marshal_name} is not in danger. No retreat necessary.",
                            "suggestion": "Use 'move' to reposition instead."
                        }

                # ═══════════════════════════════════════════════════════════
                # FORM_SQUARE PRE-VALIDATION — BEFORE objection
                # Aggressive infantry only — cavalry (Ney) blocked by pre-validation. Future 1805 marshals.
                # ═══════════════════════════════════════════════════════════
                if action == 'form_square':
                    if getattr(marshal, 'square_formation', False):
                        return {
                            "success": False,
                            "message": f"{marshal.name} is already in square formation."
                        }
                    if getattr(marshal, 'cavalry', False):
                        return {
                            "success": False,
                            "message": f"{marshal.name}'s cavalry cannot form an infantry square!"
                        }
                    if getattr(marshal, 'artillery', False):
                        return {
                            "success": False,
                            "message": f"{marshal.name}'s artillery cannot form an infantry square!"
                        }

                # ═══════════════════════════════════════════════════════════
                # RECKLESSNESS STANCE CHECK — Validation BEFORE objection
                # High recklessness blocks defensive/neutral stance changes.
                # Must run before objection so mood variance can't escalate
                # a MILD objection to MODERATE and bypass the real block.
                # ═══════════════════════════════════════════════════════════
                if action == 'stance_change' and getattr(marshal, 'is_reckless_cavalry', False):
                    target_stance_raw_reck = (command.get('target_stance') or command.get('target') or '').lower()
                    can_use, block_reason = marshal.can_use_stance(target_stance_raw_reck)
                    if not can_use:
                        return {
                            "success": False,
                            "message": block_reason,
                            "recklessness": getattr(marshal, 'recklessness', 0)
                        }

                # ═══════════════════════════════════════════════════════════
                # AP PRE-CHECK — Validation BEFORE objection
                # If the player doesn't have enough AP, fail immediately.
                # Without this, an objection fires and then "proceed" fails
                # with an AP error, which is confusing.
                # ═══════════════════════════════════════════════════════════
                if action_costs_point and is_player_action_check:
                    required_ap = 1  # Default cost
                    if action == 'stance_change':
                        target_stance_raw_ap = (command.get('target_stance') or command.get('target') or '').lower()
                        stance_map_ap = {
                            "neutral": Stance.NEUTRAL, "defensive": Stance.DEFENSIVE,
                            "defense": Stance.DEFENSIVE, "defend": Stance.DEFENSIVE,
                            "aggressive": Stance.AGGRESSIVE, "attack": Stance.AGGRESSIVE,
                            "offense": Stance.AGGRESSIVE,
                        }
                        target_stance_ap = stance_map_ap.get(target_stance_raw_ap)
                        if target_stance_ap:
                            required_ap = self._get_stance_change_cost(current_stance, target_stance_ap)
                    if required_ap > 0 and world.actions_remaining < required_ap:
                        cost_str = f" ({required_ap} action{'s' if required_ap > 1 else ''})" if required_ap > 1 else ""
                        return {
                            "success": False,
                            "message": f"Not enough actions remaining{cost_str}. "
                                      f"{world.actions_remaining} action{'s' if world.actions_remaining != 1 else ''} left.",
                            "actions_remaining": int(world.actions_remaining),
                            "action_summary": world.get_action_summary()
                        }

                # ═══════════════════════════════════════════════════════════
                # SKIP OBJECTION if flag was cleared (e.g., by retreat state)
                # ═══════════════════════════════════════════════════════════
                if should_check_objection:
                    # ═══════════════════════════════════════════════════════════
                    # V2a OBJECTION SYSTEM
                    # Deterministic ConcernLevel evaluation with mood variance
                    # ═══════════════════════════════════════════════════════════

                    # Evaluate concern level using V2 system
                    # NOTE: game_state (method param) already has {"world": world, ...}
                    # V2 evaluators extract world via _get_world(game_state)
                    base_concern = evaluate_situation(marshal, action, command, game_state)

                    # V2b Step 14b: Vindication escalation/de-escalation (+1 or -1 max)
                    # Ordering: base trigger → vindication shift → mood variance
                    # NONE never escalates (no fake objections about orders marshal is fine with)
                    # MILD never drops below MILD (even discredited marshal still grumbles)
                    vindication_shifted = base_concern
                    v_score = getattr(marshal, 'vindication_score', 0)
                    if v_score > 0 and base_concern != ConcernLevel.NONE:
                        # Positive vindication → escalate +1 (marshal proven right, bolder)
                        new_val = min(base_concern.value + 1, ConcernLevel.EXTREME.value)
                        vindication_shifted = ConcernLevel(new_val)
                    elif v_score < 0 and base_concern != ConcernLevel.NONE:
                        # Negative vindication → de-escalate -1 ("boy who cried wolf")
                        new_val = max(base_concern.value - 1, ConcernLevel.MILD.value)
                        vindication_shifted = ConcernLevel(new_val)

                    concern = apply_mood_variance(vindication_shifted)

                    # V2b: Update last_objection_turn for any concern (including MILD)
                    if base_concern != ConcernLevel.NONE:
                        marshal.last_objection_turn = world.current_turn

                    # Get trust tier for consequence scaling
                    trust_tier = get_trust_tier(marshal.trust.value)

                    if concern == ConcernLevel.NONE:
                        # No objection - proceed with execution
                        pass

                    elif concern == ConcernLevel.MILD:
                        # MILD: Flavor text in turn log, order executes
                        # Max 1 MILD per marshal per turn
                        if marshal.name not in [c.get("marshal") for c in world.mild_concerns_this_turn]:
                            # Generate mild flavor message
                            mild_message = self._generate_mild_concern_message(marshal, action, command)
                            world.mild_concerns_this_turn.append({
                                "marshal": marshal.name,
                                "message": mild_message,
                                "concern_level": "MILD",
                                "action": action,
                            })
                        # Continue with execution

                    else:
                        # MODERATE, STRONG, EXTREME: Popup with choices
                        # Per-marshal cap: max 1 popup per marshal per turn
                        if marshal.name in world.objection_popups_this_turn:
                            # Already had popup this turn - downgrade to MILD
                            if marshal.name not in [c.get("marshal") for c in world.mild_concerns_this_turn]:
                                mild_message = self._generate_mild_concern_message(marshal, action, command)
                                world.mild_concerns_this_turn.append({
                                    "marshal": marshal.name,
                                    "message": mild_message,
                                    "concern_level": "MILD",
                                    "action": action,
                                    "downgraded_from": concern.name,
                                })
                        else:
                            # Show popup - mark marshal as having had popup this turn
                            world.objection_popups_this_turn.add(marshal.name)

                            # V2a: Generate alternatives directly (no V1 severity calc)
                            suggested_alt = world.disobedience_system._generate_alternative(
                                marshal, command, world
                            )
                            compromise_action = world.disobedience_system._find_compromise(
                                marshal, command, suggested_alt, world
                            )

                            # ═══════════════════════════════════════════════════
                            # MASTER RULE #2: Exhaust → MILD demotion
                            # If alternatives are empty/identical/same-as-original,
                            # demote to MILD. Never show popup with fake choices.
                            # ═══════════════════════════════════════════════════
                            def _actions_match(a, b):
                                """Check if two action dicts describe the same action."""
                                if a is None or b is None:
                                    return a is None and b is None
                                a_act = a.get('action', '').lower()
                                b_act = b.get('action', '').lower()
                                if a_act != b_act:
                                    return False
                                a_tgt = (a.get('target_stance') or a.get('target', '')).lower()
                                b_tgt = (b.get('target_stance') or b.get('target', '')).lower()
                                return a_tgt == b_tgt

                            should_demote = False

                            # No preferred alternative at all
                            if suggested_alt is None:
                                should_demote = True

                            # Preferred == original (Trust button does what Insist does)
                            elif _actions_match(suggested_alt, command):
                                should_demote = True

                            # Preferred == compromise (two identical buttons)
                            elif _actions_match(suggested_alt, compromise_action):
                                should_demote = True

                            if should_demote:
                                # Fallback exhausted — demote to MILD
                                # Never show popup with identical options.
                                world.objection_popups_this_turn.discard(marshal.name)
                                if marshal.name not in [c.get("marshal") for c in world.mild_concerns_this_turn]:
                                    mild_message = self._generate_mild_concern_message(marshal, action, command)
                                    world.mild_concerns_this_turn.append({
                                        "marshal": marshal.name,
                                        "message": mild_message,
                                        "concern_level": "MILD",
                                        "action": action,
                                        "demoted_from": concern.name,
                                    })
                                # Continue with execution (no popup)
                            else:
                                # Alternatives are valid and distinct — show popup
                                tone = get_objection_tone(trust_tier)
                                insist_penalty = get_insist_penalty(trust_tier)
                                legacy_severity = concern_to_legacy_severity(concern)

                                # Generate message based on tone
                                message = self._generate_objection_message(marshal, action, command, concern, tone)

                                # V2 scaled trust values
                                trust_gain = calculate_trust_gain(concern, trust_tier)

                                objection = {
                                    # V2 fields
                                    "type": "major_objection",
                                    "concern_level": concern.name,
                                    "trust_tier": trust_tier.name,
                                    "tone": tone,
                                    "insist_penalty": insist_penalty,
                                    "trust_gain": trust_gain,
                                    "compromise_gain": COMPROMISE_TRUST_GAIN,
                                    # Backward compat fields
                                    "severity": legacy_severity,
                                    "message": message,
                                    "marshal": marshal.name,
                                    "personality": marshal.personality,
                                    "original_order": command,
                                    # Alternatives generated by personality-specific logic
                                    "suggested_alternative": suggested_alt,
                                    "compromise": compromise_action,
                                }

                                # Store pending objection
                                world.pending_objection = objection

                                return {
                                    "success": True,
                                    "awaiting_response": True,
                                    "pending_objection": True,  # CRITICAL for AP skip logic
                                    "state": "awaiting_player_choice",
                                    "message": message,
                                    "objection": objection,
                                    "choices": ["trust", "insist", "compromise"] if objection.get("suggested_alternative") else ["trust", "insist"],
                                    "marshal": marshal_name,
                                    "personality": marshal.personality,
                                    "concern_level": concern.name,
                                    "tone": tone,
                                    "severity": legacy_severity,
                                    "trust": int(marshal.trust.value),
                                    "trust_label": marshal.trust.get_label(),
                                    "vindication": world.vindication_tracker.get_vindication_data(marshal_name).get("score", 0),
                                    "authority": int(world.authority_tracker.authority),
                                    "suggested_alternative": objection.get("suggested_alternative"),
                                    "compromise": objection.get("compromise")
                                }

        # ============================================================
        # STRATEGIC BONUSES: Apply morale/trust/combat bonuses (Phase 5)
        # Only for player actions, only in non-mock mode
        # ============================================================

        # Define combat actions that get strategic_combat_bonus
        COMBAT_ACTIONS = ["attack", "charge"]

        # Check if we should apply bonuses
        mode = parsed_command.get("mode", "mock")
        strategic_score = parsed_command.get("strategic_score", 0)

        # Only apply for non-mock, player actions with a marshal
        if mode != "mock" and is_player_action_check and marshal_name:
            marshal = world.get_marshal(marshal_name)
            if marshal and marshal.nation == world.player_nation:
                from backend.ai.feedback import apply_strategic_bonuses
                is_combat_action = action in COMBAT_ACTIONS
                apply_strategic_bonuses(marshal, strategic_score, is_combat_action)

        # ============================================================
        # GROUCHY AMBIGUITY COMBAT BUFF (Phase 5.2)
        # Literal marshals get combat bonuses from clear orders
        # ============================================================
        ambiguity = parsed_command.get("ambiguity", 50)
        if is_player_action_check and marshal_name:
            marshal_obj = world.get_marshal(marshal_name)
            if marshal_obj and getattr(marshal_obj, 'personality', '') == 'literal':
                self._apply_grouchy_ambiguity_buff(marshal_obj, ambiguity, strategic_score, action)

        # ════════════════════════════════════════════════════════════
        # CLARIFICATION GATE (Phase 5.2-C — Grouchy)
        # Literal personality + high ambiguity + strategic = clarification popup
        # "You wish me to pursue Blucher (nearest enemy), Sire?"
        # ════════════════════════════════════════════════════════════
        if not is_strategic_execution and marshal_name:
            cl_marshal = world.get_marshal(marshal_name)
            if cl_marshal and getattr(cl_marshal, 'personality', '') == 'literal':
                cl_ambiguity = parsed_command.get("ambiguity", 5)
                cl_is_strategic = parsed_command.get("is_strategic", False)
                if cl_ambiguity > 60 and cl_is_strategic:
                    interpreted = parsed_command.get("interpreted_target")
                    reason = parsed_command.get("interpretation_reason", "unclear")
                    alternatives = parsed_command.get("alternatives", [])
                    strategic_type = parsed_command.get("strategic_type", "unknown")

                    options = []
                    if interpreted:
                        options.append({
                            "label": f"Yes, {interpreted}",
                            "value": "confirm",
                            "target": interpreted
                        })
                    for alt in alternatives[:2]:
                        options.append({
                            "label": f"No, {alt}",
                            "value": "specify",
                            "target": alt
                        })
                    if interpreted:
                        options.append({"label": "Proceed as ordered", "value": "confirm", "target": interpreted})
                    # Note: popup adds its own "Cancel Order" button — don't duplicate

                    if strategic_type == "PURSUE":
                        cl_msg = f"You wish me to pursue {interpreted}, Sire?"
                    elif strategic_type == "SUPPORT":
                        cl_msg = f"You wish me to support {interpreted}, Sire?"
                    elif strategic_type == "MOVE_TO":
                        cl_msg = f"You wish me to march to {interpreted}, Sire?"
                    elif strategic_type == "HOLD":
                        cl_msg = f"You wish me to hold {interpreted}, Sire?"
                    else:
                        cl_msg = f"I understand {interpreted}, Sire. Is this correct?"

                    return {
                        "success": True,
                        "free_action": True,
                        "state": "awaiting_clarification",
                        "type": "clarification",
                        "strategic_type": strategic_type,
                        "marshal": cl_marshal.name,
                        "original_command": command.get("raw_command", ""),
                        "message": cl_msg,
                        "interpreted_target": interpreted,
                        "interpretation_reason": reason,
                        "alternatives": alternatives,
                        "options": options,
                        "action_summary": world.get_action_summary(),
                        "game_state": world.get_filtered_game_state_summary()
                    }

        # ════════════════════════════════════════════════════════════
        # STRATEGIC COMMAND INTERCEPTION (Phase 5.2)
        # If parser detected a strategic command, create StrategicOrder
        # on the marshal and execute first step immediately.
        # ════════════════════════════════════════════════════════════
        if (not is_strategic_execution and
                parsed_command.get("is_strategic") and
                parsed_command.get("strategic_type")):
            strategic_result = self._execute_strategic_command(parsed_command, command, game_state)
            if strategic_result is not None:
                # Strategic command handled — set result and flow to action economy
                result = strategic_result
                # Jump past normal routing to action economy
                # (Python doesn't have goto, so we use a flag)
                _skip_routing = True
            else:
                _skip_routing = False
        else:
            _skip_routing = False

        # ============================================================
        # Continue with normal command routing
        # ============================================================

        if _skip_routing:
            pass  # Already have result from strategic handler
        # Handle special actions first
        elif action == "status":
            result = self._execute_status(command, game_state)
        elif action == "help":
            result = self._execute_help(command, game_state)
        elif action == "recruit":
            result = self._execute_recruit(command, game_state)
        elif action == "build":
            result = self._execute_build(command, game_state)
        elif action == "repair":
            result = self._execute_repair(command, game_state)
        elif action in ("economy", "treasury", "finances"):
            result = self._execute_economy(command, game_state)
        elif action == "garrison":
            result = self._execute_garrison(command, game_state)
        elif action == "end_turn":
            result = self._execute_end_turn(command, game_state)
        # ════════════════════════════════════════════════════════════
        # TACTICAL STATE ACTIONS (Phase 2.6)
        # ════════════════════════════════════════════════════════════
        elif action == "drill":
            result = self._execute_drill(command, game_state)
        elif action == "fortify":
            result = self._execute_fortify(command, game_state)
        elif action == "unfortify":
            result = self._execute_unfortify(command, game_state)
        elif action == "form_square":
            result = self._execute_form_square(command, game_state)
        elif action == "break_square":
            result = self._execute_break_square(command, game_state)
        # ════════════════════════════════════════════════════════════
        # STANCE SYSTEM (Phase 2.7)
        # ════════════════════════════════════════════════════════════
        elif action == "stance_change":
            result = self._execute_stance_change(command, game_state)
        # ════════════════════════════════════════════════════════════
        # CHEAT COMMANDS (Phase 8 Session 8A)
        # ════════════════════════════════════════════════════════════
        elif action == "cheat":
            result = self._execute_cheat(command, game_state)
        # ════════════════════════════════════════════════════════════
        # DEBUG COMMANDS (Phase 2.8) - Must be before command_type routing
        # ════════════════════════════════════════════════════════════
        elif action == "debug":
            result = self._execute_debug(command, game_state)
        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS SYSTEM (Phase 3)
        # ════════════════════════════════════════════════════════════
        elif action == "charge":
            result = self._execute_charge(command, game_state)
        elif action == "restrain":
            result = self._execute_restrain(command, game_state)
        elif action == "cancel":
            result = self._execute_cancel(command, game_state)
        # ════════════════════════════════════════════════════════════
        # DIPLOMATIC COMMANDS (Phase 8 Session 3)
        # ════════════════════════════════════════════════════════════
        elif action in ("diplomatic_proposal", "diplomatic_mission",
                        "diplomatic_feasibility", "diplomatic_advisory",
                        "diplomatic_error", "diplomatic_break",
                        "diplomatic_downgrade", "diplomatic_declare_war",
                        "diplomatic_ultimatum"):
            result = self._execute_diplomatic(command, game_state)
        # ════════════════════════════════════════════════════════════
        # VASSAL COMMANDS (Phase 8 Session 5)
        # ════════════════════════════════════════════════════════════
        elif action == "invest_vassal":
            result = self._execute_invest_vassal(command, game_state)
        elif action == "change_autonomy":
            result = self._execute_change_autonomy(command, game_state)
        elif action == "make_vassal":
            result = self._execute_make_vassal(command, game_state)
        elif action == "release_vassal":
            result = self._execute_release_vassal(command, game_state)
        # Route to appropriate handler
        elif command_type == "specific":
            result = self._execute_specific(command, game_state)
        elif command_type == "general_attack":
            result = self._execute_general_attack(command, game_state)
        elif command_type == "auto_assign_attack":
            result = self._execute_auto_assign_attack(command, game_state)
        elif command_type == "auto_assign_bombardment":
            result = self._execute_auto_assign_bombardment(command, game_state)
        elif command_type == "auto_assign_scout":
            result = self._execute_auto_assign_scout(command, game_state)
        elif command_type == "general_retreat":
            result = self._execute_general_retreat(command, game_state)
        elif command_type == "general_defensive":
            result = self._execute_general_defensive(command, game_state)
        else:
            result = {
                "success": False,
                "message": f"Unknown command type: {command_type}"
            }

        # ============================================================
        # ACTION ECONOMY: Consume action ONLY if command succeeded
        # ============================================================

        # Only consume action if:
        # 1. Command succeeded
        # 2. Action costs a point (not free)
        # 3. Marshal belongs to player nation (enemy AI has separate action budget)
        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}

        # Determine if this is a player action (should consume from player's action budget)
        is_player_action = True  # Default to player action
        marshal_name = command.get("marshal")
        if marshal_name:
            executing_marshal = world.get_marshal(marshal_name)
            if executing_marshal and executing_marshal.nation != world.player_nation:
                is_player_action = False  # Enemy AI action - don't consume player actions

        # Check if this action is free (counter-punch, etc.)
        is_free_action = result.get("free_action", False) or result.get("no_action_cost", False)

        # CRITICAL: Don't consume AP for pending_objection (Phase M) - AP consumed
        # when player responds, not when objection triggers
        if result.get("success", False) and action_costs_point and is_player_action and not is_free_action and not result.get("pending_objection"):
            if is_admin_action:
                # Admin actions consume from admin AP pool, not CP
                world.use_admin_action()
                # Auto-end turn when BOTH pools are exhausted
                both_exhausted = (world.actions_remaining <= 0 and world.admin_actions_remaining <= 0)
                action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 1, "should_end_turn": both_exhausted}
            else:
                # Check for variable action cost (stance_change returns this)
                variable_cost = result.get("variable_action_cost")
                if variable_cost is not None:
                    # Variable costs (stance: 0-2, strategic upgrades: 1-2)
                    if variable_cost > 0:
                        if world.actions_remaining < variable_cost:
                            # Safety net — should be caught by pre-checks above
                            return {
                                "success": False,
                                "message": f"Not enough actions! Need {variable_cost}, have {world.actions_remaining}.",
                                "actions_remaining": int(world.actions_remaining),
                                "action_summary": world.get_action_summary()
                            }
                        for _ in range(variable_cost):
                            action_result = world.use_action(action)
                    else:
                        # Free transition (returning to neutral)
                        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
                else:
                    # NOW consume the action (after validation passed)
                    action_result = world.use_action(action)
        elif is_free_action:
            # Free action (counter-punch) - don't consume action point
            action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0, "should_end_turn": False}
            print("  [FREE ACTION] Counter-punch or similar - no action consumed")

        # Add action info to result
        result["action_info"] = {
            "cost": action_result.get("action_cost", 0),
            "remaining": world.actions_remaining,
            "turn_advanced": action_result.get("turn_advanced", False),
            "new_turn": action_result.get("new_turn")
        }

        # EXPLICIT: For pending_objection (Phase M), ensure cost shows 0
        # AP is consumed when player responds, not when objection triggers
        if result.get("pending_objection"):
            result["action_info"]["cost"] = 0

        result["action_summary"] = world.get_action_summary()

        # FIX: Prepend mild objection message if there was one
        if mild_message and result.get("success"):
            result["message"] = mild_message + result.get("message", "")
            result["mild_objection"] = True

        # Prepend square-break notification if auto-break fired (Session 67 fix)
        if self._pending_square_break_msg and result.get("success") and result.get("message"):
            result["message"] = self._pending_square_break_msg + "\n" + result["message"]
            self._pending_square_break_msg = ""  # Consume

        # ════════════════════════════════════════════════════════════
        # AUTO-END TURN: When actions exhausted, call end_turn properly
        # This ensures enemy AI processes its turn (was being skipped before!)
        # Must mirror _execute_end_turn() data capture — see P0-1/2/3 audit.
        # ════════════════════════════════════════════════════════════
        if action_result.get("should_end_turn", False) and is_player_action:
            from backend.game_logic.turn_manager import TurnManager

            # Capture data BEFORE advance_turn() clears it (same as _execute_end_turn)
            saved_mild_concerns = [c.copy() for c in world.mild_concerns_this_turn]
            saved_gold_spent = world.gold_spent_this_turn.copy()

            turn_manager = TurnManager(world, executor=self)
            turn_result = turn_manager.end_turn(game_state)

            # Update result with turn end info
            result["action_info"]["turn_advanced"] = True
            result["action_info"]["new_turn"] = turn_result.get("next_turn")

            # Add enemy phase results to the response (popup dialog, no terminal text)
            if turn_result.get("enemy_phase"):
                result["enemy_phase"] = turn_result["enemy_phase"]

            # Tactical events — absorbed into Morning Dispatch's TURN EVENTS section
            tactical_events = turn_result.get("tactical_events", [])
            if tactical_events:
                result["tactical_events"] = tactical_events
                # Hoist battle_report from tactical events (auto-charge) to result level
                for te in tactical_events:
                    if te.get("battle_report"):
                        result["battle_report"] = te["battle_report"]
                        break

            # Add strategic reports — CRITICAL: without this, strategic popups
            # (hold battles, movement progress) never appear in Godot when the
            # turn auto-advances from actions being exhausted.
            if turn_result.get("strategic_reports"):
                result["strategic_reports"] = turn_result["strategic_reports"]

            # Add Independent Command Report (Phase 2.5) — was missing on auto-advance
            if turn_result.get("show_independent_command_report"):
                result["show_independent_command_report"] = True
                result["independent_command_report"] = turn_result.get("independent_command_report", [])

            # Include saved mild concerns (captured before advance_turn cleared them)
            if saved_mild_concerns:
                result["mild_concerns"] = saved_mild_concerns

            # Build turn_end financial event (same as _execute_end_turn)
            nation = world.player_nation
            income_data = world.calculate_turn_income(nation)
            upkeep_data = world.calculate_turn_upkeep(nation)
            treasury = world.nation_gold.get(nation, 0)
            income_val = income_data["income"]
            upkeep_val = upkeep_data["total"]
            spent_val = saved_gold_spent.get(nation, 0)
            net_val = income_val - upkeep_val
            bk_turns = int(world.nation_bankruptcy_turns.get(nation, 0))
            turn_end_event = {
                "type": "turn_end",
                "old_turn": int(turn_result.get("turn_ended", world.current_turn - 1)),
                "new_turn": int(turn_result.get("next_turn", world.current_turn)),
                "income": int(income_val),
                "upkeep": int(upkeep_val),
                "spent": int(spent_val),
                "net": int(net_val),
                "treasury": int(treasury),
                "bankruptcy_turns": bk_turns,
            }
            existing_events = result.get("events", [])
            result["events"] = [turn_end_event] + existing_events + turn_result.get("events", [])

            # Append financial summary to message
            net_sign = "+" if net_val >= 0 else ""
            spent_str = f" | Spent: {spent_val}g" if spent_val > 0 else ""
            result["message"] = result.get("message", "") + f"\n\nIncome: {income_val}g | Upkeep: {upkeep_val}g | Net: {net_sign}{net_val}g{spent_str} | Treasury: {treasury:,}g"
            if bk_turns > 0:
                result["message"] += f"\nWARNING: Bankrupt for {bk_turns} turn{'s' if bk_turns > 1 else ''}!"

            # Phase 6.2.F: Occupation may complete during turn resolution
            if world.pending_capture_choice:
                result["pending_capture_choice"] = True
                result["capture_data"] = world.pending_capture_choice

            # Check victory/defeat
            if turn_result.get("victory_check", {}).get("game_over"):
                result["game_over"] = True
                result["victory"] = turn_result["victory_check"].get("result")

            # Morning Dispatch — Berthier's turn-start briefing (Phase 6.5, auto-advance path)
            from backend.game_logic.dispatch import build_morning_dispatch
            result["morning_dispatch"] = build_morning_dispatch(world, tactical_events)

            # Autosave at start of new turn (auto-advance path, mirrors _execute_end_turn)
            from backend.save_manager import autosave
            autosave_result = autosave(world)
            if not autosave_result["success"]:
                print(f"Autosave warning: {autosave_result['message']}")

        return result

    def _execute_specific(self, command: Dict, game_state: Dict) -> Dict:
        """Execute a specific order (marshal and action both specified)."""
        marshal_name = command.get("marshal")
        action = command.get("action")
        target = command.get("target")

        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Handle different actions
        if action == "attack":
            return self._execute_attack(marshal, target, world, game_state)
        elif action == "defend":
            return self._execute_defend(marshal, world, game_state)
        elif action == "hold":
            # Hold is an alias for defend - same mechanics, different flavor
            return self._execute_hold(marshal, world, game_state)
        elif action == "wait":
            # Wait is a free action - marshal passes turn
            return self._execute_wait(marshal, world, game_state)
        elif action == "move":
            return self._execute_move(marshal, target, world, game_state)
        elif action == "scout":
            return self._execute_scout(marshal, target, world, game_state)
        elif action == "retreat":
            return self._execute_retreat_action(marshal, world, game_state)
        elif action == "drill":
            return self._execute_drill(command, game_state)
        elif action == "fortify":
            return self._execute_fortify(command, game_state)
        elif action == "unfortify":
            return self._execute_unfortify(command, game_state)
        elif action == "form_square":
            return self._execute_form_square(command, game_state)
        elif action == "break_square":
            return self._execute_break_square(command, game_state)
        elif action == "stance_change":
            return self._execute_stance_change(command, game_state)
        elif action == "cheat":
            return self._execute_cheat(command, game_state)
        elif action == "debug":
            return self._execute_debug(command, game_state)
        else:
            return {
                "success": False,
                "message": f"Unknown action: {action}"
            }

    def _apply_battle_effects_to_region(
        self,
        region_name: str,
        attacker_strength: int,
        defender_strength: int,
        world: 'WorldState'
    ) -> None:
        """Apply war damage, stability hit, and building damage to a region after battle.

        Uses pre-battle troop counts for the 50k major battle threshold.
        Civilian buildings (markets, depots, training grounds) damaged by battle.
        Fortifications are immune — they're built to withstand combat and provide
        contested capture holdout value even after the defending army retreats.
        """
        import random
        region = world.get_region(region_name)
        if not region:
            return
        combined = attacker_strength + defender_strength
        is_major = combined >= 50000
        region.apply_war_damage(0.20 if is_major else 0.10)
        region.stability = max(0, region.stability - 10)

        # Battle damages civilian buildings (not fortifications — forts are built to withstand combat
        # and their value is delaying capture via contested capture mechanic in 6.2.F)
        # Major battles (50k+ troops) always damage; normal battles 25% chance
        for building in region.buildings:
            if building["type"] != "fortification" and not building.get("damaged", False):
                if is_major or random.random() < 0.25:
                    building["damaged"] = True
                    world.log_event({
                        "type": "building_damaged",
                        "region": region_name,
                        "building": building["type"],
                        "cause": "battle",
                    })

        # Watchtower battle damage (Phase 6 Fog - Session 35)
        # Active → damaged. Under construction → destroyed (none).
        wt = getattr(region, 'watchtower', 'none')
        if wt == "active":
            if is_major or random.random() < 0.25:
                region.watchtower = "damaged"
                world.log_event({
                    "type": "building_damaged",
                    "region": region_name,
                    "building": "watchtower",
                    "cause": "battle",
                })
        elif wt == "under_construction":
            # Under construction + battle → destroyed
            region.watchtower = "none"
            region.watchtower_turns_remaining = 0
            world.log_event({
                "type": "building_damaged",
                "region": region_name,
                "building": "watchtower",
                "cause": "battle",
            })

    def _log_battle_event(self, battle_result: Dict, location: str, world) -> None:
        """Extract and log the battle event from a combat result dict."""
        event = battle_result.get("log_battle_event")
        if event:
            event = event.copy()
            event["location"] = location
            world.log_event(event)

    def _process_combat_notifications(self, battle_result: Dict, attacker, defender, world) -> None:
        """Create notifications for combat side effects (counter-punch earned, drill cancelled)."""
        from backend.notifications import (
            create_notification, NotificationPriority,
            COUNTER_PUNCH_EARNED, DRILL_CANCELLED,
        )
        player_nation = getattr(world, 'player_nation', 'France')

        # Counter-punch earned: defender earned a free attack
        if battle_result.get("counter_punch_earned"):
            if getattr(defender, 'nation', '') == player_nation:
                world.notifications.add(create_notification(
                    notification_type=COUNTER_PUNCH_EARNED,
                    priority=NotificationPriority.HIGH,
                    title=f"{defender.name} — free attack!",
                    message=f"{defender.name} earned a free attack from their defensive victory. Use within 2 turns or the opportunity expires.",
                    turn_created=int(world.current_turn),
                    details={"marshal": defender.name},
                ))

        # Drill cancelled: defender's drill training destroyed
        if battle_result.get("drill_cancelled"):
            if getattr(defender, 'nation', '') == player_nation:
                world.notifications.add(create_notification(
                    notification_type=DRILL_CANCELLED,
                    priority=NotificationPriority.HIGH,
                    title=f"{defender.name} drill lost",
                    message=f"{defender.name}'s drill training was destroyed by the enemy attack. All progress lost — must restart from scratch.",
                    turn_created=int(world.current_turn),
                    details={"marshal": defender.name},
                ))

    def _handle_forced_retreat(
        self,
        battle_result: Dict,
        attacker,
        defender,
        world: 'WorldState'
    ) -> str:
        """
        Handle forced retreat for broken armies after combat.

        When morale drops below 25%, the army is forced to retreat.
        - If safe retreat exists: normal retreat to that location
        - If SURROUNDED (no safe retreat): Army is BROKEN
          - Teleports to spawn_location (capital) with 3-10% of forces
          - Takes 4 turns to recover
          - Can ONLY recruit during recovery

        Returns message describing any forced retreats or broken armies.
        """
        retreat_messages = []

        # Check attacker forced retreat
        if battle_result.get("attacker", {}).get("forced_retreat"):
            if attacker and attacker.strength > 0:
                msg = self._apply_forced_retreat_or_break(attacker, defender, world)
                if msg:
                    retreat_messages.append(msg)

        # Check defender forced retreat
        if battle_result.get("defender", {}).get("forced_retreat"):
            if defender and defender.strength > 0:
                msg = self._apply_forced_retreat_or_break(defender, attacker, world)
                if msg:
                    retreat_messages.append(msg)

        if retreat_messages:
            return "\n" + "\n".join(retreat_messages)
        return ""

    def _has_depot_supply_bonus(self, world, region_name, nation):
        """Check if destination or any adjacent region has a friendly undamaged supply depot.

        Used for depot forward logistics: depots project supply benefits
        to the region they're in AND adjacent regions, halving movement attrition.
        """
        region = world.get_region(region_name)
        if not region:
            return False

        # Check destination region itself
        if region.controller == nation:
            if region.has_building("supply_depot"):
                return True

        # Check adjacent regions
        for adj_name in region.adjacent_regions:
            adj = world.get_region(adj_name)
            if adj and adj.controller == nation:
                if adj.has_building("supply_depot"):
                    return True
        return False

    def _resolve_garrison_combat(self, marshal, target_region, world, game_state) -> dict:
        """
        Resolve combat between an attacking marshal and a capital garrison.

        Garrison fights with simplified combat: no morale, no retreat, no flanking.
        Attacker stays in their original region until garrison falls below 5,000.
        Garrison gets terrain defense bonus and fortification building bonus.

        Args:
            marshal: Attacking marshal
            target_region: Region with garrison
            world: Current world state
            game_state: Game state dict

        Returns:
            Result dict with success, message, events
        """
        # Calculate garrison effective defense
        terrain_bonus = TERRAIN_DEFENSE_BONUS.get(target_region.terrain, 0.0)
        fort_bonus = 0.25 if target_region.has_building("fortification") else 0.0
        garrison_effective = int(target_region.garrison_strength * (1.0 + terrain_bonus) * (1.0 + fort_bonus))

        # Attacker effective strength (uses single-source modifier from marshal.py)
        attacker_modifier = marshal.get_attack_modifier()
        attacker_effective = int(marshal.strength * attacker_modifier)

        # Calculate losses — proportional exchange
        # Garrison damage to attacker: ratio of garrison_effective to attacker_effective
        # Attacker damage to garrison: ratio of attacker_effective to garrison_effective
        if attacker_effective <= 0:
            return {
                "success": False,
                "message": f"{marshal.name} has no combat strength to assault the garrison."
            }

        # Damage ratios (capped to prevent absurd results)
        attacker_damage_ratio = min(0.35, garrison_effective / max(attacker_effective, 1) * 0.25)
        garrison_damage_ratio = min(0.50, attacker_effective / max(garrison_effective, 1) * 0.35)

        attacker_losses = int(marshal.strength * attacker_damage_ratio)
        garrison_losses = int(target_region.garrison_strength * garrison_damage_ratio)

        # Ensure minimum losses on both sides (no zero-damage stalemates)
        attacker_losses = max(attacker_losses, int(marshal.strength * 0.02))
        garrison_losses = max(garrison_losses, int(target_region.garrison_strength * 0.10))

        # Apply losses
        marshal.strength = max(0, marshal.strength - attacker_losses)
        old_garrison = target_region.garrison_strength
        target_region.garrison_strength = max(0, target_region.garrison_strength - garrison_losses)

        # Check if garrison collapsed
        # Capital garrisons collapse below 5k threshold; detachment garrisons fight to destruction
        if target_region.garrison_detachment:
            garrison_collapsed = target_region.garrison_strength <= 0
        else:
            garrison_collapsed = target_region.garrison_strength < 5000

        if garrison_collapsed:
            # Garrison collapses — capture proceeds
            target_region.garrison_strength = 0
            target_region.garrison_detachment = False
            old_controller = target_region.controller
            old_location = marshal.location

            # Record garrison fall for diplomacy war score
            from backend.game_logic.diplomacy import record_battle as record_diplo_battle
            record_diplo_battle(
                world,
                attacker_nation=marshal.nation,
                defender_nation=old_controller,
                winner_nation=marshal.nation,
                attacker_casualties=int(attacker_losses),
                defender_casualties=int(garrison_losses),
            )

            # Move attacker into region
            marshal.move_to(target_region.name)

            # Movement attrition
            attrition_info = self._calculate_movement_attrition(marshal, target_region.name, world)

            # Attempt capture
            capture_result = self._attempt_region_capture(
                marshal, target_region.name, world, game_state, had_garrison=False)

            msg = (
                f"{marshal.name} assaults the {target_region.name} garrison! "
                f"Garrison collapses ({old_garrison:,} -> 0). "
                f"{marshal.name} loses {attacker_losses:,} troops in the assault. "
                f"{marshal.name} marches into {target_region.name}!"
            )
            if attrition_info["total_losses"] > 0:
                msg += f" ({attrition_info['total_losses']:,} lost to march)"

            if capture_result["occupation_started"]:
                msg += f" {capture_result['message']}"
                return {
                    "success": True,
                    "message": msg,
                    "occupation_started": True,
                    "events": [{
                        "type": "garrison_destroyed",
                        "marshal": marshal.name,
                        "region": target_region.name,
                        "garrison_losses": int(garrison_losses),
                        "attacker_losses": int(attacker_losses),
                    }, {
                        "type": "occupation_started",
                        "marshal": marshal.name,
                        "region": target_region.name,
                        "turns_required": capture_result["turns_required"],
                    }],
                    "new_state": game_state
                }

            msg += f" Captured: {old_controller} -> {marshal.nation}"

            conquest_event = {
                "type": "conquest",
                "marshal": marshal.name,
                "region": target_region.name,
                "garrison_destroyed": True,
            }
            if capture_result.get("capture_choice"):
                conquest_event["capture_choice"] = capture_result["capture_choice"]

            result = {
                "success": True,
                "message": msg,
                "events": [conquest_event],
                "new_state": game_state
            }

            if marshal.nation == world.player_nation and world.pending_capture_choice:
                result["message"] += "\nYour forces have taken the region! How shall they behave?"
                result["pending_capture_choice"] = True
                result["capture_data"] = world.pending_capture_choice

            return result
        else:
            # Garrison holds — attacker stays in place
            msg = (
                f"{marshal.name} assaults the {target_region.name} garrison! "
                f"Garrison: {old_garrison:,} -> {target_region.garrison_strength:,} "
                f"(-{garrison_losses:,}). "
                f"{marshal.name} loses {attacker_losses:,} troops. "
                f"Garrison holds — {target_region.garrison_strength:,} defenders remain."
            )
            if target_region.has_building("fortification"):
                msg += " Fortifications bolster the defense."

            # Record garrison hold for diplomacy war score
            from backend.game_logic.diplomacy import record_battle as record_diplo_battle
            record_diplo_battle(
                world,
                attacker_nation=marshal.nation,
                defender_nation=target_region.controller,
                winner_nation=target_region.controller,
                attacker_casualties=int(attacker_losses),
                defender_casualties=int(garrison_losses),
            )

            return {
                "success": True,
                "message": msg,
                "events": [{
                    "type": "garrison_assault",
                    "marshal": marshal.name,
                    "region": target_region.name,
                    "garrison_losses": int(garrison_losses),
                    "attacker_losses": int(attacker_losses),
                    "garrison_remaining": int(target_region.garrison_strength),
                }],
            }

    def _calculate_movement_attrition(self, marshal, destination_region, world, is_retreat=False) -> dict:
        """Calculate and apply movement attrition. Returns info dict.

        Args:
            marshal: Marshal moving
            destination_region: Name of destination region
            world: WorldState
            is_retreat: If True, halved base rate (0.5% vs 1%)

        Returns:
            Dict with march_losses, harassment_losses, total_losses, destination
        """
        base = 0.005 if is_retreat else 0.01
        size_penalty = min(0.02, max(0, (marshal.strength - 20000) / 500000))
        rate = base + size_penalty

        # Terrain multiplier from destination
        region = world.get_region(destination_region)
        terrain_mult = region.movement_cost if region else 1.0
        rate *= terrain_mult

        # Friendly stable territory: no march attrition (good roads, supply lines)
        is_friendly_stable = (
            region and region.controller == marshal.nation and region.stability >= 76
        )

        # Depot forward logistics: halve march attrition if friendly depot nearby
        # Only for normal moves, not retreats (retreats already have their own 0.5x)
        depot_bonus = False
        if not is_friendly_stable and not is_retreat:
            if self._has_depot_supply_bonus(world, destination_region, marshal.nation):
                rate *= 0.5
                depot_bonus = True

        losses = 0 if is_friendly_stable else int(marshal.strength * rate)
        harassment_losses = 0

        # Harassment from enemy fortification
        if region and region.controller and region.controller != marshal.nation:
            if region.has_building("fortification"):
                harassment_losses = int(marshal.strength * 0.04)
            # Harassment from enemy garrison detachment (smaller than fort — 2%)
            if region.garrison_detachment and region.garrison_strength > 0:
                harassment_losses += int(marshal.strength * 0.02)

        total_losses = losses + harassment_losses
        if total_losses > 0:
            marshal.strength = max(0, marshal.strength - total_losses)

        return {
            "march_losses": int(losses),
            "harassment_losses": int(harassment_losses),
            "total_losses": int(total_losses),
            "destination": destination_region,
            "depot_bonus": depot_bonus,
        }

    def _apply_forced_retreat_or_break(self, marshal, enemy, world: 'WorldState') -> str:
        """
        Apply forced retreat or break the army if surrounded.

        Uses get_safe_retreat_destination (BUG-009 fix) which properly checks
        threat zones. If no safe retreat exists, army is BROKEN.

        Returns message describing what happened.
        """
        import random

        # Try to find safe retreat location using threat-aware pathfinding
        # Pass attacker location to prioritize retreating AWAY from the threat
        attacker_location = getattr(enemy, 'location', None) if enemy else None
        retreat_to = world.get_safe_retreat_destination(marshal.name, attacker_location)

        if retreat_to:
            # ════════════════════════════════════════════════════════════
            # NORMAL FORCED RETREAT: Safe location found
            # ════════════════════════════════════════════════════════════
            old_loc = marshal.location
            # Clear occupation state (Phase 6.2.F) — forced retreat breaks occupation
            marshal.occupation_region = None
            marshal.occupation_turns_held = 0
            marshal.occupation_turns_required = 0
            # Clear strategic order before moving (forced retreat breaks all orders)
            strategic_msg = ""
            if marshal.strategic_order:
                cmd_type = marshal.strategic_order.command_type
                if cmd_type == "HOLD":
                    strategic_msg = f" {marshal.name}'s HOLD order at {old_loc} is broken!"
                    marshal.holding_position = False
                    marshal.hold_region = ""
                else:
                    strategic_msg = f" {marshal.name}'s {cmd_type} order is cancelled!"
                # Notification: forced retreat voided strategic order (player only)
                if getattr(marshal, 'nation', '') == getattr(world, 'player_nation', 'France'):
                    from backend.notifications import (
                        create_notification, NotificationPriority, FORCED_RETREAT_ORDER_VOIDED,
                    )
                    world.notifications.add(create_notification(
                        notification_type=FORCED_RETREAT_ORDER_VOIDED,
                        priority=NotificationPriority.CRITICAL,
                        title=f"{marshal.name} orders lost",
                        message=f"{marshal.name} was forced to retreat to {retreat_to}. Their {cmd_type} order has been cancelled.",
                        turn_created=int(world.current_turn),
                        details={"marshal": marshal.name, "order_type": cmd_type, "retreat_to": retreat_to},
                    ))
                marshal.strategic_order = None
            marshal.move_to(retreat_to)  # Use move_to() for proper state clearing
            # Clear artillery bombardment state — forced retreat breaks sustained fire
            if getattr(marshal, 'artillery', False):
                marshal.last_bombardment_target = None
                marshal.bombardment_streak = 0
            # Movement attrition on forced retreat (Phase 6.2.F) — halved rate
            forced_retreat_attrition = self._calculate_movement_attrition(marshal, retreat_to, world, is_retreat=True)
            marshal.retreating = True
            marshal.retreat_recovery = 0  # Start recovery at stage 0
            marshal.retreated_this_turn = True  # Mark for ally covering system
            attrition_note = ""
            if forced_retreat_attrition["total_losses"] > 0:
                attrition_note = f" ({forced_retreat_attrition['total_losses']:,} lost to march)"
            # Log retreat event
            world.log_event({
                "type": "retreat",
                "marshal": marshal.name,
                "nation": getattr(marshal, "nation", ""),
                "from": old_loc,
                "to": retreat_to,
            })
            return f"⚠️ {marshal.name}'s broken army flees to {retreat_to}!{strategic_msg}{attrition_note} (recovering for 3 turns)"
        else:
            # ════════════════════════════════════════════════════════════
            # SURROUNDED - ARMY BROKEN: No safe retreat possible
            # Army shatters, survivors flee to capital with 3-10% strength
            # ════════════════════════════════════════════════════════════
            old_loc = marshal.location
            old_strength = marshal.strength

            # Calculate survivors (3-10% of current strength)
            survival_rate = random.uniform(0.03, 0.10)
            survivors = max(1000, int(old_strength * survival_rate))  # Minimum 1000 survivors

            # Get spawn location (capital)
            spawn_loc = getattr(marshal, 'spawn_location', 'Paris')

            # Apply broken state
            # NOTE: Broken armies do NOT set retreated_this_turn because:
            # 1. They flee to capital (not adjacent region) - no ally cover possible
            # 2. They're in BROKEN state with 3-10% strength - not a normal retreat
            marshal.move_to(spawn_loc)  # Use move_to() for proper state clearing
            marshal.strength = survivors
            marshal.morale = 20  # Shattered morale
            marshal.broken = True
            marshal.broken_recovery = 0  # Start at stage 0 (4 turns to recover)

            # Clear any other states
            marshal.retreating = False
            marshal.retreat_recovery = 0
            marshal.drilling = False
            marshal.drilling_locked = False
            marshal.shock_bonus = 0
            marshal.fortified = False
            marshal.defense_bonus = 0
            marshal.turns_fortified = 0  # Reset decay counter
            marshal.moved_this_turn = False  # Symmetry: clear artillery movement flag
            marshal.last_bombardment_target = None
            marshal.bombardment_streak = 0
            marshal.stance = Stance.NEUTRAL
            # Clear occupation state (Phase 6.2.F)
            marshal.occupation_region = None
            marshal.occupation_turns_held = 0
            marshal.occupation_turns_required = 0

            # Clear personality ability states
            marshal.turns_in_defensive_stance = 0
            marshal.counter_punch_available = False
            marshal.counter_punch_turns = 0
            marshal.counter_punch_ready = False
            marshal.holding_position = False
            marshal.hold_region = ""

            # Clear strategic order (army shattered, all orders void)
            strategic_msg = ""
            if marshal.strategic_order:
                cmd_type = marshal.strategic_order.command_type
                if cmd_type == "HOLD":
                    strategic_msg = f" {marshal.name}'s HOLD position at {old_loc} is lost!"
                else:
                    strategic_msg = f" {marshal.name}'s {cmd_type} order is void!"
                # Notification: broken army voided strategic order (player only)
                if getattr(marshal, 'nation', '') == getattr(world, 'player_nation', 'France'):
                    from backend.notifications import (
                        create_notification, NotificationPriority, FORCED_RETREAT_ORDER_VOIDED,
                    )
                    world.notifications.add(create_notification(
                        notification_type=FORCED_RETREAT_ORDER_VOIDED,
                        priority=NotificationPriority.CRITICAL,
                        title=f"{marshal.name} orders lost",
                        message=f"{marshal.name}'s army was shattered at {old_loc}. Their {cmd_type} order is void.",
                        turn_created=int(world.current_turn),
                        details={"marshal": marshal.name, "order_type": cmd_type, "location": old_loc},
                    ))
                marshal.strategic_order = None

            survival_percent = int(survival_rate * 100)
            # Log marshal_broken event
            world.log_event({
                "type": "marshal_broken",
                "marshal": marshal.name,
                "nation": getattr(marshal, "nation", ""),
                "location": old_loc,
            })
            return (
                f"💀 {marshal.name}'s army is SURROUNDED and SHATTERED at {old_loc}! "
                f"Only {survivors:,} survivors ({survival_percent}%) escape to {spawn_loc}.{strategic_msg} "
                f"Army is BROKEN - can only recruit for 4 turns!"
            )

    def _execute_bombardment(self, marshal, defender, world: WorldState, game_state) -> Dict:
        """
        Execute ranged bombardment: artillery fires from adjacent region.

        This is NOT a battle — no winner/loser, no counter-punch, no morale swing
        on attacker. Bombardment grinds the target from range at low risk.

        Routing: Called from _execute_attack when artillery attacks a target
        in a different (adjacent) region. Same-region artillery attacks use
        the normal resolve_battle() path.

        Spec reference: BOMBARDMENT_SPEC.md §4
        """
        import random
        from backend.models.region import TERRAIN_BOMBARDMENT_MODIFIER

        # ════════════════════════════════════════════════════════════
        # BOMBARDMENT LIMIT CHECK: max 2 per turn
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'bombardments_this_turn', 0) >= 2:
            return {
                "success": False,
                "message": (
                    f"{marshal.name}'s guns have expended their ammunition for today. "
                    f"The battery needs time to resupply. (Max 2 bombardments per turn)"
                )
            }

        # ════════════════════════════════════════════════════════════
        # DAMAGE CALCULATION (§4.2)
        # ════════════════════════════════════════════════════════════
        defender_region = world.get_region(defender.location)
        terrain = defender_region.terrain if defender_region else "plains"
        terrain_mod = TERRAIN_BOMBARDMENT_MODIFIER.get(terrain, 1.0)

        base_rate = 0.04  # 4% of defender's strength
        shock_skill = marshal.get_effective_skill("shock")
        damage_multiplier = 1.0 + (shock_skill / 15.0)

        # DIMINISHING RETURNS HOOK (not active — see §14)
        # streak = marshal.bombardment_streak
        # if streak >= 5: damage_multiplier *= 0.50
        # elif streak >= 3: damage_multiplier *= 0.75

        # SQUARE FORMATION (Session 67): +50% bombardment damage vs packed square
        square_bombardment_bonus = 1.0
        if getattr(defender, 'square_formation', False):
            square_bombardment_bonus = 1.50

        raw_damage = defender.strength * base_rate * damage_multiplier * terrain_mod * square_bombardment_bonus
        variance = random.uniform(0.80, 1.20)
        defender_casualties = int(raw_damage * variance)

        # ════════════════════════════════════════════════════════════
        # RETURN CASUALTIES (§4.3) — counter-battery / wear
        # ════════════════════════════════════════════════════════════
        return_rate = 0.015  # 1.5% of own strength
        return_variance = random.uniform(0.80, 1.20)
        attacker_casualties = int(marshal.strength * return_rate * return_variance)

        # ════════════════════════════════════════════════════════════
        # FORT DEGRADATION (§5)
        # ════════════════════════════════════════════════════════════
        fortification_degraded = False
        fortification_old = 0.0
        fortification_new = 0.0
        if getattr(defender, 'defense_bonus', 0) > 0:
            fortification_old = defender.defense_bonus
            degradation_amount = 0.10  # Always artillery rate for bombardment
            defender.defense_bonus = max(0, round(defender.defense_bonus - degradation_amount, 2))
            fortification_new = defender.defense_bonus
            fortification_degraded = True

        # ════════════════════════════════════════════════════════════
        # APPLY CASUALTIES
        # ════════════════════════════════════════════════════════════
        pre_defender_strength = defender.strength
        defender.take_casualties(defender_casualties)
        marshal.take_casualties(attacker_casualties)

        # ════════════════════════════════════════════════════════════
        # MORALE EFFECTS (§4.7)
        # Defender: -3 per bombardment. Attacker: None.
        # SQUARE FORMATION (Session 67): Extra -15 morale (packed troops panic under shells)
        # ════════════════════════════════════════════════════════════
        bombardment_morale = -3
        if getattr(defender, 'square_formation', False):
            bombardment_morale -= 15
        defender.adjust_morale(bombardment_morale)

        # Capture target location before defender might be broken/moved
        target_location = defender.location

        # ════════════════════════════════════════════════════════════
        # COLLATERAL DAMAGE (§4.4): Shells hit other forces in target region
        # 40% chance per non-primary marshal, 25% of primary raw damage
        # Affects marshals only — not capital garrisons or detachments
        # ════════════════════════════════════════════════════════════
        collateral_results = []
        collateral_messages = []
        friendly_fire_redemption = None

        all_in_region = [
            m for m in world.get_marshals_in_region(target_location)
            if m.name != defender.name and m.strength > 0
            and not getattr(m, 'broken', False)
            and not getattr(m, 'retreating', False)
        ]

        for force in all_in_region:
            if random.random() < 0.40:
                collateral_raw = raw_damage * 0.25  # 25% of primary raw damage
                collateral_variance = random.uniform(0.80, 1.20)
                collateral_casualties = int(collateral_raw * collateral_variance)

                if collateral_casualties > 0:
                    force.take_casualties(collateral_casualties)
                    force.adjust_morale(-1)

                    is_friendly = (force.nation == marshal.nation)

                    collateral_entry = {
                        "name": force.name,
                        "nation": force.nation,
                        "casualties": int(collateral_casualties),
                        "friendly_fire": is_friendly,
                    }
                    collateral_results.append(collateral_entry)

                    if is_friendly:
                        collateral_messages.append(
                            f"  FRIENDLY FIRE: {force.name} ({marshal.nation}) "
                            f"— {collateral_casualties:,} casualties from stray shells!"
                        )
                        # Trust penalty: -5 (§4.4)
                        force.trust.modify(-5)
                        # Relationship penalty: -1 with artillery marshal
                        force.modify_relationship(marshal.name, -1)
                        # Notification: friendly fire trust penalty (player only)
                        if force.nation == getattr(world, 'player_nation', 'France'):
                            from backend.notifications import (
                                create_notification, NotificationPriority, FRIENDLY_FIRE_TRUST,
                            )
                            trust_val = int(force.trust.value)
                            world.notifications.add(create_notification(
                                notification_type=FRIENDLY_FIRE_TRUST,
                                priority=NotificationPriority.HIGH,
                                title=f"Friendly fire — {force.name}",
                                message=f"{force.name} caught in {marshal.name}'s bombardment. Trust dropped to {trust_val}.",
                                turn_created=int(world.current_turn),
                                details={"victim": force.name, "bombarder": marshal.name, "trust": trust_val},
                            ))

                        # Redemption threshold check (§4.4)
                        # Only trigger for first victim — game handles one
                        # redemption at a time; others fire on next action.
                        if not friendly_fire_redemption:
                            friendly_fire_redemption = (
                                world.disobedience_system.check_redemption_threshold(force, world))
                    else:
                        collateral_messages.append(
                            f"  Collateral: {force.name} ({force.nation}) "
                            f"— {collateral_casualties:,} casualties from stray shells"
                        )

                    # Collateral target destroyed
                    if force.strength <= 0 and force.name in world.marshals:
                        self._apply_forced_retreat_or_break(force, marshal, world)

        # ════════════════════════════════════════════════════════════
        # BOMBARDMENT STREAK TRACKING
        # ════════════════════════════════════════════════════════════
        if target_location == getattr(marshal, 'last_bombardment_target', None):
            marshal.bombardment_streak += 1
        else:
            marshal.last_bombardment_target = target_location
            marshal.bombardment_streak = 1

        # ════════════════════════════════════════════════════════════
        # INCREMENT COUNTERS
        # ════════════════════════════════════════════════════════════
        marshal.bombardments_this_turn += 1
        marshal.increment_attacks_this_turn()  # Shares exhaustion counter
        marshal.in_combat_this_turn = True  # For cannon fire interrupt detection
        marshal.idle_turns = 0
        marshal._acted_this_turn = True  # Prevents idle increment at turn end

        # Record attack for flanking system (bombardment counts)
        world.record_attack(marshal.name, marshal.location, target_location)

        # Record battle for cannon fire detection (hearing the guns)
        world.record_battle(target_location, marshal.name, defender.name, "bombardment")

        # ════════════════════════════════════════════════════════════
        # CHECK IF DEFENDER DESTROYED (§4.8)
        # Reuses _apply_forced_retreat_or_break for consistent state clearing.
        # Region NOT captured — artillery doesn't advance.
        # ════════════════════════════════════════════════════════════
        enemy_destroyed = defender.strength <= 0
        destroyed_msg = ""
        if enemy_destroyed and defender.name in world.marshals:
            # Use the existing break system for proper state clearing
            break_msg = self._apply_forced_retreat_or_break(
                defender, marshal, world)
            destroyed_msg = f"\n{break_msg}"

        # ════════════════════════════════════════════════════════════
        # BUILD NARRATIVE MESSAGE
        # ════════════════════════════════════════════════════════════
        terrain_display = terrain.replace("_", " ").title()
        if terrain_mod > 1.0:
            terrain_note = f" Open {terrain_display} terrain offers no cover from the shells."
        elif terrain_mod < 0.80:
            terrain_note = f" The {terrain_display} terrain provides significant cover, reducing effectiveness."
        elif terrain_mod < 1.0:
            terrain_note = f" The {terrain_display} terrain provides some cover."
        else:
            terrain_note = ""

        fort_note = ""
        if fortification_degraded:
            if fortification_new <= 0:
                fort_note = " The enemy fortifications have been completely destroyed!"
            else:
                fort_note = f" Enemy fortifications degraded ({int(fortification_old * 100)}% → {int(fortification_new * 100)}%)."

        destroyed_note = ""
        if enemy_destroyed:
            destroyed_note = destroyed_msg  # Contains break/shatter message from existing system

        collateral_note = ""
        if collateral_messages:
            collateral_note = "\n\n  -- Collateral Damage --\n" + "\n".join(collateral_messages)

        message = (
            f"{'=' * 40}\n"
            f"  BOMBARDMENT: {marshal.name} → {defender.name}\n"
            f"{'=' * 40}\n"
            f"{marshal.name}'s guns thunder from {marshal.location}, "
            f"raining shells on {defender.name}'s position at {target_location}.\n"
            f"{terrain_note}\n"
            f"  Enemy casualties: {defender_casualties:,} "
            f"({defender.name}: {pre_defender_strength:,} → {int(defender.strength):,})\n"
            f"  Return fire/wear: {attacker_casualties:,} "
            f"({marshal.name}: {int(marshal.strength + attacker_casualties):,} → {int(marshal.strength):,})\n"
            f"  Defender morale: {int(defender.morale)}%"
            f"{fort_note}{destroyed_note}{collateral_note}"
        )

        # ════════════════════════════════════════════════════════════
        # BOMBARDMENT ADVISORY (carry forward from old system)
        # ════════════════════════════════════════════════════════════
        bombardment_advisory = None
        if not enemy_destroyed:
            defender_fort = getattr(defender, 'defense_bonus', 0)
            target_reg = world.get_region(target_location)
            has_fort_building = (target_reg.has_building("fortification")
                                if target_reg and hasattr(target_reg, 'has_building') else False)
            if defender_fort <= 0 and not has_fort_building:
                bombardment_advisory = (
                    f"Sire, the enemy fortifications at {target_location} are crumbling. "
                    f"An infantry assault would now have favorable odds."
                )

        # ════════════════════════════════════════════════════════════
        # EVENT LOG (§8)
        # ════════════════════════════════════════════════════════════
        bombardment_event = {
            "type": "bombardment",
            "attacker": marshal.name,
            "attacker_nation": marshal.nation,
            "defender": defender.name,
            "defender_nation": defender.nation,
            "attacker_location": marshal.location,
            "defender_location": target_location,
            "attacker_casualties": int(attacker_casualties),
            "defender_casualties": int(defender_casualties),
            "terrain": terrain,
            "terrain_modifier": terrain_mod,
            "fort_degraded": fortification_degraded,
            "fort_old": fortification_old,
            "fort_new": fortification_new,
            "collateral": collateral_results,
        }
        world.log_event(bombardment_event)

        # Fog of War: Bombardment grants visibility on target region
        world.update_intel_from_battle(target_location, world.current_turn)

        # ════════════════════════════════════════════════════════════
        # BERTHIER OBSERVATION (§11)
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.battle_report import generate_bombardment_report

        berthier_observation = generate_bombardment_report({
            "attacker_name": marshal.name,
            "defender_name": defender.name,
            "attacker_casualties": int(attacker_casualties),
            "defender_casualties": int(defender_casualties),
            "defender_remaining": int(defender.strength),
            "defender_original": int(pre_defender_strength),
            "terrain": terrain,
            "terrain_modifier": terrain_mod,
            "fort_degraded": fortification_degraded,
            "fort_old": fortification_old,
            "fort_new": fortification_new,
            "collateral": collateral_results,
        })

        # ════════════════════════════════════════════════════════════
        # BUILD RESULT DICT
        # ════════════════════════════════════════════════════════════
        bombardments_remaining = max(0, 2 - marshal.bombardments_this_turn)

        result = {
            "success": True,
            "action": "bombardment",
            "message": message,
            "bombardment_result": {
                "attacker": {
                    "name": marshal.name,
                    "casualties": int(attacker_casualties),
                    "remaining": int(marshal.strength),
                },
                "defender": {
                    "name": defender.name,
                    "casualties": int(defender_casualties),
                    "remaining": int(defender.strength),
                    "morale": int(defender.morale),
                },
                "terrain": terrain,
                "terrain_modifier": terrain_mod,
                "fort_degraded": fortification_degraded,
                "fort_old": fortification_old,
                "fort_new": fortification_new,
                "bombardments_remaining": int(bombardments_remaining),
                "collateral": collateral_results,
                "berthier_observation": str(berthier_observation),
            },
            "events": [bombardment_event],
            "new_state": game_state,
        }

        if bombardment_advisory:
            result["bombardment_advisory"] = bombardment_advisory

        # Friendly fire redemption event (§4.4)
        if friendly_fire_redemption:
            result["redemption_event"] = friendly_fire_redemption

        return result

    def _execute_attack(self, marshal, target, world: WorldState, game_state, skip_reckless_popup: bool = False) -> Dict:
        """
        Execute an attack order with combat and region conquest.

        If attacking a region, will capture it after defeated all defenders.
        Handles undefended regions with instant capture.

        Args:
            skip_reckless_popup: If True, skip the recklessness popup check.
                                 Used when called from respond_to_glorious_charge.
        """
        # Auto-break square formation (Session 67)
        self._auto_break_square(marshal, "attack")

        # ════════════════════════════════════════════════════════════
        # COUNTER-PUNCH CHECK (Phase 2.8): Davout's free attack after defending
        # If Davout has counter_punch_available, this attack costs 0 actions
        # ════════════════════════════════════════════════════════════
        counter_punch_message = ""
        is_counter_punch = False
        if getattr(marshal, 'counter_punch_available', False) and marshal.personality == 'cautious':
            is_counter_punch = True
            marshal.counter_punch_available = False  # Consume the counter-punch
            marshal.counter_punch_turns = 0  # Clear the turns counter
            counter_punch_message = (
                f"========================================\n"
                f"  [!] COUNTER-PUNCH! (FREE ACTION) [!]  \n"
                f"========================================\n"
                f"{marshal.name} strikes back after successfully defending!\n"
                f"This attack costs NO actions.\n\n"
            )
            print(f"  [COUNTER-PUNCH] {marshal.name} uses counter-punch (free attack)")

        # ════════════════════════════════════════════════════════════
        # DRILL STATE CHECK: Handle drilling marshal trying to attack
        # ════════════════════════════════════════════════════════════
        drill_cancelled_message = ""
        if getattr(marshal, 'drilling', False):
            if getattr(marshal, 'drilling_locked', False):
                # Turn 2: Locked in drill, cannot attack
                return {
                    "success": False,
                    "message": f"{marshal.name} is locked in drill formation and cannot attack. Only RETREAT is allowed.",
                    "drilling_locked": True
                }
            else:
                # Turn 1: Can attack but drill is cancelled
                marshal.drilling = False
                marshal.drill_complete_turn = -1
                drill_cancelled_message = f"⚠️ DRILL CANCELLED: {marshal.name}'s drill was interrupted - troops dispersed before training completed.\n\n"

        # ════════════════════════════════════════════════════════════
        # ARTILLERY MOVEMENT CHECK: Can't attack on the turn artillery moved
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'artillery', False) and getattr(marshal, 'moved_this_turn', False):
            return {
                "success": False,
                "message": f"{marshal.name}'s artillery is still setting up after repositioning. "
                           f"Available to fire next turn."
            }

        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS CHECK (Phase 3)
        # At recklessness 3+, trigger popup for player choice
        # At recklessness 4+, auto-charge (handled in turn start, not here)
        # AI (non-player nation) auto-charges at 3+ without popup
        # Skip if called from restrain response (skip_reckless_popup=True)
        # ════════════════════════════════════════════════════════════
        if marshal.is_reckless_cavalry and not skip_reckless_popup:
            recklessness = getattr(marshal, 'recklessness', 0)
            is_player = marshal.nation == world.player_nation

            # At recklessness 3, player gets popup choice
            # AI at 3+ auto-charges
            if recklessness >= 3:
                # Resolve target if empty (find nearest enemy) BEFORE proceeding
                # This ensures we have a valid target for the popup or auto-charge
                resolved_target = target
                if not resolved_target:
                    nearest = world.find_nearest_enemy(marshal.location)
                    if nearest:
                        enemy, dist = nearest
                        if dist <= marshal.movement_range:
                            resolved_target = enemy.name

                # Only trigger recklessness popup/auto-charge if we have a valid target
                # If no target in range, let normal attack flow handle it (move toward enemy)
                if resolved_target:
                    # ════════════════════════════════════════════════════════════
                    # TERRAIN CHARGE BLOCKING (Phase 6.1): mountains/forest/urban
                    # block cavalry charges. Check the DEFENDER's region terrain.
                    # If blocked, look for alternative chargeable enemies in range
                    # on allowed terrain. If alternatives exist, offer popup to
                    # redirect the charge. Otherwise show terrain-blocked message
                    # and fall through to normal attack.
                    # ════════════════════════════════════════════════════════════
                    charge_terrain_blocked = False
                    blocked_terrain_name = None
                    charge_target_marshal = None
                    for m in world.marshals.values():
                        if m.name.lower() == resolved_target.lower() and m.nation != marshal.nation:
                            charge_target_marshal = m
                            break
                    if charge_target_marshal:
                        # Check terrain at DEFENDER's location (not attacker's)
                        charge_target_region = world.get_region(charge_target_marshal.location)
                        if charge_target_region and charge_target_region.terrain in CHARGE_BLOCKED_TERRAIN:
                            charge_terrain_blocked = True
                            blocked_terrain_name = charge_target_region.terrain.replace("_", " ").title()

                    if charge_terrain_blocked:
                        # ── Terrain blocks charge on this target. Check for ──
                        # ── alternative enemies in range on allowed terrain.  ──
                        # Sort by: nearest first, then weakest (reckless cavalry
                        # charges the closest easy prey on open ground).
                        chargeable_alternatives = []
                        for m in world.marshals.values():
                            if m.nation == marshal.nation or m.strength <= 0:
                                continue
                            if m.name == (charge_target_marshal.name if charge_target_marshal else ""):
                                continue  # Skip the blocked target
                            dist = world.get_distance(marshal.location, m.location)
                            if dist <= marshal.movement_range:
                                alt_region = world.get_region(m.location)
                                if alt_region and alt_region.terrain not in CHARGE_BLOCKED_TERRAIN:
                                    alt_terrain = alt_region.terrain.replace("_", " ").title()
                                    chargeable_alternatives.append({
                                        "name": m.name,
                                        "location": m.location,
                                        "terrain": alt_terrain,
                                        "distance": dist,
                                        "strength": m.strength,
                                    })
                        # Nearest first, weakest as tiebreaker
                        chargeable_alternatives.sort(key=lambda a: (a["distance"], a["strength"]))

                        if chargeable_alternatives and is_player and recklessness < 4:
                            # Offer popup to redirect charge to an alternative target
                            alt_lines = []
                            for alt in chargeable_alternatives:
                                alt_lines.append(f"• CHARGE {alt['name'].upper()}: "
                                                f"at {alt['location']} ({alt['terrain']}, {alt['distance']} away)")
                            alt_text = "\n".join(alt_lines)

                            marshal.pending_glorious_charge = True
                            marshal.pending_charge_target = chargeable_alternatives[0]["name"]

                            return {
                                "success": False,
                                "pending_glorious_charge": True,
                                "marshal": marshal.name,
                                "target": chargeable_alternatives[0]["name"],
                                "recklessness": recklessness,
                                "charge_redirected": True,
                                "blocked_target": resolved_target,
                                "blocked_terrain": blocked_terrain_name,
                                "message": (
                                    f"🐴⛔ {marshal.name}'s blood is up (Recklessness: {recklessness}) "
                                    f"but {blocked_terrain_name} terrain at {charge_target_marshal.location} "
                                    f"blocks the cavalry charge!\n\n"
                                    f"Alternative targets on open ground:\n{alt_text}\n\n"
                                    f"• CHARGE: Redirect charge to {chargeable_alternatives[0]['name']}\n"
                                    f"• RESTRAIN: Normal attack on {resolved_target} (no charge bonus)"
                                ),
                                "options": ["charge", "restrain"]
                            }
                        else:
                            # No alternatives (or AI/4+) — tell player terrain blocks,
                            # fall through to normal attack below
                            print(f"  [CHARGE BLOCKED] {blocked_terrain_name} terrain blocks "
                                  f"{marshal.name}'s charge on {resolved_target} — normal attack")

                    elif not charge_terrain_blocked:
                        # Terrain allows charge — show popup or auto-charge
                        # Strategic execution (sally, etc.) auto-charges — no popup.
                        # Ney on HOLD sallies autonomously; he wouldn't stop mid-charge
                        # to ask permission. Result shows in strategic report.
                        is_strategic_sally = marshal.in_strategic_mode
                        if is_player and recklessness < 4 and not is_strategic_sally:  # Player at exactly 3 - popup
                            # Set pending state for popup
                            marshal.pending_glorious_charge = True
                            marshal.pending_charge_target = resolved_target

                            return {
                                "success": False,  # Not executed yet - waiting for response
                                "pending_glorious_charge": True,
                                "marshal": marshal.name,
                                "target": resolved_target,
                                "recklessness": recklessness,
                                "message": f"🐴 {marshal.name}'s blood is up! (Recklessness: {recklessness})\n\n"
                                          f"Choose:\n"
                                          f"• CHARGE: Execute Glorious Charge (2x damage dealt AND taken, resets recklessness)\n"
                                          f"• RESTRAIN: Normal attack (marshal may object next time)",
                                "options": ["charge", "restrain"]
                            }
                        else:
                            # AI at 3+ or Player at 4+ - auto-charge
                            return self._execute_glorious_charge(marshal, resolved_target, world, game_state)

        # Handle None target - find nearest enemy for this marshal
        if not target:
            # Find the nearest enemy to this specific marshal
            # FOG-AWARE (Session 37): Player marshals only auto-target visible enemies
            if marshal.nation == world.player_nation and hasattr(world, 'get_region_intel'):
                from backend.models.intel import FULL as _FULL, PARTIAL as _PARTIAL
                result = world.find_nearest_enemy(
                    marshal.location,
                    filter_fn=lambda e: world.get_region_intel(e.location).visibility in (_FULL, _PARTIAL)
                )
            else:
                result = world.find_nearest_enemy(marshal.location)

            if result:
                nearest_enemy, distance = result
                # Check if in range (distance already returned by find_nearest_enemy)
                if distance <= marshal.movement_range:
                    # Auto-target the nearest enemy
                    target = nearest_enemy.name
                else:
                    # Out of range — literal marshals ask for clarification instead of guessing
                    if getattr(marshal, 'personality', '') == 'literal':
                        enemies = [e for e in world.get_enemies_of_nation(marshal.nation) if e.strength > 0]
                        # FOG-AWARE (Session 37): Only show visible enemies for player
                        if marshal.nation == world.player_nation and hasattr(world, 'get_region_intel'):
                            from backend.models.intel import FULL, PARTIAL
                            enemies = [e for e in enemies
                                       if world.get_region_intel(e.location).visibility in (FULL, PARTIAL)]
                        options = []
                        for e in enemies[:3]:
                            e_dist = world.get_distance(marshal.location, e.location)
                            options.append({
                                "label": f"Pursue {e.name} ({e.location}, {e_dist} away)",
                                "value": "specify",
                                "target": e.name
                            })
                        # Note: popup adds its own "Cancel Order" button — don't duplicate
                        return {
                            "success": True,
                            "free_action": True,
                            "state": "awaiting_clarification",
                            "type": "clarification",
                            "strategic_type": "PURSUE",
                            "marshal": marshal.name,
                            "message": f"{nearest_enemy.name} is {distance} regions away, Sire. Shall I pursue?",
                            "interpreted_target": nearest_enemy.name,
                            "interpretation_reason": "nearest",
                            "alternatives": [e.name for e in enemies if e.name != nearest_enemy.name][:2],
                            "options": options,
                            "action_summary": world.get_action_summary(),
                            "game_state": world.get_filtered_game_state_summary()
                        }

                    # Non-literal marshals: move toward the enemy
                    current_region = world.get_region(marshal.location)
                    best_next = None
                    best_distance = distance  # Current distance

                    for adjacent_name in current_region.adjacent_regions:
                        adj_distance = world.get_distance(adjacent_name, nearest_enemy.location)
                        if adj_distance < best_distance:
                            best_distance = adj_distance
                            best_next = adjacent_name

                    if best_next:
                        old_location = marshal.location
                        marshal.location = best_next
                        return {
                            "success": True,
                            "message": f"{marshal.name} advances from {old_location} to {best_next}, moving toward {nearest_enemy.name} at {nearest_enemy.location}! (Now {best_distance} region{'s' if best_distance != 1 else ''} away)"
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"{marshal.name} cannot get closer to any enemy from {marshal.location}."
                        }
            else:
                return {
                    "success": False,
                    "message": "No enemies found to attack!"
                }

        # ============================================================
        # FUZZY MATCHING: Resolve target name first
        # ============================================================

        # Try fuzzy matching for enemy marshal name first
        # Pass attacker's nation for nation-aware enemy lookup (required for enemy AI)
        enemy_by_name, enemy_error = self._fuzzy_match_enemy(target, world, marshal.nation)
        resolved_target = target

        if not enemy_by_name:
            # Not an enemy - try fuzzy matching for region names
            target_region_fuzzy, region_error = self._fuzzy_match_region(target, world)

            # If region has a suggestion, ask for confirmation
            if region_error and "Did you mean" in region_error.get("message", ""):
                return region_error

            if target_region_fuzzy:
                resolved_target = target_region_fuzzy.name
            elif enemy_error and "Did you mean" in enemy_error.get("message", ""):
                # Enemy suggestion - show it
                return enemy_error

        # ============================================================
        # EC-9: COALITION MEMBER ATTACK PREVENTION (COALITION_SPEC §11.9)
        # During coalition war, members cannot attack each other.
        # ============================================================
        if enemy_by_name:
            from backend.game_logic.coalition import is_coalition_member, is_coalition_active
            if is_coalition_active(world) and \
               is_coalition_member(marshal.nation, world) and \
               is_coalition_member(enemy_by_name.nation, world):
                return {
                    "success": False,
                    "message": f"Cannot attack {enemy_by_name.name} — {enemy_by_name.nation} is a coalition ally."
                }

        # ============================================================
        # RANGE CHECK: Verify target is within marshal's attack range
        # ============================================================

        # First, determine target location
        target_location = None

        # Check if target is an enemy marshal name
        if enemy_by_name:
            target_location = enemy_by_name.location
        else:
            # Use resolved target name for region lookup
            target_region = world.get_region(resolved_target)
            if target_region:
                target_location = resolved_target

        # If we found a valid target location, check range
        if target_location:
            distance = world.get_distance(marshal.location, target_location)

            if distance > marshal.movement_range:
                # ARTILLERY: Block PURSUE auto-promotion — artillery can't chase
                if getattr(marshal, 'artillery', False):
                    return {
                        "success": False,
                        "message": f"Target out of range. {marshal.name}'s artillery can only engage adjacent regions."
                    }

                # OUT OF RANGE — auto-upgrade to strategic PURSUE if targeting enemy marshal
                is_player_nation = marshal.nation == world.player_nation
                if enemy_by_name and is_player_nation:
                    # Pre-check: strategic commands cost 2 AP (1 for literal)
                    is_literal = getattr(marshal, 'personality', '') == 'literal'
                    strategic_cost = 1 if is_literal else 2
                    if world.actions_remaining < strategic_cost:
                        return {
                            "success": False,
                            "message": f"Not enough actions for a strategic pursuit! Need {strategic_cost}, have {world.actions_remaining}.",
                            "actions_remaining": int(world.actions_remaining),
                            "action_summary": world.get_action_summary()
                        }
                    print(f"[ATTACK->PURSUE] {marshal.name}: {target} out of range (distance {distance}), auto-upgrading to PURSUE")
                    pursue_parsed = {
                        "success": True,
                        "command": {
                            "marshal": marshal.name,
                            "action": "attack",
                            "target": enemy_by_name.name,
                            "target_type": "marshal",
                        },
                        "is_strategic": True,
                        "strategic_type": "PURSUE",
                        "attack_on_arrival": True,  # Player said "attack", not "pursue"
                        "auto_upgrade": False,  # Same cost as explicit strategic command
                        "raw_input": f"{marshal.name} attack {target}",
                        "strategic_score": 60,
                        "ambiguity": 15,
                    }
                    return self._execute_strategic_command(pursue_parsed, pursue_parsed["command"], game_state)

                # Non-enemy or AI marshal — provide helpful error
                marshal_type = "cavalry" if marshal.movement_range == 2 else "infantry"

                # Find closer targets within range
                # Use nation-aware enemy lookup (required for enemy AI)
                # FOG-AWARE (Session 37): Only suggest visible enemies for player
                nearby_targets = []
                is_player = marshal.nation == world.player_nation
                for enemy in world.get_enemies_of_nation(marshal.nation):
                    if enemy.strength > 0:
                        enemy_distance = world.get_distance(marshal.location, enemy.location)
                        if enemy_distance <= marshal.movement_range:
                            # Fog check: player only sees PARTIAL+ enemies
                            if is_player and hasattr(world, 'get_region_intel'):
                                from backend.models.intel import FULL, PARTIAL
                                intel = world.get_region_intel(enemy.location)
                                if intel.visibility not in (FULL, PARTIAL):
                                    continue
                            nearby_targets.append(f"{enemy.name} at {enemy.location} ({enemy_distance} region{'s' if enemy_distance != 1 else ''} away)")

                error_msg = f"{marshal.name} cannot reach {target} from {marshal.location}! "
                error_msg += f"Range: {marshal.movement_range}, Distance: {distance}"

                suggestion = None
                if nearby_targets:
                    suggestion = f"Targets in range: {', '.join(nearby_targets)}"
                else:
                    suggestion = f"No enemies within range. Try 'move to {target_location}' to get closer first"

                return {
                    "success": False,
                    "message": error_msg,
                    "suggestion": suggestion
                }

        # ============================================================
        # NORMAL ATTACK LOGIC (Range check passed)
        # ============================================================

        # ════════════════════════════════════════════════════════════
        # ENGAGEMENT CHECK: Cannot attack elsewhere if enemy in your region
        # Same rule as movement - must deal with engaged enemies first
        # ════════════════════════════════════════════════════════════
        marshals_here = world.get_marshals_in_region(marshal.location)
        enemies_here = [m for m in marshals_here if m.nation != marshal.nation and m.strength > 0]

        if enemies_here:
            # Check if target is in a DIFFERENT region
            # (Attacking enemy in same region is allowed - that's fighting them!)
            target_in_same_region = False
            for enemy in enemies_here:
                if enemy.name.lower() == target.lower() or enemy.location == resolved_target:
                    target_in_same_region = True
                    break

            if not target_in_same_region:
                enemy_names = [e.name for e in enemies_here]
                return {
                    "success": False,
                    "message": f"Cannot attack elsewhere while engaged with enemy forces! {', '.join(enemy_names)} must be dealt with first.",
                    "engaged_with": enemy_names,
                    "suggestion": f"Attack {enemies_here[0].name} in {marshal.location} first"
                }

        # Find enemy marshal - either by name or at target location
        # Use nation-aware lookups (required for enemy AI to attack player marshals)
        enemy_marshal = None

        # Check if target is an enemy marshal name (use original target for enemy names)
        enemy_marshal = world.get_enemy_by_name_for_nation(target, marshal.nation)

        if not enemy_marshal:
            # Check if target is a region with enemies (use resolved_target for regions)
            enemy_marshal = world.get_enemy_at_location_for_nation(resolved_target, marshal.nation)

        # ════════════════════════════════════════════════════════════
        # AUTO WAR DECLARATION (Phase 8 Session 2)
        # If attacking a nation we're not at WAR with, auto-declare war
        # before proceeding. Costs 1 DP, applies relation penalties.
        # ════════════════════════════════════════════════════════════
        if enemy_marshal and not world.is_at_war(marshal.nation, enemy_marshal.nation):
            from backend.game_logic.diplomacy import declare_war
            war_result = declare_war(world, marshal.nation, enemy_marshal.nation)
            if war_result.get("success"):
                # Deduct DP for player
                if marshal.nation == world.player_nation:
                    dp = getattr(world, 'diplomatic_points', 0)
                    world.diplomatic_points = max(0, dp - war_result.get("dp_cost", 1))
                # War declared — continue with attack

        # ════════════════════════════════════════════════════════════
        # BOMBARDMENT: Region-name targeting selects strongest enemy (§4.4)
        # When artillery bombards a region name, pick the strongest enemy
        # marshal as the primary target. Other marshals take collateral.
        # ════════════════════════════════════════════════════════════
        if (enemy_marshal and not enemy_by_name
                and getattr(marshal, 'artillery', False)
                and marshal.location != (enemy_marshal.location or "")):
            all_enemies_at_target = [
                m for m in world.marshals.values()
                if m.location == resolved_target
                and m.nation != marshal.nation
                and m.strength > 0
                and not getattr(m, 'broken', False)
            ]
            if len(all_enemies_at_target) > 1:
                enemy_marshal = max(all_enemies_at_target, key=lambda m: m.strength)

        if not enemy_marshal:
            # No enemy found - target should already be resolved, get the region
            target_region = world.get_region(resolved_target)

            if target_region:
                # Check if already controlled
                # ENEMY AI FIX: Use attacker's nation, not hardcoded player_nation
                if target_region.controller == marshal.nation:
                    return {
                        "success": False,
                        "message": f"{resolved_target} is already controlled by {marshal.nation}"
                    }

                # Auto-war-declaration for undefended territory (Phase 8 Session 2)
                if target_region.controller and not world.is_at_war(marshal.nation, target_region.controller):
                    from backend.game_logic.diplomacy import declare_war, can_enter_territory
                    if not can_enter_territory(world, marshal.nation, target_region.controller):
                        war_result = declare_war(world, marshal.nation, target_region.controller)
                        if war_result.get("success") and marshal.nation == world.player_nation:
                            dp = getattr(world, 'diplomatic_points', 0)
                            world.diplomatic_points = max(0, dp - war_result.get("dp_cost", 1))

                # Check for any defenders (marshals from nations other than attacker)
                defenders = [m for m in world.marshals.values()
                            if m.location == resolved_target and m.strength > 0 and m.nation != marshal.nation]

                if not defenders:
                    # ════════════════════════════════════════════════════════════
                    # GARRISON DEFENSE: Garrison fights attackers when no marshal
                    # is present. Capital garrisons collapse below 5k. Detachment
                    # garrisons (garrison_detachment) fight to destruction.
                    # ════════════════════════════════════════════════════════════
                    garrison_fights = False
                    if target_region.garrison_strength > 0 and target_region.controller != marshal.nation:
                        if target_region.garrison_detachment:
                            # Detachment garrisons always fight (no collapse threshold)
                            garrison_fights = True
                        elif target_region.garrison_strength >= 5000:
                            # Capital garrisons fight above 5k
                            garrison_fights = True

                    if garrison_fights:
                        garrison_result = self._resolve_garrison_combat(
                            marshal, target_region, world, game_state)
                        if drill_cancelled_message:
                            garrison_result["message"] = drill_cancelled_message + garrison_result["message"]
                        return garrison_result

                    # If garrison exists but below collapse threshold, it collapses — clear it
                    if target_region.garrison_strength > 0 and target_region.controller != marshal.nation:
                        target_region.garrison_strength = 0
                        target_region.garrison_detachment = False

                    # UNDEFENDED - Capture attempt (may start occupation if fortified)
                    old_controller = target_region.controller
                    old_location = marshal.location

                    # Move attacker to captured region
                    marshal.move_to(resolved_target)

                    # Movement attrition (Phase 6.2.F)
                    attrition_info = self._calculate_movement_attrition(marshal, resolved_target, world)

                    # Attempt capture (Phase 6.2.F: contested capture)
                    capture_result = self._attempt_region_capture(
                        marshal, resolved_target, world, game_state, had_garrison=False)

                    capture_message = f"{marshal.name} marches from {old_location} into {resolved_target} unopposed!"
                    if attrition_info["total_losses"] > 0:
                        capture_message += f" ({attrition_info['march_losses']:,} lost to march"
                        if attrition_info.get("depot_bonus"):
                            capture_message += " — forward supply lines reduce losses"
                        if attrition_info["harassment_losses"] > 0:
                            capture_message += f", {attrition_info['harassment_losses']:,} to enemy harassment"
                        capture_message += ")"

                    if capture_result["occupation_started"]:
                        capture_message += f" {capture_result['message']}"
                        if drill_cancelled_message:
                            capture_message = drill_cancelled_message + capture_message
                        return {
                            "success": True,
                            "message": capture_message,
                            "occupation_started": True,
                            "events": [{
                                "type": "occupation_started",
                                "marshal": marshal.name,
                                "region": resolved_target,
                                "turns_required": capture_result["turns_required"],
                            }],
                            "new_state": game_state
                        }

                    # Instant capture
                    capture_message += f" Captured: {old_controller} → {marshal.nation}"
                    if drill_cancelled_message:
                        capture_message = drill_cancelled_message + capture_message

                    conquest_event = {
                        "type": "conquest",
                        "marshal": marshal.name,
                        "region": resolved_target,
                        "unopposed": True,
                    }
                    if capture_result.get("capture_choice"):
                        conquest_event["capture_choice"] = capture_result["capture_choice"]
                    result = {
                        "success": True,
                        "message": capture_message,
                        "events": [conquest_event],
                        "new_state": game_state
                    }

                    if marshal.nation == world.player_nation and world.pending_capture_choice:
                        result["message"] += "\nYour forces have taken the region! How shall they behave?"
                        result["pending_capture_choice"] = True
                        result["capture_data"] = world.pending_capture_choice

                    return result

            # If region not found, return error
            if not target_region:
                return {
                    "success": False,
                    "message": f"Unknown target: {target}"
                }

            # Try to find nearest enemy as last resort
            nearest = world.find_nearest_enemy(marshal.location)
            if nearest:
                enemy_marshal, distance = nearest
                if distance > 2:
                    return {
                        "success": False,
                        "message": f"No enemy found at {target}. Nearest enemy is {enemy_marshal.name} at {enemy_marshal.location} ({distance} regions away).",
                        "suggestion": f"Try: 'Attack {enemy_marshal.name}' or move closer first"
                    }
            else:
                return {
                    "success": False,
                    "message": "No enemies found! You may have won the campaign.",
                }

        if not enemy_marshal or enemy_marshal.strength <= 0:
            return {
                "success": False,
                "message": f"Cannot find living enemy: {resolved_target}"
            }

        # ════════════════════════════════════════════════════════════
        # BOMBARDMENT ROUTING (§3): Artillery in different region → bombardment
        # Same-region artillery combat still uses full resolve_battle().
        # ════════════════════════════════════════════════════════════
        if (getattr(marshal, 'artillery', False)
                and marshal.location != enemy_marshal.location):
            bombard_result = self._execute_bombardment(
                marshal, enemy_marshal, world, game_state)
            if drill_cancelled_message:
                bombard_result["message"] = drill_cancelled_message + bombard_result["message"]
            if counter_punch_message:
                bombard_result["message"] = counter_punch_message + bombard_result["message"]
            if is_counter_punch:
                bombard_result["free_action"] = True
                bombard_result["counter_punch_used"] = True
            return bombard_result

        # ============================================================
        # ALLY COVERS RETREAT SYSTEM: If target retreated this turn,
        # an ally in the same region can step in to defend
        # ============================================================
        covering_message = ""
        original_target = None  # Track original target for messaging

        if getattr(enemy_marshal, 'retreated_this_turn', False):
            # Target retreated this turn - check for covering allies
            covering_candidates = [
                m for m in world.marshals.values()
                if m.location == enemy_marshal.location  # Same region
                and m.nation == enemy_marshal.nation     # Same nation
                and m.name != enemy_marshal.name         # Not the target itself
                and m.strength > 0                       # Has troops
                and not getattr(m, 'retreated_this_turn', False)  # Didn't also retreat
            ]

            if covering_candidates:
                # Pick the strongest ally to cover
                covering_ally = max(covering_candidates, key=lambda m: m.strength)
                original_target = enemy_marshal
                enemy_marshal = covering_ally  # Swap defender

                covering_message = (
                    f"🛡️ {covering_ally.name} steps forward to cover {original_target.name}'s retreat! "
                    f"\"{original_target.name} is in no condition to fight - I'll handle this!\"\n\n"
                )
                print(f"  [ALLY COVER] {covering_ally.name} covers for retreating {original_target.name}")
            else:
                # No covering ally - target is EXPOSED
                covering_message = (
                    f"⚠️ {enemy_marshal.name} is EXPOSED! (Just retreated, no ally to cover)\n\n"
                )
                print(f"  [EXPOSED] {enemy_marshal.name} retreated and has no cover!")

        # ============================================================
        # FLANKING SYSTEM (Phase 2.5): Record attack origin BEFORE combat
        # ============================================================
        origin_region = marshal.location  # Capture origin BEFORE any movement
        target_location = enemy_marshal.location

        # Record this attack for flanking calculation
        world.record_attack(marshal.name, origin_region, target_location)

        # Calculate flanking bonus based on all attacks this turn
        flanking_info = world.calculate_flanking_bonus(target_location)
        flanking_bonus = flanking_info["bonus"]

        # Generate flanking message if applicable
        flanking_message = world.get_flanking_message(marshal.name, origin_region, target_location)

        # ════════════════════════════════════════════════════════════
        # CAVALRY CHARGE (Phase 2.8): Ney can attack from 2 regions away
        # Cannot leapfrog over enemies - must engage them first
        # ════════════════════════════════════════════════════════════
        cavalry_charge_message = ""
        attack_distance = world.get_distance(origin_region, target_location)
        is_cavalry = getattr(marshal, 'cavalry', False)

        if is_cavalry and attack_distance == 2:
            # Find the middle region for the charge
            middle_regions = []
            current_region = world.get_region(origin_region)
            for adj in current_region.adjacent_regions:
                if world.get_distance(adj, target_location) == 1:
                    middle_regions.append(adj)

            # CHECK FOR ENEMIES IN MIDDLE REGION - Cannot leapfrog!
            if middle_regions:
                for middle in middle_regions:
                    enemies_in_middle = [
                        m for m in world.get_marshals_in_region(middle)
                        if m.nation != marshal.nation and m.strength > 0
                    ]
                    if enemies_in_middle:
                        blocking_enemy = enemies_in_middle[0]
                        return {
                            "success": False,
                            "message": f"Cannot charge through {middle} - {blocking_enemy.name} blocks the path! Engage them first.",
                            "blocked_by": blocking_enemy.name,
                            "blocking_region": middle,
                            "suggestion": f"Attack {blocking_enemy.name} at {middle} first"
                        }

                middle = middle_regions[0]
                # Transit intel: cavalry charging through middle region gets PARTIAL snapshot
                if marshal.nation == world.player_nation:
                    world.update_intel_from_transit(middle, world.current_turn)
                cavalry_charge_message = f"🐴 {marshal.name}'s cavalry thunders across {middle} to strike! (Cavalry Charge: 2-region attack)\n"
            else:
                cavalry_charge_message = f"🐴 {marshal.name}'s cavalry charges across the battlefield! (Cavalry Charge: 2-region attack)\n"

        # Read terrain from defender's region (defender chose this ground)
        defender_region = world.get_region(enemy_marshal.location)
        battle_terrain = defender_region.terrain if defender_region else "plains"

        # Fortification bonus (Phase 6.2.E): defender gets +25% if region has functional fortification
        fort_bonus = 0.0
        if defender_region and defender_region.has_building("fortification"):
            fort_bonus = 0.25

        # Capture pre-battle strengths for war damage threshold (Phase 6.2.C)
        pre_battle_attacker_strength = marshal.strength
        pre_battle_defender_strength = enemy_marshal.strength
        battle_region_name = enemy_marshal.location

        # ════════════════════════════════════════════════════════════
        # REINFORCEMENT (Phase 7, Session 61a): Adjacent marshals
        # physically relocate to battle region before combat.
        # Must run BEFORE coordination context (A-C2 ordering).
        # ════════════════════════════════════════════════════════════
        attacker_reinforcements = self._calculate_reinforcements(
            marshal, enemy_marshal, battle_region_name, marshal.nation, world
        )
        defender_reinforcements = self._calculate_reinforcements(
            enemy_marshal, marshal, battle_region_name, enemy_marshal.nation, world
        )

        # Process arrivals — BEFORE coordination context (A-C2)
        arrived_names = set()
        # Artillery that reinforced but stayed in adjacent position (Gate 4 fix)
        artillery_reinforced_adjacent = []
        # Track pre-arrival locations for retreat-on-loss (Gate 4: spec says
        # "reinforcer retreats with primary if battle lost")
        reinforcer_origin = {}  # marshal_name -> original_location
        for side_primary, results_list in [(marshal, attacker_reinforcements),
                                           (enemy_marshal, defender_reinforcements)]:
            for result in results_list:
                if result["arrived"]:
                    arriving = world.marshals.get(result["marshal"])
                    if arriving:
                        # Record arrived_via_support BEFORE any changes (A-C2)
                        order = getattr(arriving, 'strategic_order', None)
                        result["arrived_via_support"] = (
                            order is not None
                            and order.command_type == "SUPPORT"
                            and order.target == side_primary.name
                        )
                        # Save origin for retreat-on-loss BEFORE relocation
                        reinforcer_origin[arriving.name] = arriving.location
                        # Physical relocation — artillery stays in adjacent position
                        # (Gate 4: artillery reinforces via fire support, not advance)
                        if getattr(arriving, 'artillery', False):
                            # Artillery provides coordination bonus from adjacent
                            # position but does NOT advance to front line.
                            # NOT added to arrived_names — artillery remains
                            # countable as an adjacent ally for +2% attack bonus.
                            artillery_reinforced_adjacent.append(arriving)
                        else:
                            arriving.location = battle_region_name
                            arrived_names.add(arriving.name)
                        arriving.reinforced_this_turn = True
                        # Clear path (now invalid) but DO NOT clear strategic_order yet (A-C2)
                        if arriving.strategic_order:
                            arriving.strategic_order.path = []

        # ════════════════════════════════════════════════════════════
        # COORDINATION (Phase 7, Session 57): Combined arms detection
        # Calculate for BOTH sides independently (A-C3)
        # S61a: Pass reinforcement_results for A-C2 dedicated support,
        # exclude arrived names from adjacent count.
        # ════════════════════════════════════════════════════════════
        attacker_coord = self._calculate_coordination_context(
            marshal, world,
            reinforcement_results=attacker_reinforcements,
            exclude_from_adjacent=arrived_names)
        self._calculate_coordination_context(
            enemy_marshal, world,
            reinforcement_results=defender_reinforcements,
            exclude_from_adjacent=arrived_names)

        # ════════════════════════════════════════════════════════════
        # [S62] CASUALTY DISTRIBUTION: Build participant lists BEFORE
        # clearing strategic orders (so SUPPORT detection works for D3).
        # ════════════════════════════════════════════════════════════
        atk_participants = self._get_casualty_participants(
            marshal, battle_region_name, marshal.nation, world)
        def_participants = self._get_casualty_participants(
            enemy_marshal, battle_region_name, enemy_marshal.nation, world)

        # Gate 4: Artillery that reinforced from adjacent (didn't relocate)
        # must still participate in casualty distribution
        for art in artillery_reinforced_adjacent:
            if art.nation == marshal.nation and art not in atk_participants:
                atk_participants.append(art)
            elif art.nation == enemy_marshal.nation and art not in def_participants:
                def_participants.append(art)

        is_coordinated_battle = (len(atk_participants) >= 2 or len(def_participants) >= 2)

        # NOTE: Strategic order clearing for arrived reinforcements is DEFERRED
        # until after process_battle_relationships() so Hostile+SUPPORT marshals
        # are correctly detected as Participating in relationship checks (W-1 fix).

        # Coordination preview removed — Berthier's narrative observation
        # handles coordination storytelling; detailed numbers deferred to
        # Battle History screen (Phase 8.5).

        # ════════════════════════════════════════════════════════════
        # ARTILLERY OVERWATCH (Session 68): Enemy artillery in defender's
        # region passively debuffs all attackers by -3% per gun.
        # Must run BEFORE resolve_battle so penalty applies to combat.
        # Overwatch is NOT coordination — does not count toward cap.
        # Does NOT apply to bombardment (ranged fire, separate path).
        # ════════════════════════════════════════════════════════════
        overwatch_count = self._calculate_overwatch(
            marshal, atk_participants, battle_region_name, world)

        # ════════════════════════════════════════════════════════════
        # SUPPORT AUTO-BOMBARDMENT (Session 68): Artillery on SUPPORT
        # targeting the attacker fires preparatory bombardment BEFORE
        # resolve_battle(). Defender takes damage first.
        # Does NOT fire on defensive battles (only when supported
        # marshal is the ATTACKER). Does NOT consume player AP.
        # ════════════════════════════════════════════════════════════
        auto_bombardment_messages = []
        auto_bombardment_results = []
        support_bombardment_total_damage = 0

        for m in list(world.marshals.values()):
            if m.nation != marshal.nation:
                continue
            if not getattr(m, 'artillery', False):
                continue
            order = getattr(m, 'strategic_order', None)
            if order is None or order.command_type != "SUPPORT" or order.target != marshal.name:
                continue
            # Eligibility checks
            if getattr(m, 'moved_this_turn', False):
                continue
            if getattr(m, 'bombardments_this_turn', 0) >= 2:
                continue
            if m.strength <= 0:
                continue
            if getattr(m, 'broken', False):
                continue
            if getattr(m, 'retreated_this_turn', False):
                continue
            if getattr(m, 'retreat_recovery', 0) > 0:
                continue
            # Must be adjacent to or co-located with battle region
            m_region = world.get_region(m.location)
            if m.location != battle_region_name:
                if not m_region or battle_region_name not in m_region.adjacent_regions:
                    continue

            # Fire auto-bombardment against defender
            print(f"  [AUTO-BOMBARD] {m.name} (SUPPORT {marshal.name}) fires on {enemy_marshal.name}")
            bombard_result = self._execute_bombardment(m, enemy_marshal, world, game_state)

            if bombard_result.get("success"):
                auto_bombardment_results.append(bombard_result)
                br = bombard_result.get("bombardment_result", {})
                def_cas = br.get("defender", {}).get("casualties", 0)
                support_bombardment_total_damage += def_cas
                auto_bombardment_messages.append(
                    f"Artillery support: {m.name}'s guns bombard {enemy_marshal.name}'s position! "
                    f"({def_cas:,} casualties)"
                )

                # Fog of war: auto-bombardment from adjacent region gives
                # defender PARTIAL intel on artillery's source region
                if (m.location != battle_region_name
                        and enemy_marshal.nation == getattr(world, 'player_nation', 'France')):
                    world.update_intel_from_transit(m.location, world.current_turn)

                # Early exit: defender destroyed by bombardment
                if enemy_marshal.strength <= 0:
                    print(f"  [AUTO-BOMBARD] Defender {enemy_marshal.name} destroyed by bombardment!")
                    break

        # ════════════════════════════════════════════════════════════
        # DEAD-DEFENDER CHECK: If auto-bombardment killed the defender,
        # skip resolve_battle entirely. Attacker wins with 0 casualties.
        # ════════════════════════════════════════════════════════════
        if enemy_marshal.strength <= 0 and auto_bombardment_results:
            # Clear coordination + overwatch fields before returning
            involved_regions = {marshal.location, battle_region_name}
            self._clear_coordination_fields(involved_regions, world)

            # Remove destroyed defender
            world.marshals.pop(enemy_marshal.name, None)

            # Advance attacker if not artillery
            advance_msg = ""
            if not getattr(marshal, 'artillery', False) and marshal.location != battle_region_name:
                marshal.move_to(battle_region_name)
                advance_msg = f" {marshal.name} advances into {battle_region_name}."

            # Attempt capture
            conquest_msg = ""
            target_region = world.get_region(battle_region_name)
            if (target_region and target_region.controller != marshal.nation
                    and not getattr(marshal, 'artillery', False)):
                remaining_defenders = [
                    m for m in world.marshals.values()
                    if m.location == battle_region_name and m.strength > 0 and m.nation != marshal.nation
                ]
                if not remaining_defenders:
                    capture_result = self._attempt_region_capture(
                        marshal, battle_region_name, world, game_state, had_garrison=True)
                    if capture_result.get("captured"):
                        conquest_msg = f" {battle_region_name} captured by {marshal.nation}!"

            preamble = "\n".join(auto_bombardment_messages)
            main_msg = (
                f"The preparatory bombardment destroyed {enemy_marshal.name}. "
                f"{marshal.name} advances unopposed."
            )

            # Fog of War: battle visibility
            world.update_intel_from_battle(battle_region_name, world.current_turn)

            result = {
                "success": True,
                "action": "attack",
                "message": f"{preamble}\n\n{main_msg}{advance_msg}{conquest_msg}",
                "auto_bombardment": True,
                "auto_bombardment_results": [
                    r.get("bombardment_result", {}) for r in auto_bombardment_results
                ],
                "events": [{
                    "type": "battle",
                    "attacker": {"name": marshal.name},
                    "defender": {"name": enemy_marshal.name},
                    "location": battle_region_name,
                    "outcome": "attacker_victory",
                    "auto_bombardment_kill": True,
                }],
                "new_state": game_state,
            }
            if counter_punch_message:
                result["message"] = counter_punch_message + result["message"]
            if drill_cancelled_message:
                result["message"] = drill_cancelled_message + result["message"]
            if covering_message:
                result["message"] = covering_message + result["message"]
            if cavalry_charge_message:
                result["message"] = cavalry_charge_message + result["message"]
            return result

        # ════════════════════════════════════════════════════════════
        # RESOLVE COMBAT
        # Solo battles (1v1): apply_casualties=True — zero behavior change.
        # Coordinated battles (2+ on either side): apply_casualties=False,
        # caller distributes among participants (Session 62).
        # ════════════════════════════════════════════════════════════
        atk_distribution = {}  # Per-marshal casualty map (populated in coordinated path)
        if is_coordinated_battle:
            battle_result = self.combat_resolver.resolve_battle(
                attacker=marshal,
                defender=enemy_marshal,
                terrain=battle_terrain,
                flanking_bonus=flanking_bonus,
                flanking_message=flanking_message,
                fortification_bonus=fort_bonus,
                apply_casualties=False,
            )

            # Distribute raw casualties proportionally among participants
            atk_distribution = self._distribute_casualties(
                battle_result["attacker_raw_casualties"], atk_participants)
            def_distribution = self._distribute_casualties(
                battle_result["defender_raw_casualties"], def_participants)

            outcome = battle_result["raw_outcome"]
            atk_won = outcome in ("attacker_victory", "attacker_tactical_victory")
            atk_lost = outcome in ("defender_victory", "defender_tactical_victory", "mutual_destruction")
            def_won = outcome in ("defender_victory", "defender_tactical_victory")

            # ── Apply per-participant effects (C1 caller responsibilities) ──

            # ATTACKER SIDE
            for p in atk_participants:
                p.take_casualties(atk_distribution.get(p.name, 0))
                p.adjust_morale(battle_result["attacker_morale_delta"])  # UNIFORM morale
                if atk_won:
                    p.battles_won += 1
                elif atk_lost:
                    p.battles_lost += 1

            # DEFENDER SIDE
            for p in def_participants:
                p.take_casualties(def_distribution.get(p.name, 0))
                p.adjust_morale(battle_result["defender_morale_delta"])  # UNIFORM morale
                if def_won:
                    p.battles_won += 1
                elif atk_won or outcome == "mutual_destruction":
                    p.battles_lost += 1

            # ── PRIMARY-ONLY EFFECTS ──

            # Recklessness: primary attacker only (N1)
            # Note: glorious_charge paths redirect to _execute_glorious_charge before
            # reaching this code, so recklessness always applies here.
            if hasattr(marshal, 'is_reckless_cavalry') and marshal.is_reckless_cavalry:
                if atk_won:
                    marshal._increment_recklessness()
                elif atk_lost:
                    marshal.reset_recklessness()

            # Counter-punch: primary defender only (N1)
            if outcome in ("defender_victory", "defender_tactical_victory", "stalemate"):
                if getattr(enemy_marshal, 'personality', '') == 'cautious':
                    enemy_marshal.counter_punch_available = True
                    enemy_marshal.counter_punch_turns = 2

            # Counter-Punch Mastery (Davout ability): primary defender only
            if (enemy_marshal.strength > 0
                    and hasattr(enemy_marshal, 'ability')
                    and enemy_marshal.ability.get("name") == "Counter-Punch Mastery"):
                enemy_marshal.counter_punch_ready = True

            # ── Update battle_result with post-distribution state ──
            # Downstream code reads these fields for movement, conquest, retreat.
            battle_result["attacker"]["remaining"] = int(marshal.strength)
            battle_result["attacker"]["morale"] = int(marshal.morale)
            battle_result["defender"]["remaining"] = int(enemy_marshal.strength)
            battle_result["defender"]["morale"] = int(enemy_marshal.morale)

            # Set forced_retreat flags per-primary for _handle_forced_retreat
            FORCED_RETREAT_THRESHOLD = 25
            battle_result["attacker"]["forced_retreat"] = (
                marshal.strength > 0 and marshal.morale <= FORCED_RETREAT_THRESHOLD
            )
            battle_result["defender"]["forced_retreat"] = (
                enemy_marshal.strength > 0 and enemy_marshal.morale <= FORCED_RETREAT_THRESHOLD
            )

            # Set notification flags for _process_combat_notifications
            battle_result["counter_punch_earned"] = bool(
                getattr(enemy_marshal, 'counter_punch_available', False)
                and getattr(enemy_marshal, 'personality', '') == 'cautious'
                and outcome in ("defender_victory", "defender_tactical_victory", "stalemate")
            )
            battle_result["counter_punch_mastery_earned"] = bool(
                getattr(enemy_marshal, 'counter_punch_ready', False)
                and hasattr(enemy_marshal, 'ability')
                and enemy_marshal.ability.get("name") == "Counter-Punch Mastery"
            )

            # Pursuit damage: primary attacker vs primary defender only
            if battle_result["defender"]["forced_retreat"] and atk_won:
                attacker_ability_name = ""
                if hasattr(marshal, 'ability'):
                    attacker_ability_name = marshal.ability.get("name", "")

                pursuit_damage = 0
                pursuit_message = None
                if attacker_ability_name == "Pursuit Master" and getattr(marshal, 'cavalry', False):
                    pursuit_damage = 5000
                    pursuit_message = (
                        f"🐴 {marshal.name}'s '{marshal.ability['name']}' — "
                        f"cavalry runs down the retreating enemy! (+{pursuit_damage:,} pursuit casualties)"
                    )
                elif attacker_ability_name == "Vorwärts!":
                    pursuit_damage = 3000
                    pursuit_message = (
                        f"⚔️ {marshal.name}'s '{marshal.ability['name']}' — "
                        f"relentless pursuit inflicts extra casualties! (+{pursuit_damage:,} pursuit casualties)"
                    )

                if pursuit_damage > 0 and enemy_marshal.strength > 0:
                    old_strength = enemy_marshal.strength
                    enemy_marshal.strength = max(1000, enemy_marshal.strength - pursuit_damage)
                    actual_pursuit = old_strength - enemy_marshal.strength
                    if actual_pursuit > 0:
                        battle_result["pursuit_damage"] = int(actual_pursuit)
                        battle_result["pursuit_message"] = pursuit_message

            # Store distribution info for event logging
            battle_result["casualty_distribution"] = {
                "attacker_side": atk_distribution,
                "defender_side": def_distribution,
            }

        else:
            # Solo battle — existing behavior unchanged (apply_casualties=True default)
            battle_result = self.combat_resolver.resolve_battle(
                attacker=marshal,
                defender=enemy_marshal,
                terrain=battle_terrain,
                flanking_bonus=flanking_bonus,
                flanking_message=flanking_message,
                fortification_bonus=fort_bonus,
            )

        # ════════════════════════════════════════════════════════════
        # COORDINATION CONTEXT FOR BATTLE REPORT (Session 65)
        # Inject data before clearing transient fields so
        # _pick_observation() can use coordination-specific priorities.
        # ════════════════════════════════════════════════════════════
        coord_context = {
            "type_count": attacker_coord.get("type_count", 0),
            "hostile_forced_participants": [],
            "hostile_refused": [],
            "devoted_allies": [],
        }
        # Classify our (attacker-side) participants by relationship
        if is_coordinated_battle:
            for p in atk_participants:
                if p.name == marshal.name:
                    continue
                rel = p.get_relationship(marshal.name)
                if rel == -2:
                    # Hostile — check for SUPPORT order
                    order = getattr(p, 'strategic_order', None)
                    has_support = (
                        order is not None
                        and order.command_type == "SUPPORT"
                        and order.target == marshal.name
                    )
                    if has_support:
                        coord_context["hostile_forced_participants"].append(p.name)
                    else:
                        coord_context["hostile_refused"].append(p.name)
                elif rel == 2:
                    coord_context["devoted_allies"].append(p.name)
        battle_result["coordination_context"] = coord_context
        battle_result["reinforcement_results_for_report"] = {
            "attacker": attacker_reinforcements,
            "defender": defender_reinforcements,
        }
        # Session 68: Inject auto-bombardment and overwatch data for observation re-pick
        battle_result["support_bombardment_total_damage"] = support_bombardment_total_damage
        battle_result["overwatch_count"] = overwatch_count

        # Clear coordination transient fields (D5 + X1)
        involved_regions = {marshal.location}
        if enemy_marshal.strength > 0:
            involved_regions.add(enemy_marshal.location)
        involved_regions.add(battle_region_name)
        self._clear_coordination_fields(involved_regions, world)

        # Log battle event
        self._log_battle_event(battle_result, battle_region_name, world)

        # Combat notifications (counter-punch earned, drill cancelled)
        self._process_combat_notifications(battle_result, marshal, enemy_marshal, world)

        # ════════════════════════════════════════════════════════════
        # WIN/LOSS RELATIONSHIP FORMULA (Session 64)
        # Fires after resolve_battle with 2+ same-nation participants.
        # Ordered pairs per D4, strict >50 threshold per M2.
        # Must run BEFORE destruction check so all participants
        # are still in world.marshals.
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.relationship import process_battle_relationships
        relationship_changes = process_battle_relationships(
            marshal, enemy_marshal, battle_result, battle_region_name, world
        )
        for rc in relationship_changes:
            world.log_event({
                "type": "relationship_change",
                "marshal": rc["marshal"],
                "toward": rc["toward"],
                "change": rc["change"],
                "new_value": rc["new_value"],
                "new_label": rc["new_label"],
                "direction": rc["direction"],
                "nation": rc["nation"],
                "location": battle_region_name,
            })

        # ════════════════════════════════════════════════════════════
        # RE-PICK OBSERVATION WITH COORDINATION DATA (Session 65)
        # Now that coordination_context, reinforcement data, and
        # relationship_changes are all available, re-evaluate the
        # Berthier observation. Coordination priorities (P0.5-P15)
        # may override the initial observation from resolve_battle().
        # ════════════════════════════════════════════════════════════
        battle_result["relationship_changes"] = relationship_changes
        # Session 68: inject auto-bombardment results for observation re-pick
        if auto_bombardment_results:
            battle_result["auto_bombardment_results"] = [
                r.get("bombardment_result", {}) for r in auto_bombardment_results
            ]
        if (coord_context.get("type_count", 0) >= 3
                or coord_context.get("hostile_forced_participants")
                or coord_context.get("hostile_refused")
                or coord_context.get("devoted_allies")
                or attacker_reinforcements or defender_reinforcements
                or relationship_changes
                or support_bombardment_total_damage > 0
                or overwatch_count > 0):
            from backend.game_logic.battle_report import _pick_observation
            new_observation = _pick_observation(battle_result, world.player_nation)
            if "battle_report" in battle_result:
                battle_result["battle_report"]["observation"] = new_observation
            # Also update the log event's embedded report
            if "log_battle_event" in battle_result:
                log_report = battle_result["log_battle_event"].get("battle_report")
                if log_report:
                    log_report["observation"] = new_observation

        # NOW clear strategic orders for arrived reinforcements (A-C2 step 5).
        # Deferred to here so Hostile+SUPPORT marshals participate in
        # relationship checks above (W-1 fix, Session 62 post-review).
        for results_list in [attacker_reinforcements, defender_reinforcements]:
            for result in results_list:
                if result["arrived"]:
                    arriving = world.marshals.get(result["marshal"])
                    if arriving:
                        arriving.strategic_order = None

        # Fog of War (Session 34A): Battle grants FULL visibility on battle region
        world.update_intel_from_battle(battle_region_name, world.current_turn)

        # Apply war damage + stability hit to battle region (Phase 6.2.C)
        self._apply_battle_effects_to_region(
            battle_region_name, pre_battle_attacker_strength,
            pre_battle_defender_strength, world
        )

        # V2a: Reset idle tracking on attack
        marshal.idle_turns = 0
        marshal._acted_this_turn = True

        # Record battle for cannon fire detection (hearing the guns)
        world.record_battle(target_location, marshal.name, enemy_marshal.name,
                            battle_result.get("outcome", "unknown"))

        # Record battle for diplomatic war score (Phase 8 Session 2)
        from backend.game_logic.diplomacy import record_battle as record_diplo_battle
        outcome = battle_result.get("outcome", "")
        atk_won = "attacker" in outcome and "victory" in outcome
        def_won = "defender" in outcome and "victory" in outcome
        diplo_winner = marshal.nation if atk_won else (enemy_marshal.nation if def_won else None)
        if diplo_winner:
            record_diplo_battle(
                world,
                attacker_nation=marshal.nation,
                defender_nation=enemy_marshal.nation,
                winner_nation=diplo_winner,
                attacker_casualties=int(battle_result.get("attacker", {}).get("casualties", 0)),
                defender_casualties=int(battle_result.get("defender", {}).get("casualties", 0)),
            )

        # Check if enemy was destroyed
        enemy_destroyed = enemy_marshal.strength <= 0
        if enemy_destroyed:
            destroyed_msg = f" {enemy_marshal.name}'s army is destroyed!"
            world.marshals.pop(enemy_marshal.name, None)
        else:
            destroyed_msg = ""

        # ALSO check if attacker was destroyed
        if marshal.strength <= 0:
            world.marshals.pop(marshal.name, None)

        # ============================================================
        # FORCED RETREAT: Handle broken armies (morale <= 25%)
        # MUST happen BEFORE movement/conquest check so retreating
        # defenders don't block territory capture!
        # ============================================================
        forced_retreat_msg = self._handle_forced_retreat(
            battle_result, marshal, enemy_marshal, world
        )

        # [S62] Handle forced retreat for non-primary participants in coordinated battles
        if is_coordinated_battle:
            for p in atk_participants:
                if p.name != marshal.name and p.strength > 0 and p.morale <= 25:
                    msg = self._apply_forced_retreat_or_break(p, enemy_marshal, world)
                    if msg:
                        forced_retreat_msg += "\n" + msg
            for p in def_participants:
                if p.name != enemy_marshal.name and p.strength > 0 and p.morale <= 25:
                    msg = self._apply_forced_retreat_or_break(p, marshal, world)
                    if msg:
                        forced_retreat_msg += "\n" + msg

            # ── Gate 4: Reinforcer retreat on non-win ──
            # Reinforcers who relocated to battle region must return to
            # their origin if their side didn't win (loss OR stalemate).
            # (Morale-based retreat above handles the broken case;
            # this handles the "orderly withdrawal" case.)
            if not atk_won:
                for p in atk_participants:
                    origin = reinforcer_origin.get(p.name)
                    if (origin and p.name != marshal.name
                            and p.strength > 0
                            and not getattr(p, 'broken', False)
                            and not getattr(p, 'retreated_this_turn', False)
                            and p.location == battle_region_name):
                        p.location = origin
                        forced_retreat_msg += (
                            f"\n{p.name} withdraws to {origin} after the battle.")
            if not def_won:
                for p in def_participants:
                    origin = reinforcer_origin.get(p.name)
                    if (origin and p.name != enemy_marshal.name
                            and p.strength > 0
                            and not getattr(p, 'broken', False)
                            and not getattr(p, 'retreated_this_turn', False)
                            and p.location == battle_region_name):
                        p.location = origin
                        forced_retreat_msg += (
                            f"\n{p.name} withdraws to {origin} after the battle.")

            # Clean up destroyed non-primary participants
            for p in atk_participants + def_participants:
                if p.name not in (marshal.name, enemy_marshal.name) and p.strength <= 0:
                    world.marshals.pop(p.name, None)

        # ===== ATTACKER MOVEMENT & REGION CONQUEST LOGIC =====
        conquered = False
        conquest_msg = ""
        attacker_moved = False
        movement_msg = ""

        # Check if defender retreated/fled (even in stalemate, empty territory = advance)
        defender_fled = (
            enemy_marshal.strength > 0 and  # Defender survived
            enemy_marshal.location != target_location  # But no longer in target territory
        )

        # Move attacker to target location if:
        # 1. They won the battle (victor = attacker), OR
        # 2. Defender fled (even in stalemate, pursue into empty territory)
        victor = battle_result.get('victor')
        can_advance = (victor == marshal.name) or defender_fled

        print(f"[ATTACK MOVEMENT] Checking: victor={victor}, marshal={marshal.name}, strength={marshal.strength}")
        print(f"[ATTACK MOVEMENT] defender_fled={defender_fled}, enemy_location={enemy_marshal.location if enemy_marshal.strength > 0 else 'DESTROYED'}")
        print(f"[ATTACK MOVEMENT] marshal.location={marshal.location}, target_location={target_location}")

        # ARTILLERY: No advance on win — positional platform stays in place
        is_artillery_no_advance = getattr(marshal, 'artillery', False) and marshal.location != target_location
        if is_artillery_no_advance:
            if can_advance:
                movement_msg = (f" {marshal.name}'s bombardment forces the enemy to retreat from {target_location}. "
                                f"Region must be secured by infantry to complete the capture.")
            print(f"[ATTACK MOVEMENT] Artillery {marshal.name} stays at {marshal.location} (no advance on win)")
        elif can_advance and marshal.strength > 0 and not getattr(self, '_current_sortie', False):
            if marshal.location != target_location:
                print(f"[ATTACK MOVEMENT] MOVING {marshal.name}: {marshal.location} -> {target_location}")
                marshal.move_to(target_location)
                # Movement attrition on post-battle advance (Phase 6.2.F)
                attrition_info = self._calculate_movement_attrition(marshal, target_location, world)
                attacker_moved = True
                if defender_fled and victor != marshal.name:
                    movement_msg = f" {enemy_marshal.name} retreats! {marshal.name} pursues into {target_location}."
                else:
                    movement_msg = f" {marshal.name} advances into {target_location}."
                if attrition_info["total_losses"] > 0:
                    march_note = f" ({attrition_info['total_losses']:,} lost to march"
                    if attrition_info.get("depot_bonus"):
                        march_note += " — forward supply lines reduce losses"
                    march_note += ")"
                    movement_msg += march_note
            else:
                print("[ATTACK MOVEMENT] Already at target location, no move needed")
        else:
            print(f"[ATTACK MOVEMENT] NOT moving: can_advance={can_advance}, strength={marshal.strength}")

        # Check if territory can be captured
        # Use target_location (the region) not resolved_target (which might be marshal name)
        # ARTILLERY: Skip capture for artillery attacking from adjacent (no advance = no capture)
        target_region = world.get_region(target_location)
        if target_region and target_region.controller != marshal.nation and not is_artillery_no_advance:
            # Find all remaining defenders (marshals from nations other than attacker)
            # NOTE: This check happens AFTER forced retreats, so fled defenders aren't counted
            remaining_defenders = [
                m for m in world.marshals.values()
                if m.location == target_location and m.strength > 0 and m.nation != marshal.nation
            ]

            print(f"[CONQUEST CHECK] target_location={target_location}, controller={target_region.controller}")
            print(f"[CONQUEST CHECK] remaining_defenders={[m.name for m in remaining_defenders]}")

            # If no defenders left, attempt capture (may start occupation if fortified)
            if not remaining_defenders:
                capture_result = self._attempt_region_capture(
                    marshal, target_location, world, game_state, had_garrison=True)
                if capture_result["captured"]:
                    conquered = True
                    conquest_msg = f" {target_location} has been captured by {marshal.nation}!"
                elif capture_result["occupation_started"]:
                    conquest_msg = f" {capture_result['message']}"

        # Build message with flanking info if applicable
        flanking_prefix = ""
        if flanking_message:
            flanking_prefix = f"\n{flanking_message}\n"

        # ============================================================
        # VINDICATION SYSTEM: Resolve post-battle trust/authority
        # ============================================================
        vindication_msg = ""
        vindication_result = None

        # Determine battle outcome for vindication
        if battle_result["victor"] == marshal.name:
            battle_outcome = "victory"
        elif battle_result["victor"] == enemy_marshal.name:
            battle_outcome = "defeat"
        else:
            battle_outcome = "draw"

        # Call vindication tracker if there was a pending vindication for this marshal
        if world.vindication_tracker.has_pending(marshal.name):
            vindication_result = world.vindication_tracker.resolve_battle(
                marshal_name=marshal.name,
                result=battle_outcome,
                game_state=world
            )
            if vindication_result:
                vindication_msg = f"\n\n📜 {vindication_result['message']}"

        # NOTE: Forced retreat was already handled above (before movement/conquest check)
        # forced_retreat_msg is already set

        # ════════════════════════════════════════════════════════════
        # V2b: AUTHORITY MAJOR VICTORY / DEFEAT (+5 / -5)
        # Fires ONCE per battle (multiple criteria don't stack).
        # Runs after advance-after-win so territory capture is visible.
        # Only for player-nation battles.
        # ════════════════════════════════════════════════════════════
        player_nation = world.player_nation
        player_is_attacker = marshal.nation == player_nation
        player_is_defender = enemy_marshal.nation == player_nation if enemy_marshal.strength > 0 or enemy_destroyed else False
        # Also check original nation for destroyed marshals
        if not player_is_defender and hasattr(enemy_marshal, 'nation'):
            player_is_defender = enemy_marshal.nation == player_nation

        if player_is_attacker or player_is_defender:
            outcome = battle_result.get("raw_outcome", battle_result.get("outcome", ""))
            atk_won = "attacker" in outcome and "victory" in outcome
            def_won = "defender" in outcome and "victory" in outcome

            # Determine if player won or lost
            player_won = (player_is_attacker and atk_won) or (player_is_defender and def_won)
            player_lost = (player_is_attacker and def_won) or (player_is_defender and atk_won)

            if player_won:
                # Major victory: outnumbered win OR captured enemy capital
                outnumbered = pre_battle_attacker_strength < pre_battle_defender_strength
                if player_is_defender:
                    # Defender was outnumbered if attacker was larger
                    outnumbered = pre_battle_defender_strength < pre_battle_attacker_strength
                capital_captured = False
                if conquered:
                    target_reg = world.get_region(target_location)
                    if target_reg and getattr(target_reg, 'is_capital', False):
                        capital_captured = True
                if outnumbered or capital_captured:
                    world.authority_tracker.modify_authority(+5)

            elif player_lost:
                # Major defeat: outnumbering loss OR lost capital
                outnumbering = pre_battle_attacker_strength > pre_battle_defender_strength
                if player_is_defender:
                    # Defender was outnumbering if defender was larger
                    outnumbering = pre_battle_defender_strength > pre_battle_attacker_strength
                capital_lost = False
                target_reg = world.get_region(target_location)
                if target_reg and getattr(target_reg, 'is_capital', False):
                    if target_reg.controller != player_nation:
                        capital_lost = True
                if outnumbering or capital_lost:
                    world.authority_tracker.modify_authority(-5)

        # ════════════════════════════════════════════════════════════
        # COALITION: Threat + war exhaustion from battle (Session 7)
        # France wins: +3. Decisive: +5 additional. Capital: +15.
        # War exhaustion: +casualties//1000 (cap 20) for losing nation.
        # Coalition shock: +5 WE to other members on decisive defeat.
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.coalition import (
            add_threat, add_war_exhaustion_from_battle, add_coalition_shock
        )
        france = world.player_nation
        atk_cas = int(battle_result.get("attacker_casualties", 0))
        def_cas = int(battle_result.get("defender_casualties", 0))
        total_cas = atk_cas + def_cas

        if battle_result.get("victor") == marshal.name and marshal.nation == france:
            # France won as attacker
            add_threat(world, 3, "battle_win")
            # Decisive: ratio > 2:1 AND total casualties > 10,000
            if def_cas > 0 and atk_cas > 0:
                ratio = def_cas / atk_cas if atk_cas > 0 else 999
            elif def_cas > 0:
                ratio = 999
            else:
                ratio = 0
            if ratio > 2 and total_cas > 10000:
                add_threat(world, 5, "decisive_victory")
                add_coalition_shock(enemy_marshal.nation, world)
            # Capital capture
            if conquered:
                cap_reg = world.get_region(target_location)
                if cap_reg and getattr(cap_reg, 'is_capital', False):
                    add_threat(world, 15, "capital_capture")
            # War exhaustion for defender
            add_war_exhaustion_from_battle(enemy_marshal.nation, def_cas, world)

        elif battle_result.get("victor") == enemy_marshal.name:
            # France lost (either as attacker or defender)
            if marshal.nation == france:
                add_war_exhaustion_from_battle(marshal.nation, atk_cas, world)
            if enemy_marshal.nation == france:
                # France won as defender
                add_threat(world, 3, "battle_win")
                if atk_cas > 0 and def_cas > 0:
                    ratio = atk_cas / def_cas if def_cas > 0 else 999
                elif atk_cas > 0:
                    ratio = 999
                else:
                    ratio = 0
                if ratio > 2 and total_cas > 10000:
                    add_threat(world, 5, "decisive_victory")
                    add_coalition_shock(marshal.nation, world)
                add_war_exhaustion_from_battle(marshal.nation, atk_cas, world)

        # Build auto-bombardment preamble (Session 68) — prepended before combat description
        auto_bombard_preamble = ""
        if auto_bombardment_messages:
            auto_bombard_preamble = "\n".join(auto_bombardment_messages) + "\n\n"

        # Build final message with optional drill cancellation prefix, counter-punch, cavalry charge, and covering
        battle_message = counter_punch_message + cavalry_charge_message + covering_message + flanking_prefix + auto_bombard_preamble + battle_result["description"] + destroyed_msg + movement_msg + conquest_msg + vindication_msg + forced_retreat_msg
        if drill_cancelled_message:
            battle_message = drill_cancelled_message + battle_message

        # Generate battle name: "Battle of [Region]"
        battle_name = f"Battle of {target_location}"

        result = {
            "success": True,
            "message": battle_message,
            "battle_name": battle_name,
            "events": [{
                "type": "battle",
                "battle_name": battle_name,
                "attacker": battle_result["attacker"],
                "defender": battle_result["defender"],
                "outcome": battle_result["outcome"],
                "victor": battle_result["victor"],
                "enemy_destroyed": enemy_destroyed,
                "region_conquered": conquered,
                "region_name": resolved_target if conquered else None,
                "flanking_bonus": flanking_bonus,
                "flanking_origins": list(flanking_info["unique_origins"]) if flanking_info["unique_origins"] else [],
                "vindication": vindication_result,
                "attacker_forced_retreat": battle_result.get("attacker", {}).get("forced_retreat", False),
                "defender_forced_retreat": battle_result.get("defender", {}).get("forced_retreat", False),
                "cavalry_terrain_message": battle_result.get("cavalry_terrain_message"),
                # Fort degradation (for enemy phase dialog display)
                "fortification_degraded": battle_result.get("fortification_degraded", False),
                "fortification_old": battle_result.get("fortification_old", 0),
                "fortification_new": battle_result.get("fortification_new", 0),
            }],
            "new_state": game_state
        }

        # Phase 6.1: Pass cavalry terrain message through as separate field
        # so Godot can display it in structured UI (not just embedded in description text)
        if battle_result.get("cavalry_terrain_message"):
            result["cavalry_terrain_message"] = battle_result["cavalry_terrain_message"]

        # Berthier's After-Action Report
        if battle_result.get("battle_report"):
            result["battle_report"] = battle_result["battle_report"]

        # Auto-bombardment data (Session 68): pass through for Godot display
        if auto_bombardment_results:
            result["auto_bombardment"] = True
            result["auto_bombardment_results"] = [
                r.get("bombardment_result", {}) for r in auto_bombardment_results
            ]
            result["support_bombardment_total_damage"] = int(support_bombardment_total_damage)

        # Overwatch data (Session 68): pass through for battle report
        if overwatch_count > 0:
            result["overwatch_count"] = int(overwatch_count)
            result["overwatch_penalty_pct"] = int(overwatch_count * 3)

        # Coordination preview removed — narrative observation only (Gate 4).

        # ════════════════════════════════════════════════════════════
        # FIRST-TIME COORDINATION TUTORIAL (Session 66)
        # Fires ONCE per campaign when player's marshals achieve combined arms.
        # ════════════════════════════════════════════════════════════
        if (not world.coordination_tutorial_shown
                and attacker_coord.get("type_count", 0) >= 2
                and marshal.nation == world.player_nation):
            world.coordination_tutorial_shown = True
            result["coordination_tutorial"] = {
                "title": "BERTHIER'S REPORT",
                "message": (
                    '"Sire, our marshals fight as one corps for the first time! '
                    'The combined arms of infantry and cavalry proved decisive."'
                ),
                "tip": (
                    "Position different unit types together for combined arms bonuses. "
                    "Coordination improves with strong relationships between marshals."
                ),
                "warning": (
                    "When marshals coordinate, casualties are shared. "
                    "All friendly marshals in a battle region take proportional "
                    "damage — even those not directly targeted."
                ),
            }

        # Reinforcement notification messages (Session 65/66)
        reinf_messages = []
        arrived_names = []
        for r in attacker_reinforcements:
            if r.get("arrived"):
                reinf_messages.append(
                    f"{r['marshal']}'s forces arrived to reinforce {marshal.name}!")
                arrived_names.append(r["marshal"])
            else:
                reason = r.get("reason", "unknown")
                if reason == "literal_personality":
                    friendly_reason = f"{r['marshal']} awaits explicit orders and did not march to the sound of the guns."
                elif reason == "fate_intervened":
                    friendly_reason = f"{r['marshal']} was nearly in position, but fate intervened at the crucial moment."
                else:
                    friendly_reason = f"{r['marshal']} could not reach the battlefield in time."
                reinf_messages.append(friendly_reason)

        # Aggregate ally casualties (Session 66)
        if arrived_names and atk_distribution:
            ally_casualties = sum(
                atk_distribution.get(name, 0) for name in arrived_names)
            if ally_casualties > 0:
                if len(arrived_names) == 1:
                    reinf_messages.append(
                        f"His supporting ally lost {int(ally_casualties):,} men.")
                else:
                    reinf_messages.append(
                        f"His supporting allies lost {int(ally_casualties):,} men combined.")

        if reinf_messages:
            result["reinforcement_messages"] = reinf_messages

        # Mark as free action for Davout's Counter-Punch
        if is_counter_punch:
            result["free_action"] = True
            result["counter_punch_used"] = True

        # Phase 6.2.E: Flag pending capture choice for popup
        if world.pending_capture_choice:
            result["pending_capture_choice"] = True
            result["capture_data"] = world.pending_capture_choice

        # ════════════════════════════════════════════════════════════
        # REINFORCEMENT TRUST PENALTIES (Session 61a)
        # Non-Literal, non-Hostile marshals who fail to arrive lose -3 trust.
        # ════════════════════════════════════════════════════════════
        all_reinforcements = attacker_reinforcements + defender_reinforcements
        for reinf_result in all_reinforcements:
            if not reinf_result["arrived"] and reinf_result["reason"] not in ("literal_personality", "fate_intervened"):
                failing = world.marshals.get(reinf_result["marshal"])
                if failing:
                    # Determine which primary this marshal was trying to reinforce
                    primary_name = (
                        marshal.name if failing.nation == marshal.nation
                        else enemy_marshal.name
                    )
                    rel = failing.get_relationship(primary_name)
                    if rel != -2:  # Hostile gets no penalty
                        failing.trust.modify(-3)

        # Attach reinforcement data to result for display (N3)
        if attacker_reinforcements or defender_reinforcements:
            result["reinforcement_results"] = {
                "attacker": attacker_reinforcements,
                "defender": defender_reinforcements,
            }

        # ════════════════════════════════════════════════════════════
        # EXHAUSTION TRACKING (Phase 3 - Attack Spam Prevention)
        # Increment attack counter AFTER attack, but NOT for counter-punch
        # Counter-punch is reactive, not spam
        # ════════════════════════════════════════════════════════════
        if not is_counter_punch:
            marshal.increment_attacks_this_turn()

        # ════════════════════════════════════════════════════════════
        # BOMBARDMENT STREAK TRACKING (Artillery Session 2)
        # Track consecutive artillery attacks on same target region
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'artillery', False):
            if target_location == getattr(marshal, 'last_bombardment_target', None):
                marshal.bombardment_streak += 1
            else:
                marshal.last_bombardment_target = target_location
                marshal.bombardment_streak = 1

        # ════════════════════════════════════════════════════════════
        # BERTHIER BOMBARDMENT ADVISORY (Artillery Session 2)
        # Alert when enemy fortifications are crumbling after bombardment
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'artillery', False) and not enemy_destroyed:
            defender_fort = getattr(enemy_marshal, 'defense_bonus', 0)
            target_reg = world.get_region(target_location)
            has_fort_building = target_reg.has_building("fortification") if target_reg and hasattr(target_reg, 'has_building') else False
            if defender_fort <= 0 and not has_fort_building:
                result["bombardment_advisory"] = (
                    f"Sire, the enemy fortifications at {target_location} are crumbling. "
                    f"An infantry assault would now have favorable odds."
                )

        return result

    def _execute_defend(self, marshal, world, game_state) -> Dict:
        """
        Smart defend - context-aware defensive behavior.

        Maps "defend" to appropriate action based on current stance:
        - If NEUTRAL → change to DEFENSIVE stance (1 action)
        - If DEFENSIVE and not fortified → execute fortify
        - If DEFENSIVE and already fortified → return info message
        - If AGGRESSIVE → change to DEFENSIVE stance (2 actions)

        This makes "defend" an intuitive command that always moves
        the marshal toward a more defensive posture.
        """
        # ════════════════════════════════════════════════════════════
        # DRILL STATE CHECK: Handle drilling marshal trying to defend
        # ════════════════════════════════════════════════════════════
        drill_cancelled_message = ""
        if getattr(marshal, 'drilling', False):
            if getattr(marshal, 'drilling_locked', False):
                # Turn 2: Locked in drill, cannot defend
                return {
                    "success": False,
                    "message": f"{marshal.name} is locked in drill formation and cannot change to defensive stance. Only RETREAT is allowed.",
                    "drilling_locked": True
                }
            else:
                # Turn 1: Can defend but drill is cancelled
                marshal.drilling = False
                marshal.drill_complete_turn = -1
                drill_cancelled_message = f"⚠️ DRILL CANCELLED: {marshal.name}'s drill was interrupted - troops dispersed before training completed.\n\n"

        # ════════════════════════════════════════════════════════════
        # SMART DEFEND: Context-aware routing based on stance
        # ════════════════════════════════════════════════════════════
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)

        # Case 1: Already in DEFENSIVE stance
        if current_stance == Stance.DEFENSIVE:
            # Check if already fortified
            if getattr(marshal, 'fortified', False):
                current_bonus = int(getattr(marshal, 'defense_bonus', 0) * 100)
                return {
                    "success": False,
                    "message": f"{marshal.name} is already defending and fortified at {marshal.location} (+{current_bonus}% defense). "
                              f"No further defensive action needed.",
                }

            # Not fortified yet - execute fortify
            command = {"marshal": marshal.name}
            fortify_result = self._execute_fortify(command, game_state)

            # Prepend drill cancelled message if applicable
            if drill_cancelled_message and fortify_result.get("success"):
                fortify_result["message"] = drill_cancelled_message + fortify_result.get("message", "")
                fortify_result["drill_cancelled"] = True

            return fortify_result

        # Case 2: In NEUTRAL or AGGRESSIVE stance - change to DEFENSIVE
        action_cost = self._get_stance_change_cost(current_stance, Stance.DEFENSIVE)

        # Check if player has enough actions
        if action_cost > 0 and world.actions_remaining < action_cost:
            return {
                "success": False,
                "message": f"Switching {marshal.name} to defensive stance requires {action_cost} action(s), "
                          f"but only {world.actions_remaining} remaining."
            }

        # Execute the stance change
        old_stance = current_stance
        marshal.stance = Stance.DEFENSIVE

        # Build message
        if old_stance == Stance.AGGRESSIVE:
            defend_message = f"{marshal.name} abandons aggressive posture and shifts to DEFENSIVE stance. "
            defend_message += f"Effect: -10% attack, +15% defense. (Cost: {action_cost} actions)"
        else:
            defend_message = f"{marshal.name} shifts to DEFENSIVE stance at {marshal.location}. "
            defend_message += "Effect: -10% attack, +15% defense."

        if drill_cancelled_message:
            defend_message = drill_cancelled_message + defend_message

        events = [{
            "type": "stance_change",
            "marshal": marshal.name,
            "from_stance": old_stance.value,
            "to_stance": "defensive",
            "action_cost": action_cost
        }]

        # Add drill_cancelled event if drill was interrupted
        if drill_cancelled_message:
            events.insert(0, {
                "type": "drill_cancelled",
                "marshal": marshal.name,
                "reason": "defend"
            })

        return {
            "success": True,
            "message": defend_message,
            "drill_cancelled": bool(drill_cancelled_message),
            "variable_action_cost": action_cost,  # Variable cost based on stance transition
            "events": events,
            "new_state": game_state
        }

    def _execute_hold(self, marshal, world, game_state) -> Dict:
        """
        Execute a hold order - alias for defend with different flavor text.

        "Hold" means the same thing as "defend" mechanically:
        - Changes to defensive stance if not already
        - Fortifies if already defensive
        - Same action costs

        GROUCHY IMMOVABLE (Phase 2.8):
        - For literal marshals (Grouchy), hold also sets holding_position = True
        - This grants +15% defense bonus when defending at that location
        - The bonus persists as long as Grouchy stays at that position

        The distinction is purely for player expression - some prefer
        "hold the line" to "defend".
        """
        # ════════════════════════════════════════════════════════════
        # GROUCHY IMMOVABLE (Phase 2.8): Set holding_position for literal marshals
        # ════════════════════════════════════════════════════════════
        immovable_message = ""
        if getattr(marshal, 'personality', '') == 'literal':
            marshal.holding_position = True
            marshal.hold_region = marshal.location
            immovable_message = f"\n🏰 {marshal.name} plants himself at {marshal.location}! (IMMOVABLE: +15% defense while holding)"
            print(f"  [IMMOVABLE] {marshal.name} holding at {marshal.location}")

        # Delegate to defend - hold IS defend, just different wording
        result = self._execute_defend(marshal, world, game_state)

        # Adjust message to use "hold" terminology if successful
        if result.get("success") and result.get("message"):
            # Replace "defend" terminology with "hold" in message
            original_msg = result["message"]
            # Keep the message mostly the same - the mechanics message is fine
            # Just prepend a "holding" flavor if stance changed
            if "shifts to DEFENSIVE stance" in original_msg:
                result["message"] = original_msg.replace(
                    "shifts to DEFENSIVE stance",
                    "holds position, shifting to DEFENSIVE stance"
                )
            # Add Immovable message
            if immovable_message:
                result["message"] += immovable_message

        # Update event type if present
        if result.get("events"):
            for event in result["events"]:
                if event.get("type") == "stance_change":
                    event["command"] = "hold"  # Mark that this came from hold command
                    if getattr(marshal, 'personality', '') == 'literal':
                        event["immovable"] = True

        return result

    def _execute_wait(self, marshal, world, game_state) -> Dict:
        """
        Execute a wait order - free action (costs 0 actions).

        "Wait" means the marshal passes their turn without acting.
        This is useful when:
        - Conserving actions for other marshals
        - Waiting for a better tactical moment
        - Maintaining position without committing

        Unlike defend/hold, wait does NOT change stance or provide bonuses.
        The marshal simply does nothing this action.

        NOTE: In future updates, "wait" may support conditional orders like
        "wait for Davout to attack, then move to support" but for now it's
        a simple pass action.
        """
        # Wait is always successful and costs nothing
        wait_message = f"{marshal.name} holds position at {marshal.location}, awaiting further orders."

        # Add context about current stance
        current_stance = getattr(marshal, 'stance', None)
        if current_stance:
            stance_name = current_stance.value if hasattr(current_stance, 'value') else str(current_stance)
            wait_message += f" (Current stance: {stance_name})"

        return {
            "success": True,
            "message": wait_message,
            "variable_action_cost": 0,  # FREE ACTION - costs nothing
            "events": [{
                "type": "wait",
                "marshal": marshal.name,
                "location": marshal.location,
                "action_cost": 0
            }],
            "new_state": game_state
        }

    # ════════════════════════════════════════════════════════════════════════
    # GENERIC TARGET RESOLUTION (Phase 5.2)
    # Resolves vague targets ("the enemy", "whoever needs it") for all
    # strategic types. Literal personality gets clarification popup.
    # ════════════════════════════════════════════════════════════════════════

    def _resolve_generic_target(self, marshal, strategic_type: str, target: str,
                                world, parsed_command: dict) -> dict:
        """
        Resolve a generic/vague target for any strategic command type.

        Returns:
            {"resolved": True, "target": str, "target_type": str} on success,
            {"needs_clarification": True, "response": dict} for literal marshals,
            {"resolved": False} if no resolution possible.
        """
        is_literal = getattr(marshal, 'personality', '') == 'literal'

        # ── PURSUE: nearest enemy marshal ────────────────────────────
        if strategic_type == "PURSUE":
            enemies = world.get_enemies_of_nation(marshal.nation)
            enemies = [e for e in enemies if e.strength > 0]
            nearest, alternatives = self._find_nearest_enemy(marshal, enemies, world)

            if not nearest:
                return {"resolved": False}

            if is_literal:
                return self._build_clarification(
                    marshal, strategic_type, nearest.name, "nearest enemy",
                    [e.name for e in enemies if e.name != nearest.name][:2],
                    world, f"You wish me to pursue {nearest.name}, Sire?"
                )
            return {"resolved": True, "target": nearest.name, "target_type": "marshal"}

        # ── SUPPORT: most threatened ally ────────────────────────────
        if strategic_type == "SUPPORT":
            allies = [m for m in world.marshals.values()
                      if m.nation == marshal.nation
                      and m.name != marshal.name
                      and m.strength > 0
                      and not getattr(m, 'administrative', False)]

            if not allies:
                return {"resolved": False}

            def threat_level(ally):
                threats = len(world.get_enemies_in_region(ally.location, ally.nation))
                region = world.get_region(ally.location)
                if region:
                    for adj in region.adjacent_regions:
                        threats += len(world.get_enemies_in_region(adj, ally.nation))
                return threats

            most_threatened = max(allies, key=threat_level)
            alt_names = [a.name for a in allies if a.name != most_threatened.name][:2]

            if is_literal:
                return self._build_clarification(
                    marshal, strategic_type, most_threatened.name, "most threatened ally",
                    alt_names, world,
                    f"You wish me to support {most_threatened.name}, Sire?"
                )
            return {"resolved": True, "target": most_threatened.name, "target_type": "marshal"}

        # ── MOVE_TO: nearest enemy region ────────────────────────────
        if strategic_type == "MOVE_TO":
            enemies = world.get_enemies_of_nation(marshal.nation)
            enemies = [e for e in enemies if e.strength > 0]
            nearest, _ = self._find_nearest_enemy(marshal, enemies, world)

            if not nearest:
                return {"resolved": False}

            target_region = nearest.location
            alt_regions = list(set(
                e.location for e in enemies if e.location != target_region
            ))[:2]

            if is_literal:
                return self._build_clarification(
                    marshal, strategic_type, target_region, "nearest enemy position",
                    alt_regions, world,
                    f"You wish me to march to {target_region}, Sire?"
                )
            return {"resolved": True, "target": target_region, "target_type": "region"}

        # ── HOLD: current location (already handled elsewhere, but be safe)
        if strategic_type == "HOLD":
            return {"resolved": True, "target": marshal.location, "target_type": "region"}

        return {"resolved": False}

    def _find_nearest_enemy(self, marshal, enemies, world):
        """Find nearest enemy by path distance. Returns (nearest_marshal, all_enemies)."""
        nearest = None
        nearest_dist = 999
        for e in enemies:
            p = world.find_path(marshal.location, e.location)
            if p and len(p) - 1 < nearest_dist:
                nearest = e
                nearest_dist = len(p) - 1
        return nearest, enemies

    def _build_clarification(self, marshal, strategic_type: str, interpreted: str,
                             reason: str, alternatives: list, world, message: str) -> dict:
        """Build a clarification response for literal marshals."""
        options = [{
            "label": f"Yes, {interpreted}",
            "value": "confirm",
            "target": interpreted
        }]
        for alt in alternatives:
            options.append({
                "label": f"No, {alt}",
                "value": "specify",
                "target": alt
            })
        options.append({"label": "Cancel", "value": "cancel"})

        return {
            "needs_clarification": True,
            "response": {
                "success": True,
                "free_action": True,
                "state": "awaiting_clarification",
                "type": "clarification",
                "strategic_type": strategic_type,
                "marshal": marshal.name,
                "message": message,
                "interpreted_target": interpreted,
                "interpretation_reason": reason,
                "alternatives": alternatives,
                "options": options,
                "action_summary": world.get_action_summary(),
                "game_state": world.get_filtered_game_state_summary()
            }
        }

    # ════════════════════════════════════════════════════════════════════════
    # STRATEGIC COMMAND HANDLER (Phase 5.2)
    # Creates StrategicOrder on marshal & executes first step immediately.
    # ════════════════════════════════════════════════════════════════════════

    def _execute_strategic_command(self, parsed_command: Dict, command: Dict, game_state: Dict) -> Optional[Dict]:
        """
        Handle a strategic command: create StrategicOrder and execute first step.

        Returns result dict if handled, None to fall through to tactical routing.
        """
        from backend.models.marshal import StrategicOrder, StrategicCondition

        world: WorldState = game_state.get("world")
        if not world:
            return None

        marshal_name = command.get("marshal")
        if not marshal_name:
            return None

        marshal = world.get_marshal(marshal_name)
        if not marshal:
            return None

        strategic_type = parsed_command.get("strategic_type")
        target = command.get("target")
        target_type = command.get("target_type", "region")
        snapshot = parsed_command.get("target_snapshot_location")

        # Auto-break square formation (Session 67: "any strategic command breaks square")
        self._auto_break_square(marshal, strategic_type or "strategic order")

        print(f"[STRATEGIC] Creating {strategic_type} order for {marshal.name} -> {target}")

        # ── Artillery PURSUE block: guns can't chase ──
        if strategic_type == "PURSUE" and getattr(marshal, 'artillery', False):
            return {
                "success": False,
                "message": f"{marshal.name}'s artillery cannot pursue. Guns must be repositioned manually — try 'move to' instead."
            }

        # ── Engagement check: cannot issue strategic orders while engaged ──
        # Exceptions:
        #   - PURSUE targeting an enemy in THIS region (or generic, which resolves to one here)
        #   - HOLD current region: defending where you stand is always valid
        enemies_here = world.get_enemies_in_region(marshal.location, marshal.nation)
        if enemies_here:
            holding_here = (
                strategic_type == "HOLD" and
                (not target or target == "generic" or target == marshal.location)
            )
            pursuing_local = (
                strategic_type == "PURSUE" and (
                    not target or target == "generic" or
                    any(e.name.lower() == target.lower() for e in enemies_here)
                )
            )
            if not holding_here and not pursuing_local:
                enemy_names = [e.name for e in enemies_here]
                return {
                    "success": False,
                    "message": f"{marshal.name} is engaged with {', '.join(enemy_names)} and cannot begin a strategic march. Deal with the engagement first.",
                    "engaged_with": enemy_names,
                    "suggestion": f"Try: '{marshal.name}, attack {enemy_names[0]}' or '{marshal.name}, retreat'"
                }

        # ── Self-targeting validation ────────────────────────────────
        if target and target.lower() == marshal.name.lower():
            return {
                "success": False,
                "message": f"{marshal.name} cannot target themselves!"
            }

        # ── Resolve generic/vague targets for ALL strategic types ────
        GENERIC_TARGETS = {
            "generic", "the enemy", "enemy", "enemies", "them",
            "the marshal", "marshal", "the general", "general",
            "the commander", "commander",
            "the region", "someone", "somebody", "anyone",
            "whoever", "nearest", "closest",
        }
        is_generic = (
            not target
            or target.lower() in GENERIC_TARGETS
            or target_type == "generic"
        )
        if is_generic:
            resolution = self._resolve_generic_target(
                marshal, strategic_type, target, world, parsed_command
            )
            if resolution.get("needs_clarification"):
                return resolution["response"]
            if resolution.get("resolved"):
                target = resolution["target"]
                target_type = resolution["target_type"]
                print(f"[STRATEGIC] Generic resolved -> {target} ({target_type})")

        # ── Validate target ───────────────────────────────────────────
        # SUPPORT must target a friendly marshal, not a region
        if strategic_type == "SUPPORT":
            # Self-SUPPORT guard (Phase 7 audit finding)
            if target and target.lower() == marshal.name.lower():
                return {
                    "success": False,
                    "message": f"Berthier pauses. 'Sire, {marshal.name} cannot be ordered to support himself. SUPPORT coordinates with a different marshal.'",
                    "suggestion": "Available French marshals: " + ", ".join(
                        m.name for m in world.marshals.values()
                        if m.nation == marshal.nation and m.name != marshal.name
                    )
                }
            ally = world.get_marshal(target)
            if not ally:
                # Check if it's a region name (Bug #4)
                region = world.get_region(target) if target else None
                if region:
                    return {
                        "success": False,
                        "message": f"{target} is a region, not a marshal. SUPPORT targets a friendly marshal.",
                        "suggestion": f"Try: '{marshal.name}, support Davout' — SUPPORT targets a friendly marshal, not a region."
                    }
                return {
                    "success": False,
                    "message": f"Cannot find marshal '{target}' to support.",
                    "suggestion": "Available French marshals: " + ", ".join(
                        m.name for m in world.marshals.values()
                        if m.nation == marshal.nation and m.name != marshal.name
                    )
                }
            if ally.nation != marshal.nation:
                return {
                    "success": False,
                    "message": f"{target} is an enemy! Use PURSUE instead.",
                    "suggestion": f"Try: '{marshal.name}, pursue {target}'"
                }
            target_type = "marshal"

        # PURSUE must target an enemy marshal
        if strategic_type == "PURSUE":
            enemy = world.get_marshal(target)
            if not enemy:
                # Check if it's a region
                region = world.get_region(target) if target else None
                if region:
                    # PURSUE a region doesn't make sense — convert to MOVE_TO
                    print(f"[STRATEGIC] PURSUE region '{target}' -> converting to MOVE_TO")
                    strategic_type = "MOVE_TO"
                    target_type = "region"
                else:
                    return {
                        "success": False,
                        "message": f"Cannot find '{target}' to pursue.",
                    }
            else:
                target_type = "marshal"

        # ── HOLD: default target to current location (Bug #7) ─────────
        if strategic_type == "HOLD" and (not target or target == "generic"):
            target = marshal.location
            target_type = "region"

        # ── HOLD: Check if already holding the same location ──────────
        # Block redundant HOLD orders to prevent accidental AP waste
        if strategic_type == "HOLD":
            existing_order = marshal.strategic_order
            if existing_order and existing_order.command_type == "HOLD":
                existing_target = existing_order.target or marshal.location
                new_target = target or marshal.location
                if existing_target == new_target:
                    return {
                        "success": False,
                        "message": f"{marshal.name} is already holding {existing_target}. No action needed.",
                        "already_holding": True,
                        "variable_action_cost": 0,  # Don't consume AP
                    }

        # ── Build path for movement orders ────────────────────────────
        path = []
        if strategic_type in ("MOVE_TO", "PURSUE", "SUPPORT", "HOLD"):
            dest = None
            if strategic_type == "MOVE_TO":
                dest = target
            elif strategic_type == "PURSUE":
                enemy = world.get_marshal(target)
                dest = enemy.location if enemy else None
            elif strategic_type == "SUPPORT":
                ally = world.get_marshal(target)
                dest = ally.location if ally else None
            elif strategic_type == "HOLD":
                dest = target

            if dest and dest != marshal.location:
                # Personality-aware pathfinding (cautious avoids enemies)
                # MOVE_TO and HOLD use weighted (Dijkstra) pathfinding for terrain-aware routes
                # PURSUE/SUPPORT stay on BFS (chasing/supporting doesn't pick scenic routes)
                use_weighted = (strategic_type in ("MOVE_TO", "HOLD"))
                pathfinder = world.find_weighted_path if use_weighted else world.find_path
                personality = getattr(marshal, 'personality', 'balanced')
                if personality == "cautious":
                    enemy_regions = [
                        rn for rn in world.regions
                        if world.get_enemies_in_region(rn, marshal.nation)
                    ]
                    path = pathfinder(marshal.location, dest,
                                      avoid_regions=enemy_regions)
                    if not path:
                        # Fallback to direct path
                        path = pathfinder(marshal.location, dest)
                else:
                    path = pathfinder(marshal.location, dest)
                if not path:
                    return {
                        "success": False,
                        "message": f"No path from {marshal.location} to {dest}.",
                    }
                # Strip start location
                path = [r for r in path if r != marshal.location]

        # ── Strategic objection check (V2a) ───────────────────────────
        # Check if marshal objects to this strategic command BEFORE creating order
        # Uses V2 evaluate_strategic_situation() (deterministic ConcernLevel triggers)

        # Check for objection response (post-objection execution)
        objection_response = command.get("objection_response")

        # ═══════════════════════════════════════════════════════════════════════════
        # V2a STRATEGIC OBJECTION CHECK
        # ═══════════════════════════════════════════════════════════════════════════
        # Uses deterministic ConcernLevel evaluation (same as tactical path).
        # Per-marshal popup cap: max 1 popup per marshal per turn.
        # Trust affects consequences (tone, insist penalty), not trigger.
        #
        # Flow:
        #   1. User issues command → V2 evaluates → concern >= MODERATE → popup
        #   2. Frontend shows popup → user chooses trust/insist/compromise
        #   3. Frontend calls /respond_to_objection
        #   4. handle_objection_response() finds pending_strategic_objection
        #   5. Routes to _handle_strategic_objection_from_endpoint()
        #   6. Re-executes strategic command with objection_response set
        # ═══════════════════════════════════════════════════════════════════════════
        if not objection_response:
            # Bypass checks (already handled by V2 evaluators for literal/etc.)
            should_check = True
            if getattr(marshal, 'retreat_recovery', 0) > 0:
                should_check = False
            if marshal.nation != world.player_nation:
                should_check = False

            if should_check:
                # V2 evaluation: deterministic concern level + mood variance
                base_concern = evaluate_strategic_situation(
                    marshal, strategic_type, target, path, game_state
                )

                # V2b: Vindication escalation/de-escalation (same as tactical path)
                vindication_shifted = base_concern
                v_score = getattr(marshal, 'vindication_score', 0)
                if v_score > 0 and base_concern != ConcernLevel.NONE:
                    new_val = min(base_concern.value + 1, ConcernLevel.EXTREME.value)
                    vindication_shifted = ConcernLevel(new_val)
                elif v_score < 0 and base_concern != ConcernLevel.NONE:
                    new_val = max(base_concern.value - 1, ConcernLevel.MILD.value)
                    vindication_shifted = ConcernLevel(new_val)
                strategic_concern = apply_mood_variance(vindication_shifted)
                # Track last objection turn for vindication decay
                if base_concern != ConcernLevel.NONE:
                    marshal.last_objection_turn = world.current_turn

                if strategic_concern == ConcernLevel.MILD:
                    # MILD: Flavor text in turn log, order proceeds
                    if marshal.name not in [c.get("marshal") for c in world.mild_concerns_this_turn]:
                        world.mild_concerns_this_turn.append({
                            "marshal": marshal.name,
                            "message": self._generate_mild_concern_message(
                                marshal, strategic_type.lower(), command
                            ),
                            "concern_level": "MILD",
                            "action": strategic_type,
                        })

                elif strategic_concern >= ConcernLevel.MODERATE:
                    # Per-marshal cap: max 1 popup per marshal per turn
                    if marshal.name in world.objection_popups_this_turn:
                        # Downgrade to MILD
                        if marshal.name not in [c.get("marshal") for c in world.mild_concerns_this_turn]:
                            world.mild_concerns_this_turn.append({
                                "marshal": marshal.name,
                                "message": self._generate_mild_concern_message(
                                    marshal, strategic_type.lower(), command
                                ),
                                "concern_level": "MILD",
                                "action": strategic_type,
                                "downgraded_from": strategic_concern.name,
                            })
                    else:
                        # Show popup
                        world.objection_popups_this_turn.add(marshal.name)

                        # V2 trust consequences
                        trust_tier = get_trust_tier(marshal.trust.value)
                        tone = get_objection_tone(trust_tier)
                        insist_penalty = get_insist_penalty(trust_tier)
                        trust_gain = calculate_trust_gain(strategic_concern, trust_tier)
                        legacy_severity = concern_to_legacy_severity(strategic_concern)

                        # Generate alternatives using V1 personality helpers
                        from backend.commands.disobedience import check_strategic_objection
                        v1_objection = check_strategic_objection(
                            marshal, strategic_type, target, path, world, game_state
                        )
                        # Extract options from V1 if available, otherwise build minimal
                        v1_options = v1_objection.get("options", []) if v1_objection else []

                        # V2b: Relationship-based SUPPORT — generate options if V1 didn't
                        from backend.commands.objection_v2 import (
                            _evaluate_relationship_support, RELATIONSHIP_SUPPORT_MESSAGES
                        )
                        relationship_concern = ConcernLevel.NONE
                        if strategic_type == "SUPPORT":
                            relationship_concern = _evaluate_relationship_support(
                                marshal, target, game_state
                            )
                        if relationship_concern >= ConcernLevel.MODERATE and not v1_options:
                            # Build relationship-specific options with timed SUPPORT compromise
                            v1_options = [
                                {
                                    "type": "insist",
                                    "text": f"Insist: SUPPORT {target} as ordered",
                                },
                                {
                                    "type": "trust",
                                    "text": "Trust: Cancel the SUPPORT order",
                                    "action": "cancel",
                                    "target": target,
                                },
                                {
                                    "type": "compromise",
                                    "text": "Compromise: Timed SUPPORT (3 turns)",
                                    "compromise": {"max_turns": 3},
                                },
                            ]

                        # Fallback: If V2 triggered MODERATE+ but V1 produced no options,
                        # build default insist/trust/compromise with aggressive preferred chain
                        if not v1_options and strategic_concern >= ConcernLevel.MODERATE:
                            from backend.commands.disobedience import _get_aggressive_preferred, _build_strategic_options
                            preferred = _get_aggressive_preferred(marshal, world) if marshal.personality == 'aggressive' else None
                            compromise = {"action": strategic_type.lower(), "max_turns": 3}
                            v1_options = _build_strategic_options(
                                marshal,
                                preferred,
                                compromise,
                                f"Proceed with {strategic_type}",
                                f"Accept: Timed {strategic_type} (3 turns)",
                                strategic_type
                            )

                        # V2b: Use relationship message if this is a relationship-triggered SUPPORT objection
                        if (relationship_concern >= ConcernLevel.MILD
                                and strategic_type == "SUPPORT"
                                and relationship_concern >= strategic_concern):
                            rel_msg_template = RELATIONSHIP_SUPPORT_MESSAGES.get(
                                relationship_concern, ""
                            )
                            if rel_msg_template:
                                message = f'"{marshal.name}: {rel_msg_template.format(target=target)}"'
                            else:
                                message = self._generate_objection_message(
                                    marshal, strategic_type.lower(), command,
                                    strategic_concern, tone
                                )
                        else:
                            message = self._generate_objection_message(
                                marshal, strategic_type.lower(), command,
                                strategic_concern, tone
                            )

                        objection = {
                            # V2 fields
                            "type": "strategic",
                            "concern_level": strategic_concern.name,
                            "trust_tier": trust_tier.name,
                            "tone": tone,
                            "insist_penalty": insist_penalty,
                            "trust_gain": trust_gain,
                            "compromise_gain": COMPROMISE_TRUST_GAIN,
                            "should_object": True,
                            # Backward compat fields
                            "severity": legacy_severity,
                            "message": message,
                            "marshal": marshal.name,
                            "personality": marshal.personality,
                            "reason": f"v2_{marshal.personality}_{strategic_type.lower()}",
                            "options": v1_options,
                            # Data for response handling
                            "original_command": command.copy(),
                            "parsed_command": parsed_command.copy(),
                            "strategic_type": strategic_type,
                            "path": path,
                            "target": target,
                            "marshal_name": marshal.name,
                        }

                        # CRITICAL: Store on world for /respond_to_objection endpoint
                        world.pending_strategic_objection = objection

                        return {
                            "success": True,
                            "pending_objection": True,
                            "objection": objection,
                            "message": message,
                            "marshal": marshal.name,
                            "personality": marshal.personality,
                            "concern_level": strategic_concern.name,
                            "tone": tone,
                            "severity": legacy_severity,
                            "trust": int(marshal.trust.value),
                            "trust_label": marshal.trust.get_label(),
                            "vindication": world.vindication_tracker.get_vindication_data(marshal.name).get("score", 0),
                            "authority": int(world.authority_tracker.authority),
                        }

        else:
            # Post-objection: Handle the response
            result = self._handle_strategic_objection_response(
                marshal, command, parsed_command, objection_response, world, game_state, path, target, strategic_type
            )
            if result is not None:
                return result

        # ── Build condition ───────────────────────────────────────────
        condition = None
        cond_dict = parsed_command.get("strategic_condition")
        if cond_dict and isinstance(cond_dict, dict):
            condition = StrategicCondition(
                max_turns=cond_dict.get("max_turns"),
                until_marshal_arrives=cond_dict.get("until_marshal_arrives"),
                until_marshal_destroyed=cond_dict.get("until_marshal_destroyed"),
                until_relieved=cond_dict.get("until_relieved", False),
                until_battle_won=cond_dict.get("until_battle_won", False),
            )

        # ── Create StrategicOrder ─────────────────────────────────────
        order = StrategicOrder(
            command_type=strategic_type,
            target=target or "generic",
            target_type=target_type,
            started_turn=world.current_turn,
            original_command=parsed_command.get("raw_input", ""),
            path=path,
            condition=condition,
            target_snapshot_location=snapshot,
            attack_on_arrival=parsed_command.get("attack_on_arrival", False),
            issued_turn=world.current_turn,
        )

        # Cancel any existing strategic order
        if marshal.strategic_order:
            print(f"[STRATEGIC] {marshal.name}'s previous order cancelled by new order")
            # Clear HOLD state if previous order was HOLD (mirrors pattern at line 937)
            if marshal.strategic_order.command_type == "HOLD":
                marshal.holding_position = False
                marshal.hold_region = ""
        marshal.strategic_order = order

        # Log strategic order event
        world.log_event({
            "type": "strategic_order",
            "marshal": marshal.name,
            "order_type": strategic_type,
            "destination": target or "",
        })

        print(f"[STRATEGIC] Order created: {strategic_type} -> {target}, path={path}")

        # ── Execute first step immediately ────────────────────────────
        # Cavalry (movement_range=2) moves UP TO movement_range regions per step
        first_step_msg = ""
        movement_range = getattr(marshal, 'movement_range', 1)
        print(f"[STRATEGIC INIT] {marshal.name}: Path = {path}, movement_range = {movement_range}")
        print(f"[STRATEGIC INIT] {marshal.name}: Executing first step from {marshal.location}...")

        # ── PURSUE: target in same region → personality-aware immediate response ──
        pursue_handled = False
        if strategic_type == "PURSUE":
            enemy_m = world.get_marshal(target)
            if enemy_m and enemy_m.strength > 0 and marshal.location == enemy_m.location:
                pursue_handled = True
                personality = getattr(marshal, 'personality', 'balanced')
                if personality == "aggressive" or order.attack_on_arrival:
                    attack_result = self.execute(
                        {"command": {"marshal": marshal.name, "action": "attack",
                                     "target": target, "_strategic_execution": True}},
                        game_state)
                    combat_msg = attack_result.get("message", "")
                    first_step_msg = f" They're right here! Engaging!\n\n{combat_msg}"
                else:
                    first_step_msg = (f" {target} is right here in {marshal.location}!"
                                      f" Awaiting the right moment to strike.")

        if not pursue_handled and strategic_type == "MOVE_TO" and path:
            steps = min(movement_range, len(path))
            moved_regions = []
            print(f"[STRATEGIC INIT] {marshal.name}: MOVE_TO first step, {steps} step(s) max")
            for i in range(steps):
                if not order.path:
                    break
                next_region = order.path[0]
                enemies = world.get_enemies_in_region(next_region, marshal.nation)
                if enemies:
                    print(f"[STRATEGIC INIT] {marshal.name}: First step BLOCKED by enemies at {next_region}")
                    if not moved_regions:
                        # First step blocked — personality-based response
                        blocked_result = self._handle_first_step_blocked(
                            marshal, enemies, next_region, world, game_state)
                        if blocked_result is not None:
                            return blocked_result  # Interrupt or combat result
                        # Literal reroute succeeded — continue with new path
                        first_step_msg = f" Adjusting route to avoid {next_region}."
                        # Re-check path after reroute
                        if order.path:
                            next_region = order.path[0]
                            enemies = world.get_enemies_in_region(next_region, marshal.nation)
                            if enemies:
                                break  # Still blocked after reroute
                        else:
                            break  # No path left
                    else:
                        break  # Mid-march block, stop here
                print(f"[STRATEGIC INIT] {marshal.name}: Moving {marshal.location} -> {next_region}")
                move_result = self.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "move",
                        "target": next_region,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                if move_result.get("success"):
                    order.path.pop(0)
                    moved_regions.append(next_region)
                    print(f"[STRATEGIC INIT] {marshal.name}: Moved to {next_region} OK")
                else:
                    print(f"[STRATEGIC INIT] {marshal.name}: Move FAILED - {move_result.get('message', '?')}")
                    break
            if not moved_regions:
                print(f"[STRATEGIC INIT] {marshal.name}: First step SKIPPED - no regions moved")
            if moved_regions:
                if len(moved_regions) > 1:
                    first_step_msg = f" Cavalry charges through {' -> '.join(moved_regions)}."
                else:
                    first_step_msg = f" Moves to {moved_regions[0]}."

        elif strategic_type == "HOLD":
            # If already at target, set holding immediately
            if marshal.location == (target or marshal.location):
                if marshal.personality == "literal":
                    marshal.holding_position = True
                    marshal.hold_region = marshal.location
                    first_step_msg = " [Immovable: +15% defense]"
                else:
                    first_step_msg = " Holding position."
            elif path:
                steps = min(movement_range, len(path))
                moved_regions = []
                for i in range(steps):
                    if not order.path:
                        break
                    next_region = order.path[0]
                    enemies = world.get_enemies_in_region(next_region, marshal.nation)
                    if enemies:
                        if not moved_regions:
                            # First step blocked — personality-based response
                            blocked_result = self._handle_first_step_blocked(
                                marshal, enemies, next_region, world, game_state)
                            if blocked_result is not None:
                                return blocked_result
                            # Literal reroute — continue with new path
                            first_step_msg = f" Adjusting route to avoid {next_region}."
                            if order.path:
                                next_region = order.path[0]
                                enemies = world.get_enemies_in_region(next_region, marshal.nation)
                                if enemies:
                                    break
                            else:
                                break
                        else:
                            break
                    move_result = self.execute(
                        {"command": {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": next_region,
                            "_strategic_execution": True
                        }},
                        game_state
                    )
                    if move_result.get("success"):
                        order.path.pop(0)
                        moved_regions.append(next_region)
                    else:
                        break
                if moved_regions:
                    first_step_msg = f" Marching to {target}."

        elif not pursue_handled and strategic_type == "PURSUE" and path:
            steps = min(movement_range, len(path))
            moved_regions = []
            for i in range(steps):
                if not order.path:
                    break
                next_region = order.path[0]
                enemies_blocking = world.get_enemies_in_region(next_region, marshal.nation)
                # Allow moving into target's region (that's the point of PURSUE)
                blocking = [e for e in enemies_blocking if e.name != target]
                if blocking:
                    if not moved_regions:
                        # First step blocked by non-target enemy
                        blocked_result = self._handle_first_step_blocked(
                            marshal, blocking, next_region, world, game_state)
                        if blocked_result is not None:
                            return blocked_result
                        # Literal reroute — continue
                        first_step_msg = f" Adjusting route to avoid {next_region}."
                        if order.path:
                            next_region = order.path[0]
                            enemies_blocking = world.get_enemies_in_region(next_region, marshal.nation)
                            blocking = [e for e in enemies_blocking if e.name != target]
                            if blocking:
                                break
                        else:
                            break
                    else:
                        break
                move_result = self.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "move",
                        "target": next_region,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                if move_result.get("success"):
                    order.path.pop(0)
                    moved_regions.append(next_region)
                else:
                    # Move failed — check if target is in this region (PURSUE should attack)
                    enemy_m = world.get_marshal(target)
                    if enemy_m and next_region == enemy_m.location:
                        personality = getattr(marshal, 'personality', 'balanced')
                        attack_on_arrival = getattr(order, 'attack_on_arrival', False)
                        if personality == "aggressive" or attack_on_arrival:
                            attack_result = self.execute(
                                {"command": {"marshal": marshal.name, "action": "attack",
                                             "target": target, "_strategic_execution": True}},
                                game_state)
                            combat_msg = attack_result.get("message", "")
                            first_step_msg = f" {target} spotted at {next_region}! Engaging!\n\n{combat_msg}"
                        else:
                            first_step_msg = f" {target} spotted at {next_region}. Preparing to engage."
                    break
            if moved_regions:
                order.path = []  # PURSUE recalculates each turn
                if len(moved_regions) > 1:
                    first_step_msg = f" Cavalry charges through {' -> '.join(moved_regions)}."
                else:
                    first_step_msg = f" Moves to {moved_regions[0]}."
                # Check if caught up
                enemy_m = world.get_marshal(target)
                if enemy_m and marshal.location == enemy_m.location:
                    first_step_msg += f" {target} found here!"

        elif strategic_type == "SUPPORT" and path:
            steps = min(movement_range, len(path))
            moved_regions = []
            for i in range(steps):
                if not order.path:
                    break
                next_region = order.path[0]
                enemies = world.get_enemies_in_region(next_region, marshal.nation)
                if enemies:
                    if not moved_regions:
                        # First step blocked
                        blocked_result = self._handle_first_step_blocked(
                            marshal, enemies, next_region, world, game_state)
                        if blocked_result is not None:
                            return blocked_result
                        # Literal reroute — continue
                        first_step_msg = f" Adjusting route to avoid {next_region}."
                        if order.path:
                            next_region = order.path[0]
                            enemies = world.get_enemies_in_region(next_region, marshal.nation)
                            if enemies:
                                break
                        else:
                            break
                    else:
                        break
                move_result = self.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "move",
                        "target": next_region,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                if move_result.get("success"):
                    order.path.pop(0)
                    moved_regions.append(next_region)
                else:
                    break
            if moved_regions:
                if len(moved_regions) > 1:
                    first_step_msg = f" Cavalry charges through {' -> '.join(moved_regions)}."
                else:
                    first_step_msg = f" Moves to {moved_regions[0]}."
            # Record arrival if first step reached ally
            ally_m = world.get_marshal(target)
            if ally_m and marshal.location == ally_m.location and order.arrived_turn is None:
                order.arrived_turn = world.current_turn

        # ── SUPPORT already co-located: set arrived_turn immediately ──
        if strategic_type == "SUPPORT" and order.arrived_turn is None:
            ally_m = world.get_marshal(target)
            if ally_m and marshal.location == ally_m.location:
                order.arrived_turn = world.current_turn

        # ── Build response ────────────────────────────────────────────
        remaining = len(order.path) if order.path else 0
        route_str = " -> ".join([marshal.location] + (order.path or []))

        if strategic_type == "MOVE_TO":
            msg = f"{marshal.name} begins march to {target}. Route: {route_str}.{first_step_msg}"
        elif strategic_type == "PURSUE":
            enemy_m = world.get_marshal(target)
            loc = enemy_m.location if enemy_m else "unknown"
            msg = f"{marshal.name} pursues {target} (at {loc}).{first_step_msg}"
        elif strategic_type == "HOLD":
            hold_loc = target or marshal.location
            msg = f"{marshal.name} will hold {hold_loc}.{first_step_msg}"
        elif strategic_type == "SUPPORT":
            ally_m = world.get_marshal(target)
            loc = ally_m.location if ally_m else "unknown"
            msg = f"{marshal.name} moves to support {target} (at {loc}).{first_step_msg}"
            # A-M3: Berthier advisory — fortified/square marshal cannot reinforce
            if getattr(marshal, 'fortified', False):
                msg += (
                    f"\n\nBerthier: \"Sire, {marshal.name} is ordered to support {target} "
                    f"but is fortified — they cannot march to reinforce from their current "
                    f"position. Consider unfortifying, or rely on the co-location coordination bonus.\""
                )
            elif getattr(marshal, 'square_formation', False):
                msg += (
                    f"\n\nBerthier: \"Sire, {marshal.name} is ordered to support {target} "
                    f"but is in square formation — they cannot march to reinforce. "
                    f"Consider breaking square first.\""
                )
        else:
            msg = f"{marshal.name} received strategic order: {strategic_type}.{first_step_msg}"

        cond_str = ""
        if condition:
            if condition.max_turns:
                cond_str = f" (for {condition.max_turns} turns)"
            elif condition.until_marshal_arrives:
                cond_str = f" (until {condition.until_marshal_arrives} arrives)"
            elif condition.until_relieved:
                cond_str = " (until relieved)"
            elif condition.until_marshal_destroyed:
                cond_str = f" (until {condition.until_marshal_destroyed} destroyed)"

        # Strategic commands cost 2 actions (1 for literal — they follow orders efficiently)
        # Auto-upgrades (e.g., attack→PURSUE) cost 1 (player didn't ask for strategic)
        is_literal = getattr(marshal, 'personality', '') == 'literal'
        is_auto_upgrade = parsed_command.get("auto_upgrade", False)
        strategic_cost = 1 if (is_literal or is_auto_upgrade) else 2

        return {
            "success": True,
            "message": msg + cond_str,
            "strategic_order": True,
            "strategic_type": strategic_type,
            "target": target,
            "path": order.path,
            "remaining_regions": remaining,
            "variable_action_cost": strategic_cost,
        }

    def _handle_strategic_objection_response(
        self,
        marshal,
        command: Dict,
        parsed_command: Dict,
        response: str,
        world,
        game_state: Dict,
        path: List[str],
        target: str,
        strategic_type: str
    ) -> Optional[Dict]:
        """
        Handle player's response to a strategic objection.

        Args:
            marshal: The objecting marshal
            command: Original command dict
            parsed_command: Parsed command dict
            response: "proceed", "preferred", or "compromise"
            world: WorldState
            game_state: Full game state dict
            path: Calculated path for movement
            target: Target of the order
            strategic_type: "HOLD", "PURSUE", "MOVE_TO", "SUPPORT"

        Returns:
            Result dict or None to continue normal processing
        """
        from backend.models.marshal import StrategicOrder, StrategicCondition

        # Get trust and preferred/compromise data from command
        preferred_action = command.get("preferred_action")
        compromise_data = command.get("compromise")
        personality = getattr(marshal, 'personality', 'balanced')

        # V2: Read scaled trust values from the stored objection data
        v2_insist_penalty = command.get("v2_insist_penalty", -10)
        v2_trust_gain = command.get("v2_trust_gain", 3)
        v2_compromise_gain = command.get("v2_compromise_gain", COMPROMISE_TRUST_GAIN)

        if response == "proceed":
            # ═══════════════════════════════════════════════════════════
            # PROCEED (insist): Execute original order, V2 scaled penalty
            # ═══════════════════════════════════════════════════════════
            if hasattr(marshal, 'modify_trust'):
                marshal.modify_trust(v2_insist_penalty)

            # Continue with normal strategic order creation
            # Return None to let flow continue
            return None

        elif response == "preferred":
            # ═══════════════════════════════════════════════════════════
            # PREFERRED (trust): Execute marshal's action, V2 scaled gain, 1 AP
            # ═══════════════════════════════════════════════════════════
            if hasattr(marshal, 'modify_trust'):
                marshal.modify_trust(v2_trust_gain)

            if not preferred_action:
                return {
                    "success": False,
                    "message": "No preferred action available",
                    "variable_action_cost": 0,
                }

            # Execute the preferred tactical action
            pref_action = preferred_action.get("action")
            pref_target = preferred_action.get("target")
            pref_strategic_type = preferred_action.get("strategic_type")

            if pref_strategic_type:
                # Preferred is another strategic command (PURSUE)
                new_parsed = {
                    "command": {
                        "marshal": marshal.name,
                        "action": pref_action,
                        "target": pref_target,
                        "objection_response": "preferred",  # L2 fix: skip re-evaluation
                    },
                    "is_strategic": True,
                    "strategic_type": pref_strategic_type,
                }
                result = self._execute_strategic_command(new_parsed, new_parsed["command"], game_state)
                if result:
                    result["variable_action_cost"] = 1
                    result["trust_change"] = v2_trust_gain
                return result

            else:
                # Preferred is tactical (attack, stance, drill, fortify)
                tactical_cmd = {
                    "marshal": marshal.name,
                    "action": pref_action,
                    "target": pref_target,
                }
                # Use _execute_post_objection to bypass re-entrant objection checks
                parsed_for_post = {"command": tactical_cmd}
                result = self._execute_post_objection(parsed_for_post, game_state, marshal.name)
                result["variable_action_cost"] = 1
                result["trust_change"] = v2_trust_gain
                return result

        elif response == "compromise":
            # ═══════════════════════════════════════════════════════════
            # COMPROMISE: Execute modified order, V2 flat +3, 2 AP
            # ═══════════════════════════════════════════════════════════
            if hasattr(marshal, 'modify_trust'):
                marshal.modify_trust(v2_compromise_gain)

            if not compromise_data:
                return {
                    "success": False,
                    "message": "No compromise available",
                    "variable_action_cost": 0,
                }

            # Build modified strategic order based on compromise type
            condition = None

            # Ney HOLD compromise: timed HOLD (3 turns)
            if compromise_data.get("max_turns"):
                condition = StrategicCondition(
                    max_turns=compromise_data["max_turns"]
                )

            # Davout PURSUE compromise: auto-cancel below ratio
            if compromise_data.get("auto_cancel_below_ratio"):
                condition = StrategicCondition(
                    auto_cancel_below_ratio=compromise_data["auto_cancel_below_ratio"]
                )

            # Davout (cautious) compromise: safe path for MOVE_TO, HOLD, SUPPORT
            if compromise_data.get("safe_path"):
                # Recalculate path avoiding enemies
                # MOVE_TO and HOLD use weighted pathfinding for terrain-aware routes
                enemy_occupied = set()
                for rn in world.regions:
                    if world.get_enemies_in_region(rn, marshal.nation):
                        enemy_occupied.add(rn)

                dest = path[-1] if path else target
                use_weighted = (strategic_type in ("MOVE_TO", "HOLD"))
                safe_pathfinder = world.find_weighted_path if use_weighted else world.find_path
                safe_path = safe_pathfinder(marshal.location, dest, avoid_regions=enemy_occupied)
                if safe_path:
                    path = [r for r in safe_path if r != marshal.location]
                else:
                    return {
                        "success": False,
                        "message": "No safe path available",
                        "variable_action_cost": 0,
                    }

            # Create the modified strategic order
            order = StrategicOrder(
                command_type=strategic_type,
                target=target or "generic",
                target_type=command.get("target_type", "region"),
                started_turn=world.current_turn,
                original_command=parsed_command.get("raw_input", ""),
                path=path,
                condition=condition,
                target_snapshot_location=parsed_command.get("target_snapshot_location"),
                attack_on_arrival=parsed_command.get("attack_on_arrival", False),
                issued_turn=world.current_turn,
                objection_resolved=True,
            )

            # Apply the order
            marshal.strategic_order = order

            # For HOLD, set holding position
            if strategic_type == "HOLD":
                hold_location = target or marshal.location
                if marshal.location == hold_location:
                    if personality == "literal":
                        marshal.holding_position = True
                        marshal.hold_region = hold_location

            # ── Execute first step immediately (same as normal strategic path) ──
            # Without this, compromise orders lose a turn sitting idle.
            first_step_msg = ""
            if order.path:
                movement_range = getattr(marshal, 'movement_range', 1)
                steps = min(movement_range, len(order.path))
                moved_regions = []
                for _i in range(steps):
                    if not order.path:
                        break
                    next_region = order.path[0]
                    enemies = world.get_enemies_in_region(next_region, marshal.nation)
                    if enemies:
                        if not moved_regions:
                            blocked_result = self._handle_first_step_blocked(
                                marshal, enemies, next_region, world, game_state)
                            if blocked_result is not None:
                                return blocked_result
                            first_step_msg = f" Adjusting route to avoid {next_region}."
                            if order.path:
                                next_region = order.path[0]
                                enemies = world.get_enemies_in_region(next_region, marshal.nation)
                                if enemies:
                                    break
                            else:
                                break
                        else:
                            break
                    move_result = self.execute(
                        {"command": {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": next_region,
                            "_strategic_execution": True,
                        }},
                        game_state
                    )
                    if move_result.get("success"):
                        order.path.pop(0)
                        moved_regions.append(next_region)
                    else:
                        break
                if moved_regions:
                    if len(moved_regions) > 1:
                        first_step_msg = f" Cavalry charges through {' -> '.join(moved_regions)}."
                    else:
                        first_step_msg = f" Moves to {moved_regions[0]}."

                # SUPPORT: if first step reached ally, record arrival
                if strategic_type == "SUPPORT":
                    ally = world.get_marshal(target)
                    if ally and marshal.location == ally.location and order.arrived_turn is None:
                        order.arrived_turn = world.current_turn

            # Build success message
            if condition and condition.max_turns:
                if strategic_type == "SUPPORT":
                    msg = f"{marshal.name} agrees to support {target} for {condition.max_turns} turns.{first_step_msg}"
                else:
                    msg = f"{marshal.name} agrees to hold position for {condition.max_turns} turns.{first_step_msg}"
            elif condition and condition.auto_cancel_below_ratio:
                msg = f"{marshal.name} will pursue cautiously, breaking off if odds turn against us.{first_step_msg}"
            elif compromise_data.get("safe_path"):
                msg = f"{marshal.name} will take a safer route to {target}.{first_step_msg}"
            else:
                msg = f"{marshal.name} agrees to the compromise.{first_step_msg}"

            return {
                "success": True,
                "message": msg,
                "strategic_order_created": True,
                "strategic_type": strategic_type,
                "target": target,
                "path": order.path,  # Updated path after first-step movement
                "variable_action_cost": 2,
                "trust_change": v2_compromise_gain,
                "compromise_applied": True,
            }

        # Unknown response
        return {
            "success": False,
            "message": f"Unknown objection response: {response}",
            "variable_action_cost": 0,
        }

    def _handle_first_step_blocked(self, marshal, enemies, blocked_region,
                                   world, game_state) -> Optional[Dict]:
        """
        Handle enemy blocking path on first step of strategic command.

        Personality-based response:
        - AGGRESSIVE: Auto-attack if odds >= 0.7, else ask
        - CAUTIOUS: Always ask
        - LITERAL: Silently reroute

        Returns:
            Dict with interrupt data if player input needed, None if handled automatically
        """
        personality = getattr(marshal, 'personality', 'balanced')
        enemy = enemies[0]
        order = marshal.strategic_order

        if personality == "literal":
            # Silently reroute around ALL enemy regions
            destination = order.target_snapshot_location or order.target
            # For PURSUE/SUPPORT, target is a marshal name — resolve to region
            if destination and destination not in world.regions:
                target_marshal = world.get_marshal(destination)
                if target_marshal:
                    destination = target_marshal.location
            enemy_regions = [
                rn for rn in world.regions
                if world.get_enemies_in_region(rn, marshal.nation)
            ]
            # MOVE_TO and HOLD use weighted pathfinding for terrain-aware rerouting
            use_weighted = (order.command_type in ("MOVE_TO", "HOLD"))
            first_step_pathfinder = world.find_weighted_path if use_weighted else world.find_path
            new_path = first_step_pathfinder(
                marshal.location, destination,
                avoid_regions=enemy_regions
            )
            if new_path:
                order.path = [r for r in new_path if r != marshal.location]
                # Return None — handled automatically, continue with normal flow
                return None  # Caller will set first_step_msg for reroute
            else:
                # No alternate route — break order
                marshal.strategic_order = None
                return {
                    "success": False,
                    "message": f"Path blocked at {blocked_region}, no alternate route. "
                               f"{marshal.name} awaits new orders.",
                    "order_cleared": True,
                    "first_step_blocked": True,
                    "variable_action_cost": 1,
                }

        elif personality == "aggressive":
            ratio = marshal.strength / max(1, enemy.strength)
            if ratio >= 0.7:
                # Auto-attack — favorable odds
                result = self.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "attack",
                        "target": enemy.name,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                # Return attack result — order continues or breaks based on combat
                combat_msg = result.get("message", "")
                if result.get("success"):
                    return {
                        "success": True,
                        "message": f"{marshal.name}: '{enemy.name} bars the way!' "
                                   f"Engaging!\n\n{combat_msg}",
                        "strategic_order": True,
                        "strategic_type": order.command_type,
                        "first_step_combat": True,
                    }
                return result

            # Bad odds — ask player
            marshal.pending_interrupt = {
                "interrupt_type": "contact_bad_odds",
                "enemy": enemy.name,
                "location": blocked_region,
                "is_first_step": True,
                "options": ["attack_anyway", "go_around", "hold_position", "cancel_order"]
            }
            return {
                "success": True,
                "requires_input": True,
                "pending_interrupt": marshal.pending_interrupt,
                "message": f"{marshal.name}: '{enemy.name} blocks the path at {blocked_region}. "
                           f"Odds unfavorable. Your orders?'",
                "strategic_order": True,
                "strategic_type": order.command_type,
                "first_step_interrupt": True,
                "variable_action_cost": 1,
            }

        else:  # cautious, balanced, loyal — always ask
            marshal.pending_interrupt = {
                "interrupt_type": "contact",
                "enemy": enemy.name,
                "location": blocked_region,
                "is_first_step": True,
                "options": ["attack", "go_around", "hold_position", "cancel_order"]
            }
            return {
                "success": True,
                "requires_input": True,
                "pending_interrupt": marshal.pending_interrupt,
                "message": f"{marshal.name}: 'Enemy at {blocked_region}. "
                           f"How shall I proceed, Sire?'",
                "strategic_order": True,
                "strategic_type": order.command_type,
                "first_step_interrupt": True,
                "variable_action_cost": 1,
            }

    def _execute_move(self, marshal, target, world: WorldState, game_state) -> Dict:
        """Execute a move order."""
        # Auto-break square formation (Session 67)
        self._auto_break_square(marshal, "move")

        # ════════════════════════════════════════════════════════════
        # DRILL STATE CHECK: Handle drilling marshal trying to move
        # ════════════════════════════════════════════════════════════
        drill_cancelled_message = ""
        if getattr(marshal, 'drilling', False):
            if getattr(marshal, 'drilling_locked', False):
                # Turn 2: Locked in drill, cannot move
                return {
                    "success": False,
                    "message": f"{marshal.name} is locked in drill formation and cannot move. Only RETREAT is allowed.",
                    "drilling_locked": True
                }
            else:
                # Turn 1: Can move but drill is cancelled
                marshal.drilling = False
                marshal.drill_complete_turn = -1
                drill_cancelled_message = f"⚠️ DRILL CANCELLED: {marshal.name}'s drill was interrupted - troops dispersed before training completed.\n\n"

        if not target:
            return {
                "success": False,
                "message": "Move order requires a destination"
            }

        # Use fuzzy matching for region lookup
        target_region, error = self._fuzzy_match_region(target, world)
        if error:
            return error

        # Get the corrected target name from fuzzy match
        target_name = target_region.name if hasattr(target_region, 'name') else target

        current_region = world.get_region(marshal.location)

        # Already there?
        if marshal.location == target_name:
            return {
                "success": False,
                "message": f"{marshal.name} is already in {target_name}."
            }

        # ════════════════════════════════════════════════════════════
        # ENEMY ENGAGEMENT CHECK: Cannot advance through enemies
        # If enemy marshal in current region, can only retreat to friendly territory
        # ════════════════════════════════════════════════════════════
        marshals_here = world.get_marshals_in_region(marshal.location)
        enemies_here = [m for m in marshals_here if m.nation != marshal.nation and world.is_at_war(marshal.nation, m.nation)]

        if enemies_here:
            # Engaged with enemy - can only move to regions controlled by marshal's nation
            if target_region.controller != marshal.nation:
                return {
                    "success": False,
                    "message": "Cannot advance while engaged with enemy forces. You may retreat to friendly territory.",
                    "engaged_with": [e.name for e in enemies_here],
                    "suggestion": f"Friendly regions adjacent: {', '.join([r for r in current_region.adjacent_regions if world.get_region(r) and world.get_region(r).controller == marshal.nation])}"
                }

        # ════════════════════════════════════════════════════════════
        # DESTINATION ENEMY CHECK: Cannot MOVE into enemy-occupied region
        # Must use ATTACK to enter regions with enemy forces
        # FOG-AWARE (Session 37): Only block if player can SEE enemies there.
        # If fogged, marshal walks in blind and discovers engagement on arrival.
        # ════════════════════════════════════════════════════════════
        marshals_at_dest = world.get_marshals_in_region(target_name)
        enemies_at_dest = [m for m in marshals_at_dest if m.nation != marshal.nation and m.strength > 0 and world.is_at_war(marshal.nation, m.nation)]

        if enemies_at_dest:
            # Fog check: player marshals only blocked if destination is visible
            can_see_enemies = True
            if marshal.nation == world.player_nation and hasattr(world, 'get_region_intel'):
                from backend.models.intel import FULL, PARTIAL
                dest_intel = world.get_region_intel(target_name)
                can_see_enemies = dest_intel.visibility in (FULL, PARTIAL)

            if can_see_enemies:
                enemy_names = [e.name for e in enemies_at_dest]
                return {
                    "success": False,
                    "message": f"Cannot move into {target_name} - enemy forces present! Use ATTACK to engage {', '.join(enemy_names)}.",
                    "enemies_at_destination": enemy_names,
                    "suggestion": f"Try: '{marshal.name}, attack {enemy_names[0]}'"
                }
            # Fogged: marshal walks in blind — will discover enemies on arrival

        # ════════════════════════════════════════════════════════════
        # DIPLOMATIC MOVEMENT RESTRICTION (Phase 8 Session 2)
        # Cannot enter territory of nations at PEACE/NON_AGGRESSION/ARMISTICE
        # unless OPEN_BORDERS or above. WAR allows entry (combat handles it).
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.diplomacy import can_enter_territory
        dest_controller = target_region.controller if hasattr(target_region, 'controller') else None
        if dest_controller and dest_controller != marshal.nation:
            if not can_enter_territory(world, marshal.nation, dest_controller):
                state = world.get_diplomatic_state(marshal.nation, dest_controller)
                return {
                    "success": False,
                    "message": f"Cannot enter {target_name} — it is controlled by {dest_controller} "
                               f"(diplomatic state: {state}). Open borders or higher required.",
                }

        distance = world.get_distance(marshal.location, target_name)
        move_range = getattr(marshal, 'movement_range', 1)

        # Check if destination is within movement range
        if distance > move_range:
            # Cannot auto-upgrade to strategic march while engaged
            if enemies_here:
                return {
                    "success": False,
                    "message": f"{marshal.name} is engaged with enemy forces and cannot begin a strategic march. Deal with the engagement first.",
                    "engaged_with": [e.name for e in enemies_here],
                    "suggestion": f"Try: '{marshal.name}, attack {enemies_here[0].name}' or '{marshal.name}, retreat'"
                }
            # Auto-upgrade to strategic MOVE_TO for distant regions
            # Pre-check: strategic commands cost 2 AP (1 for literal)
            is_literal = getattr(marshal, 'personality', '') == 'literal'
            strategic_cost = 1 if is_literal else 2
            if marshal.nation == world.player_nation and world.actions_remaining < strategic_cost:
                return {
                    "success": False,
                    "message": f"Not enough actions for a strategic march! Need {strategic_cost}, have {world.actions_remaining}.",
                    "actions_remaining": int(world.actions_remaining),
                    "action_summary": world.get_action_summary()
                }
            path = world.find_weighted_path(marshal.location, target_name)
            if path and len(path) > 1:
                order = StrategicOrder(
                    command_type="MOVE_TO",
                    target=target_name,
                    target_type="region",
                    started_turn=world.current_turn,
                    issued_turn=world.current_turn,
                    original_command=f"move to {target_name}",
                    path=path,
                )
                marshal.strategic_order = order

                # Execute first step immediately (mirrors _execute_strategic_command)
                movement_range = getattr(marshal, 'movement_range', 1)
                steps = min(movement_range, len(path) - 1)  # path[0] is current location
                regions_moved = []
                print(f"[STRATEGIC INIT] {marshal.name}: Auto-upgrade MOVE_TO, path={path}, steps={steps}")
                for i in range(steps):
                    next_region = path[1]  # Always path[1] since path shrinks after move
                    enemies_blocking = world.get_enemies_in_region(next_region, marshal.nation)
                    if enemies_blocking:
                        print(f"[STRATEGIC INIT] {marshal.name}: First step BLOCKED by enemies at {next_region}")
                        if not regions_moved:
                            # First step blocked — personality-based response
                            blocked_result = self._handle_first_step_blocked(
                                marshal, enemies_blocking, next_region, world, game_state)
                            if blocked_result is not None:
                                return blocked_result  # Interrupt or combat result
                            # Literal reroute succeeded — update local path ref and continue
                            path = [marshal.location] + list(order.path)
                            if order.path:
                                next_region = order.path[0]
                                enemies_blocking = world.get_enemies_in_region(next_region, marshal.nation)
                                if enemies_blocking:
                                    break  # Still blocked after reroute
                                # Fall through to move along rerouted path
                            else:
                                break  # No path left after reroute
                        else:
                            break  # Mid-march block
                    move_result = self.execute(
                        {"command": {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": next_region,
                            "_strategic_execution": True,
                        }}, game_state)
                    if move_result.get("success"):
                        regions_moved.append(next_region)
                        order.path = order.path[1:]  # Consume path step
                        print(f"[STRATEGIC INIT] {marshal.name}: Moved to {next_region} OK")
                    else:
                        print(f"[STRATEGIC INIT] {marshal.name}: Move FAILED - {move_result.get('message', '?')}")
                        break

                # Transit intel: regions passed through but not ended at get PARTIAL
                if len(regions_moved) > 1 and marshal.nation == world.player_nation:
                    for transit_region in regions_moved[:-1]:
                        world.update_intel_from_transit(transit_region, world.current_turn)

                moved_str = f" Moved to {' -> '.join(regions_moved)}." if regions_moved else ""
                return {
                    "success": True,
                    "message": f"{marshal.name} begins marching to {target_name} (distance: {distance}).{moved_str} Route: {' -> '.join(order.path)}.",
                    "strategic_upgrade": True,
                    "strategic_type": "MOVE_TO",
                    "path": order.path,
                    "variable_action_cost": strategic_cost,
                }
            else:
                marshal_type = "cavalry" if move_range == 2 else "infantry"
                return {
                    "success": False,
                    "message": f"{marshal.location} is too far from {target_name} (distance: {distance}, {marshal_type} range: {move_range})",
                    "suggestion": f"Adjacent regions: {', '.join(current_region.adjacent_regions)}"
                }

        # For 2-tile moves (cavalry), verify there's a valid path through adjacent region
        if distance == 2:
            # Find path through an intermediate region
            intermediate = None
            for adj_name in current_region.adjacent_regions:
                adj_region = world.get_region(adj_name)
                if adj_region and target_name in adj_region.adjacent_regions:
                    intermediate = adj_name
                    break

            if not intermediate:
                return {
                    "success": False,
                    "message": f"No valid path from {marshal.location} to {target_name}",
                    "suggestion": f"Adjacent regions: {', '.join(current_region.adjacent_regions)}"
                }

        old_location = marshal.location
        marshal.move_to(target_name)

        # Artillery: Mark as having moved this turn (blocks attacking)
        # Also reset bombardment streak (repositioning breaks sustained fire)
        if getattr(marshal, 'artillery', False):
            marshal.moved_this_turn = True
            marshal.last_bombardment_target = None
            marshal.bombardment_streak = 0

        # V2a: Reset idle tracking on move
        marshal.idle_turns = 0
        marshal._acted_this_turn = True

        # Refresh visibility immediately so destination (FULL) and new adjacents
        # (PARTIAL) are available for capture hints and the UI this turn
        if marshal.nation == world.player_nation:
            world.calculate_visibility()

        move_message = f"{marshal.name} moves from {old_location} to {target_name}"
        if drill_cancelled_message:
            move_message = drill_cancelled_message + move_message

        # Fog discovery: marshal walked into region with enemies they couldn't see
        discovered_enemies = world.get_enemies_in_region(target_name, marshal.nation)
        fog_discovery = False
        if discovered_enemies and marshal.nation == world.player_nation:
            fog_discovery = True
            enemy_names = [e.name for e in discovered_enemies]
            move_message += f". ENEMY FORCES DISCOVERED! {', '.join(enemy_names)} present in {target_name}!"
            move_message += f" {marshal.name} is now engaged — attack or retreat."

        events = [{
            "type": "move",
            "marshal": marshal.name,
            "from": old_location,
            "to": target_name
        }]

        # Transit intel: cavalry passing through intermediate region gets PARTIAL snapshot
        if distance == 2 and intermediate and marshal.nation == world.player_nation:
            world.update_intel_from_transit(intermediate, world.current_turn)

        # Movement attrition (Phase 6.2.F)
        # Cavalry 2-tile moves: attrition for BOTH intermediate + destination
        if distance == 2 and intermediate:
            attrition_intermediate = self._calculate_movement_attrition(marshal, intermediate, world)
            attrition_dest = self._calculate_movement_attrition(marshal, target_name, world)
            total_march = attrition_intermediate["march_losses"] + attrition_dest["march_losses"]
            total_harassment = attrition_intermediate["harassment_losses"] + attrition_dest["harassment_losses"]
            total_all = attrition_intermediate["total_losses"] + attrition_dest["total_losses"]
            any_depot_bonus = attrition_intermediate.get("depot_bonus") or attrition_dest.get("depot_bonus")
            if total_all > 0:
                attrition_msg = f" ({total_march:,} lost to march"
                if any_depot_bonus:
                    attrition_msg += " — forward supply lines reduce losses"
                if total_harassment > 0:
                    attrition_msg += f", {total_harassment:,} to enemy harassment"
                attrition_msg += ")"
                move_message += attrition_msg
                events[0]["march_losses"] = int(total_all)
        else:
            attrition_info = self._calculate_movement_attrition(marshal, target_name, world)
            if attrition_info["total_losses"] > 0:
                attrition_msg = f" ({attrition_info['march_losses']:,} lost to march"
                if attrition_info.get("depot_bonus"):
                    attrition_msg += " — forward supply lines reduce losses"
                if attrition_info["harassment_losses"] > 0:
                    attrition_msg += f", {attrition_info['harassment_losses']:,} to enemy harassment"
                attrition_msg += ")"
                move_message += attrition_msg
                events[0]["march_losses"] = int(attrition_info["total_losses"])

        # Add drill_cancelled event if drill was interrupted
        if drill_cancelled_message:
            events.insert(0, {
                "type": "drill_cancelled",
                "marshal": marshal.name,
                "reason": "move"
            })

        # ════════════════════════════════════════════════════════════
        # CAPTURE HINT (Session 31): Suggest attacking undefended enemy regions
        # Fog-aware: only hint about regions with FULL or PARTIAL visibility
        # ════════════════════════════════════════════════════════════
        capture_hints = []
        if marshal.nation == world.player_nation:
            from backend.models.intel import FULL, PARTIAL
            dest_region = world.get_region(target_name)
            if dest_region:
                for adj_name in dest_region.adjacent_regions:
                    adj_region = world.get_region(adj_name)
                    if not adj_region:
                        continue
                    # Must be enemy-controlled
                    if not adj_region.controller or adj_region.controller == marshal.nation:
                        continue
                    # Fog-aware: check visibility
                    intel = world.get_region_intel(adj_name)
                    if intel.visibility not in (FULL, PARTIAL):
                        continue
                    # Check if undefended: no enemy marshals AND no meaningful garrison
                    enemies_there = world.get_marshals_in_region(adj_name)
                    enemy_marshals = [m for m in enemies_there if m.nation != marshal.nation and m.strength > 0]
                    has_garrison = adj_region.garrison_strength >= 5000 or (
                        adj_region.garrison_detachment and adj_region.garrison_strength > 0
                    )
                    if not enemy_marshals and not has_garrison:
                        capture_hints.append(adj_name)

        capture_hint_msg = ""
        if capture_hints:
            if len(capture_hints) == 1:
                capture_hint_msg = f"\n[HINT] {capture_hints[0]} is undefended — attack to capture it!"
            else:
                capture_hint_msg = f"\n[HINT] Undefended regions nearby: {', '.join(capture_hints)} — attack to capture!"

        result = {
            "success": True,
            "message": move_message + capture_hint_msg,
            "drill_cancelled": bool(drill_cancelled_message),
            "events": events,
            "new_state": game_state
        }
        if fog_discovery:
            result["fog_discovery"] = True
            result["discovered_enemies"] = [e.name for e in discovered_enemies]
        if capture_hints:
            result["capture_hints"] = capture_hints
        return result

    def _execute_scout(self, marshal, target, world: WorldState, game_state) -> Dict:
        """
        Execute a scout/reconnaissance order.

        TODO (Phase 6/6.5): Godot UI for scouting:
        - Visual fog of war reveal on map (Phase 6)
        - Enemy unit icons appearing with scouted info (Phase 6.5)
        - Scout report popup/panel with detailed intel (Phase 6.5)
        - Animated scout movement to target region (Phase 6.5)
        """
        current_region = world.get_region(marshal.location)

        if target:
            # Scout specific region - use fuzzy matching
            target_region, error = self._fuzzy_match_region(target, world)
            if error:
                return error

            # Get the corrected target name from fuzzy match
            target_name = target_region.name if hasattr(target_region, 'name') else target

            distance = world.get_distance(marshal.location, target_name)

            # ════════════════════════════════════════════════════════════
            # PERSONALITY-SPECIFIC SCOUT RANGE (Phase 2.8)
            # Davout (cautious) gets +1 scout range
            # ════════════════════════════════════════════════════════════
            from backend.models.personality_modifiers import get_scout_range_bonus
            base_scout_range = 2
            scout_bonus = get_scout_range_bonus(getattr(marshal, 'personality', 'unknown'))
            max_scout_range = base_scout_range + scout_bonus

            if distance > max_scout_range:
                range_msg = f"Can only scout regions within {max_scout_range} moves"
                if scout_bonus > 0:
                    range_msg += f" (Iron Marshal: +{scout_bonus} range)"
                return {
                    "success": False,
                    "message": f"{target_name} is too far to scout (distance: {distance})",
                    "suggestion": range_msg
                }

            # Scout report
            controller = target_region.controller or "Unknown"
            marshals_there = world.get_marshals_in_region(target_name)

            # Terrain info
            terrain = getattr(target_region, 'terrain', 'plains')
            defense_pct = int(TERRAIN_DEFENSE_BONUS.get(terrain, 0.0) * 100)
            terrain_display = terrain.replace("_", " ").title()
            terrain_msg = f"Terrain: {terrain_display}"
            if defense_pct > 0:
                terrain_msg += f" (+{defense_pct}% defense)"

            # Detailed intel on enemies
            enemy_intel = []
            for m in marshals_there:
                if m.nation != world.player_nation:
                    enemy_intel.append(f"{m.name} ({m.nation}): ~{m.strength:,} troops")

            intel_msg = f"Controlled by {controller}. {terrain_msg}. "
            if enemy_intel:
                intel_msg += f"Enemy forces: {'; '.join(enemy_intel)}"
            else:
                intel_msg += "No enemy forces detected."

            # Fog of War (Session 34A): Persist FULL intel on scouted region
            world.update_intel_from_scout(target_name, world.current_turn)

            return {
                "success": True,
                "message": f"{marshal.name} scouts {target_name}: {intel_msg}",
                "events": [{
                    "type": "scout",
                    "marshal": marshal.name,
                    "target": target_name,
                    "intel": {
                        "controller": controller,
                        "terrain": terrain,
                        "terrain_display": terrain_display,
                        "defense_bonus": defense_pct,
                        "enemies": enemy_intel
                    }
                }],
                "new_state": game_state
            }
        else:
            # Scout all adjacent regions
            adjacent_intel = []
            for region_name in current_region.adjacent_regions:
                region = world.get_region(region_name)
                controller = region.controller or "Unknown"
                terrain = getattr(region, 'terrain', 'plains')
                enemies = [m for m in world.get_marshals_in_region(region_name)
                          if m.nation != world.player_nation]
                adjacent_intel.append({
                    "region": region_name,
                    "controller": controller,
                    "terrain": terrain,
                    "enemy_count": len(enemies)
                })

            # Fog of War (Session 34A): Adjacent scan refreshes PARTIAL on each adjacent region.
            # This is NOT the same as a targeted scout (which grants FULL).
            # Adjacent intel is already handled by calculate_visibility() during turn
            # processing, but the scout action provides an immediate snapshot.
            from backend.models.intel import PARTIAL
            for info in adjacent_intel:
                adj_region_name = info["region"]
                adj_intel = world.get_region_intel(adj_region_name)
                adj_enemies = [m for m in world.get_marshals_in_region(adj_region_name)
                               if m.nation != world.player_nation and m.strength > 0]
                adj_marshal_data = world._build_marshal_snapshot(adj_enemies, full=False)
                adj_total = sum(m.strength for m in adj_enemies)
                adj_intel.refresh(
                    visibility=PARTIAL,
                    source="scout",
                    turn=world.current_turn,
                    marshals=adj_marshal_data,
                    total_strength=adj_total,
                )

            intel_summary = ", ".join([
                f"{info['region']} ({info['controller']}, {info['terrain'].replace('_', ' ').title()}" +
                (f", {info['enemy_count']} enemies)" if info['enemy_count'] > 0 else ")")
                for info in adjacent_intel
            ])

            return {
                "success": True,
                "message": f"{marshal.name} scouts from {marshal.location}: {intel_summary}",
                "events": [{
                    "type": "scout",
                    "marshal": marshal.name,
                    "intel": adjacent_intel
                }],
                "new_state": game_state
            }

    def _execute_general_attack(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute general attack - finds nearest enemy automatically.

        If no marshal can attack (all out of range), moves the closest
        marshal toward the nearest enemy instead.
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        player_marshals = world.get_player_marshals()

        if not player_marshals:
            return {"success": False, "message": "No marshals available to attack"}

        # Track all combat-ready marshals and their nearest enemies
        combat_ready = []  # [(marshal, enemy, distance)]
        out_of_range = []  # [(marshal, enemy, distance)] - for fallback move
        filtered_out = []  # Explanations for non-combat-ready

        for marshal in player_marshals:
            # Filter out dead/weak marshals
            if marshal.strength <= 0:
                filtered_out.append(f"{marshal.name} (eliminated)")
                continue
            elif marshal.strength < 1000:
                filtered_out.append(f"{marshal.name} ({marshal.strength:,} troops - too weak)")
                continue

            # Check if fortified or drilling (can't attack)
            if getattr(marshal, 'fortified', False):
                filtered_out.append(f"{marshal.name} (fortified - unfortify first)")
                continue
            if getattr(marshal, 'drilling_locked', False):
                filtered_out.append(f"{marshal.name} (locked in drill)")
                continue

            # NOTE: Phase 5.2 strategic commands are complete, but personality-aware
            # target selection (interpret_by_personality) is not yet implemented here.
            # Future improvement: Aggressive picks strongest, Cautious picks weakest,
            # Literal picks nearest (current behavior for all).
            nearest = world.find_nearest_enemy(marshal.location)
            if nearest:
                enemy, distance = nearest
                # Skip dead enemies
                if enemy.strength <= 0:
                    continue

                if distance <= 1:  # Can attack (adjacent or same region)
                    combat_ready.append((marshal, enemy, distance))
                else:  # Out of range but can move toward
                    out_of_range.append((marshal, enemy, distance))

        # ════════════════════════════════════════════════════════════════
        # CASE 1: Someone can attack - execute the attack
        # ════════════════════════════════════════════════════════════════
        if combat_ready:
            # Sort by distance (prefer closer), then strength (prefer stronger)
            combat_ready.sort(key=lambda x: (x[2], -x[0].strength))
            best_marshal, best_enemy, best_distance = combat_ready[0]

            # Build explanation if others were filtered
            explanation = ""
            if filtered_out:
                explanation = f"[NOTE: {', '.join(filtered_out)}]\n"
            explanation += f"{best_marshal.name} ({best_marshal.strength:,} troops) attacks!\n\n"

            # Execute the attack (rest of original logic follows below)
            return self._execute_general_attack_combat(
                best_marshal, best_enemy, world, explanation, game_state
            )

        # ════════════════════════════════════════════════════════════════
        # CASE 2: No one can attack - move closest marshal toward enemy
        # ════════════════════════════════════════════════════════════════
        if out_of_range:
            # Sort by distance to enemy (closest first)
            out_of_range.sort(key=lambda x: x[2])
            closest_marshal, target_enemy, distance = out_of_range[0]

            # Find path toward enemy
            path = world.find_path(closest_marshal.location, target_enemy.location)

            if path and len(path) > 1:
                # Move to next region on path
                next_region = path[1]  # path[0] is current location

                # Execute the move
                old_location = closest_marshal.location
                closest_marshal.location = next_region

                remaining_distance = distance - 1

                message = (
                    f"No marshals in attack range!\n\n"
                    f"{closest_marshal.name} advances toward {target_enemy.name}:\n"
                    f"  {old_location} -> {next_region}\n"
                    f"  Distance to enemy: {remaining_distance} region(s)\n\n"
                )

                if remaining_distance <= 1:
                    message += f"[{closest_marshal.name} will be in attack range next action!]"
                else:
                    message += f"[{remaining_distance - 1} more move(s) needed to reach attack range]"

                if filtered_out:
                    message = f"[NOTE: {', '.join(filtered_out)}]\n\n" + message

                return {
                    "success": True,
                    "message": message,
                    "moved": True,
                    "marshal": closest_marshal.name,
                    "from": old_location,
                    "to": next_region,
                    "target_enemy": target_enemy.name,
                    "events": [{
                        "type": "move_toward_enemy",
                        "marshal": closest_marshal.name,
                        "from": old_location,
                        "to": next_region,
                        "target": target_enemy.name,
                        "distance_remaining": remaining_distance
                    }]
                }
            else:
                return {
                    "success": False,
                    "message": f"No path found from {closest_marshal.location} to {target_enemy.location}!"
                }

        # ════════════════════════════════════════════════════════════════
        # CASE 3: No combat-ready marshals at all
        # ════════════════════════════════════════════════════════════════
        if filtered_out:
            return {
                "success": False,
                "message": f"No combat-ready marshals!\n{', '.join(filtered_out)}"
            }

        return {
            "success": False,
            "message": "No enemies found! You may have won the campaign."
        }

    def _execute_general_attack_combat(
        self,
        best_marshal,
        best_enemy,
        world: 'WorldState',
        explanation: str,
        game_state: Dict
    ) -> Dict:
        """Helper to execute the actual combat for general attack.
        Delegates to _execute_attack() for full Phase 7 coordination,
        reinforcements, casualty distribution, relationships, and reports.
        (Gate 4 fix: same pattern as _execute_auto_assign_attack.)
        """
        # Delegate to _execute_attack with full coordination support
        attack_result = self._execute_attack(
            best_marshal, best_enemy.name, world, game_state)

        # Prepend the explanation text (marshal selection reasoning)
        if attack_result.get("message"):
            attack_result["message"] = explanation + attack_result["message"]

        # Tag as auto-assigned for UI display
        if attack_result.get("events"):
            for ev in attack_result["events"]:
                ev["auto_assigned"] = True

        return attack_result

    def _execute_auto_assign_attack(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute attack with auto-assigned marshal.
        Example: "Attack Wellington" or "Attack Rhine"
        Delegates to _execute_attack() after finding nearest marshal (Building Blocks).
        """
        target = command.get("target")
        world: WorldState = game_state.get("world")

        if not world or not target:
            return {"success": False, "message": "Error: No target or world state"}

        # FIRST: Try to find target as enemy marshal name
        enemy = world.get_enemy_by_name(target)

        if enemy:
            if enemy.strength <= 0:
                return {
                    "success": False,
                    "message": f"{target} has already been destroyed!"
                }
            # Found enemy marshal — find nearest player marshal to attack
            result = world.find_nearest_marshal_to_region(enemy.location)
            if not result:
                return {"success": False, "message": f"No marshals in range of {target}"}
            nearest_marshal, distance = result

            # Delegate to _execute_attack with full coordination support
            attack_result = self._execute_attack(nearest_marshal, target, world, game_state)
            # Tag as auto-assigned for UI display
            if attack_result.get("events"):
                for ev in attack_result["events"]:
                    ev["auto_assigned"] = True
            return attack_result

        # SECOND: Check if target is a region name with fuzzy matching
        target_region, error = self._fuzzy_match_region(target, world)

        if error:
            return error

        target_name = target_region.name if hasattr(target_region, 'name') else target

        # Find nearest marshal to this region
        result = world.find_nearest_marshal_to_region(target_name)

        if not result:
            return {"success": False, "message": f"No marshals in range of {target_name}"}

        nearest_marshal, distance = result

        # Delegate to _execute_attack with full coordination support
        attack_result = self._execute_attack(nearest_marshal, target_name, world, game_state)
        # Tag as auto-assigned for UI display
        if attack_result.get("events"):
            for ev in attack_result["events"]:
                ev["auto_assigned"] = True
        return attack_result

    def _execute_auto_assign_bombardment(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute bombardment with auto-assigned artillery marshal.
        Example: "bombard Rhineland" or "bombard Wellington" (no marshal named).
        Selects nearest artillery marshal with bombardments remaining.
        Future-proof: supports multiple artillery marshals.
        """
        target = command.get("target")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        # Find all player artillery marshals
        artillery_marshals = [
            m for m in world.get_player_marshals()
            if getattr(m, 'artillery', False)
            and m.strength > 0
        ]

        if not artillery_marshals:
            return {
                "success": False,
                "message": "No artillery marshals available for bombardment."
            }

        # Filter to those with bombardments remaining this turn
        ready_artillery = [
            m for m in artillery_marshals
            if getattr(m, 'bombardments_this_turn', 0) < 2
        ]

        if not ready_artillery:
            names = ", ".join(m.name for m in artillery_marshals)
            return {
                "success": False,
                "message": f"All artillery marshals have used their bombardments this turn. ({names}: max 2 per turn)"
            }

        if not target:
            # "bombard" alone with no target — pick nearest enemy for closest artillery
            best_marshal = None
            best_enemy = None
            best_distance = 999
            for m in ready_artillery:
                nearest = world.find_nearest_enemy(m.location)
                if nearest:
                    enemy, dist = nearest
                    if enemy.strength > 0 and dist <= 2 and dist < best_distance:
                        best_marshal = m
                        best_enemy = enemy
                        best_distance = dist
            if not best_marshal:
                return {
                    "success": False,
                    "message": "No enemies within bombardment range of any artillery marshal.",
                    "suggestion": "Name a target: 'bombard Rhineland' or 'bombard Wellington'"
                }
            target = best_enemy.name

        # Route through the specific attack executor with auto-selected artillery marshal
        # Build a command dict as if the player named the marshal
        routed_command = dict(command)
        # Resolve target location for distance sorting
        target_location = None
        enemy = world.get_enemy_by_name(target)
        if enemy and enemy.strength > 0:
            target_location = enemy.location
        else:
            target_region, error = self._fuzzy_match_region(target, world)
            if not error and target_region:
                target_location = target_region.name if hasattr(target_region, 'name') else target

        if not target_location:
            return {
                "success": False,
                "message": f"Unknown bombardment target: {target}"
            }

        # Sort artillery by distance to target (nearest first), strength as tiebreaker
        candidates = []
        for m in ready_artillery:
            dist = world.get_distance(m.location, target_location)
            if dist is not None and dist <= 2:  # Bombardment range: adjacent (1) or same region
                candidates.append((m, dist))

        if not candidates:
            names = ", ".join(f"{m.name} at {m.location}" for m in ready_artillery)
            return {
                "success": False,
                "message": f"No artillery in bombardment range of {target}.",
                "suggestion": f"Available artillery: {names}"
            }

        candidates.sort(key=lambda x: (x[1], -x[0].strength))
        chosen_marshal = candidates[0][0]

        # Route to specific attack with chosen artillery marshal
        routed_command["marshal"] = chosen_marshal.name
        routed_command["type"] = "specific"
        return self._execute_specific(routed_command, game_state)

    def _execute_auto_assign_scout(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute scout with auto-assigned marshal.
        Example: "scout Rhineland" (no marshal named).
        Selects nearest player marshal within scout range of target.
        """
        target = command.get("target")
        world: WorldState = game_state.get("world")

        if not world or not target:
            return {"success": False, "message": "Error: No target or world state"}

        # Fuzzy match target region
        target_region, error = self._fuzzy_match_region(target, world)
        if error:
            return error

        target_name = target_region.name if hasattr(target_region, 'name') else target

        # Find player marshals that can scout this target
        from backend.models.personality_modifiers import get_scout_range_bonus
        base_scout_range = 2

        player_marshals = world.get_player_marshals()
        candidates = []  # (marshal, distance)

        for m in player_marshals:
            if m.strength <= 0:
                continue
            # Check retreat/broken blocking
            if getattr(m, 'retreating', False) and getattr(m, 'retreat_recovery', 0) < 3:
                continue
            if getattr(m, 'broken', False):
                continue

            scout_bonus = get_scout_range_bonus(getattr(m, 'personality', 'unknown'))
            max_range = base_scout_range + scout_bonus
            dist = world.get_distance(m.location, target_name)
            if dist is not None and dist <= max_range:
                candidates.append((m, dist))

        if not candidates:
            return {
                "success": False,
                "message": f"No marshals in scout range of {target_name}.",
                "suggestion": "Name a specific marshal or move closer first."
            }

        # Sort by distance (nearest first), then strength as tiebreaker
        candidates.sort(key=lambda x: (x[1], -x[0].strength))
        chosen_marshal = candidates[0][0]

        # Route to specific scout with chosen marshal
        routed_command = dict(command)
        routed_command["marshal"] = chosen_marshal.name
        routed_command["type"] = "specific"
        return self._execute_specific(routed_command, game_state)

    def _execute_general_retreat(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute general retreat - retreat ALL marshals that are in danger.

        BUG-003 FIX: Only retreats marshals that have enemies nearby, not all marshals.
        BUG-010 FIX: Uses is_in_danger() to check threat properly.
        Uses proper retreat action (sets retreating state with recovery).
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        player_marshals = world.get_player_marshals()

        if not player_marshals:
            return {"success": False, "message": "No marshals to retreat"}

        # BUG-010 FIX: Find marshals that are actually in danger
        marshals_in_danger = []
        capital = world.player_capital
        for marshal in player_marshals:
            if capital and marshal.location == capital:
                continue
            if getattr(marshal, 'retreating', False):
                continue  # Already retreating

            # Use the new is_in_danger() method
            if world.is_in_danger(marshal.name):
                marshals_in_danger.append(marshal)

        if not marshals_in_danger:
            return {
                "success": False,
                "message": "No marshals are in danger. None need to retreat.",
                "suggestion": "Use 'move' to reposition marshals instead."
            }

        # Execute retreat for each marshal in danger
        retreated = []
        failed = []
        for marshal in marshals_in_danger:
            result = self._execute_retreat_action(marshal, world, game_state)
            if result.get("success"):
                retreated.append(f"{marshal.name} falling back!")
            else:
                # Capture failure reason (e.g., surrounded)
                failed.append(f"{marshal.name}: {result.get('message', 'failed')}")

        if not retreated:
            fail_msg = " | ".join(failed) if failed else "Could not retreat any marshals."
            return {
                "success": False,
                "message": fail_msg,
                "events": []
            }

        message = f"General retreat ordered! {' '.join(retreated)}"
        if failed:
            message += f" (Failed: {', '.join([f.split(':')[0] for f in failed])})"

        return {
            "success": True,
            "message": message,
            "events": [{
                "type": "general_retreat",
                "affected_marshals": len(retreated),
                "retreating": [m.name for m in marshals_in_danger if any(m.name in r for r in retreated)]
            }],
            "new_state": game_state
        }

    def _execute_general_defensive(self, command: Dict, game_state: Dict) -> Dict:
        """Execute general defensive stance (all forces defend)."""
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        player_marshals = world.get_player_marshals()

        if not player_marshals:
            return {"success": False, "message": "No marshals available"}

        marshal_names = [m.name for m in player_marshals]

        return {
            "success": True,
            "message": f"All forces take defensive positions: {', '.join(marshal_names)}",
            "events": [{
                "type": "defend",
                "marshals": marshal_names,
                "effect": "All regions get +30% defensive bonus next turn"
            }],
            "new_state": game_state
        }

    # ═══════════════════════════════════════════════════════════════════
    # ECONOMY COMMAND (Phase 6.2.G)
    # Free action showing treasury, income, upkeep breakdown
    # ═══════════════════════════════════════════════════════════════════

    def _execute_economy(self, command: Dict, game_state: Dict) -> Dict:
        """Display economy summary: treasury, income, upkeep, net.

        Free action (0 AP). Shows same data as end-of-turn financial report.
        Aliases: economy, treasury, finances.
        """
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state"}

        nation = world.player_nation
        income_data = world.calculate_turn_income(nation)
        upkeep_data = world.calculate_turn_upkeep(nation)
        admin_bonus = world.admin_actions_remaining * 75  # Potential bonus if saved

        net = income_data["income"] - upkeep_data["total"] + admin_bonus
        treasury = world.nation_gold.get(nation, 0)

        # Build detailed report
        lines = []
        lines.append("═══════════════════════════════════")
        lines.append(f"  {nation.upper()} TREASURY REPORT")
        lines.append("═══════════════════════════════════")

        # Income breakdown
        region_details = income_data["breakdown"]["region_details"]
        lines.append(f"  Income:  {income_data['income']}g  ({len(region_details)} regions)")
        for rd in region_details:
            effective = rd["effective_income"]
            base = rd["base_income"]
            modifiers = []
            if rd.get("stability_label") and rd["stability_label"] != "Stable":
                modifiers.append(rd["stability_label"].lower())
            if rd.get("war_damage", 0) > 0:
                modifiers.append(f"{rd['war_damage']}% damaged")
            mod_str = f" ({', '.join(modifiers)})" if modifiers else ""
            if effective != base:
                lines.append(f"    {rd['region']}: {effective}g / {base}g base{mod_str}")
            else:
                lines.append(f"    {rd['region']}: {effective}g")

        # Upkeep breakdown
        upkeep_breakdown = upkeep_data["breakdown"]
        lines.append(f"\n  Upkeep: -{upkeep_data['total']}g  ({len(upkeep_breakdown)} marshals)")
        if upkeep_data.get("halved"):
            lines.append("    (HALVED - bankruptcy mercy)")
        for ub in upkeep_breakdown:
            lines.append(f"    {ub['marshal']} ({ub['strength']:,} troops): -{ub['upkeep']}g")

        # Admin bonus
        if admin_bonus > 0:
            lines.append(f"\n  Admin bonus: +{admin_bonus}g  ({world.admin_actions_remaining} unused AP x 75)")
        else:
            lines.append("\n  Admin bonus: 0g  (all AP used)")

        # Spending this turn
        spent = world.gold_spent_this_turn.get(nation, 0)
        if spent > 0:
            lines.append(f"\n  Spent this turn: -{spent}g")

        # Net and treasury
        net_sign = "+" if net >= 0 else ""
        lines.append(f"\n  Projected net: {net_sign}{net}g")
        lines.append(f"  Treasury: {treasury:,}g")

        # Bankruptcy warning
        bankruptcy = world.nation_bankruptcy_turns.get(nation, 0)
        if bankruptcy > 0:
            lines.append(f"\n  WARNING: Bankrupt for {bankruptcy} turn{'s' if bankruptcy > 1 else ''}!")
            if bankruptcy >= 3:
                lines.append("  Desertion active: -5% strength per marshal per turn!")

        # Manpower pools (Phase 6)
        pool = world.manpower_pools.get(nation, {})
        inf_pool = pool.get("infantry", 0)
        cav_pool = pool.get("cavalry", 0)
        art_pool = pool.get("artillery", 0)
        cav_regen = world.get_cavalry_regen_rate(nation)
        art_regen = world.get_artillery_regen_rate(nation)

        lines.append("\n  ═══════ MANPOWER ═══════")
        lines.append(f"  Infantry Pool:  {inf_pool:,} (+{INFANTRY_BASE_REGEN:,}/turn)")
        lines.append(f"  Cavalry Pool:   {cav_pool:,} (+{cav_regen:,}/turn)")
        lines.append(f"  Artillery Pool: {art_pool:,} (+{art_regen:,}/turn)")
        if cav_pool < CAVALRY_RECRUIT_AMOUNT:
            lines.append(f"  Berthier warns: 'Cavalry reserves dangerously low, Sire.' (need {CAVALRY_RECRUIT_AMOUNT:,} to recruit)")
        if art_pool < ARTILLERY_RECRUIT_AMOUNT:
            lines.append(f"  Berthier warns: 'Artillery reserves dangerously low, Sire.' (need {ARTILLERY_RECRUIT_AMOUNT:,} to recruit)")

        lines.append("═══════════════════════════════════")

        message = "\n".join(lines)

        return {
            "success": True,
            "message": message,
            "events": [{
                "type": "economy_report",
                "income": int(income_data["income"]),
                "upkeep": int(upkeep_data["total"]),
                "admin_bonus": int(admin_bonus),
                "net": int(net),
                "treasury": int(treasury),
                "bankruptcy_turns": int(bankruptcy),
            }],
            "new_state": game_state
        }

    def _calculate_recruit_cost(self, region, world, base_cost: int = 200) -> int:
        """Calculate recruitment gold cost based on region properties.

        Priority: Capital discount wins over settling premium.
        Parameterized base_cost: 200 for infantry, 300 for cavalry.
        """
        # Capital discount: 25% off (checked first — always wins)
        if region.region_type == "capital":
            return int(base_cost * 0.75)

        # Settling stability premium: 50% more (stability 51-75)
        if 51 <= region.stability <= 75:
            return int(base_cost * 1.50)

        return base_cost

    def _execute_recruit(self, command: Dict, game_state: Dict) -> Dict:
        """Recruit new troops with manpower pools, morale dilution, stability gates, and cost modifiers.

        Phase 6: Manpower Pools — recruit type auto-determined from marshal.cavalry.
        - Infantry marshals: 10,000 troops from infantry pool at 200g base
        - Cavalry marshals: 5,000 troops from cavalry pool at 300g base
        - Green conscripts have 40% base morale (dilutes veteran armies)
        - Stability gates: blocked in Hostile/Unrest regions (stability <= 50)
        - Capital discount: 25% off at capital
        - Settling premium: 50% more at stability 51-75
        - Admin AP cost handled by executor routing layer (not here)
        """
        # Base recruit morale — upgraded by Training Ground (Phase 6.2.E)
        RECRUIT_MORALE = 40   # Green conscripts base morale

        marshal_specified = command.get("marshal")
        location_specified = command.get("target")
        requested_type = command.get("requested_type")  # Optional: for soft correction

        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # Determine which marshal gets the troops and where recruitment happens
        if marshal_specified:
            # Use fuzzy matching for marshal lookup
            marshal, error = self._fuzzy_match_marshal(marshal_specified, world)
            if error:
                return error

            recipient = marshal.name
            recruitment_location = marshal.location

        elif location_specified:
            result = world.find_nearest_marshal_to_region(location_specified)

            if not result:
                return {
                    "success": False,
                    "message": f"Berthier scans the dispatches. 'No marshal is available to receive reinforcements at {location_specified}, Sire.'"
                }

            marshal, distance = result
            recipient = marshal.name
            recruitment_location = location_specified

        else:
            capital = world.player_capital or "Paris"
            result = world.find_nearest_marshal_to_region(capital)

            if not result:
                return {
                    "success": False,
                    "message": "Berthier scans the dispatches. 'No marshal is available to receive reinforcements, Sire.'"
                }

            marshal, distance = result
            recipient = marshal.name
            recruitment_location = capital

        # --- Determine recruit type from marshal ---
        recruit_marshal = world.get_marshal(recipient)
        # Auto-break square formation (Session 67)
        if recruit_marshal:
            self._auto_break_square(recruit_marshal, "recruit")
        if getattr(recruit_marshal, 'artillery', False):
            recruit_type = "artillery"
        elif getattr(recruit_marshal, 'cavalry', False):
            recruit_type = "cavalry"
        else:
            recruit_type = "infantry"

        # Set batch size and cost based on type
        if recruit_type == "artillery":
            NEW_TROOPS = ARTILLERY_RECRUIT_AMOUNT     # 3,000
        elif recruit_type == "cavalry":
            NEW_TROOPS = CAVALRY_RECRUIT_AMOUNT       # 5,000
        else:
            NEW_TROOPS = INFANTRY_RECRUIT_AMOUNT      # 10,000

        # Build base_message with correct type and amount
        type_label = recruit_type
        if marshal_specified:
            base_message = f"{recruit_marshal.name} recruits {NEW_TROOPS:,} {type_label} at {recruit_marshal.location}"
        elif location_specified:
            base_message = f"{recruit_marshal.name} recruits {NEW_TROOPS:,} {type_label} for {location_specified} ({distance} regions away)"
        else:
            base_message = f"{recruit_marshal.name} recruits {NEW_TROOPS:,} {type_label} (nearest to capital)"

        # Soft correction: player asked for wrong type
        soft_correction = ""
        if requested_type and requested_type != recruit_type:
            soft_correction = f"Berthier notes: 'Marshal {recruit_marshal.name} commands {recruit_type}, Sire.' "

        # --- Location validation (Phase 6.2.D) ---
        region = world.get_region(recruitment_location)
        if not region:
            return {"success": False, "message": f"Unknown region: {recruitment_location}"}

        # Must be controlled by acting nation (player or AI)
        acting_nation = world.player_nation
        if recruit_marshal:
            acting_nation = recruit_marshal.nation
        if region.controller != acting_nation:
            return {
                "success": False,
                "message": f"Berthier frowns. 'We do not control {recruitment_location}, Your Majesty. Recruitment is impossible there.'"
            }

        # Stability gate: block entire Unrest tier (stability <= 50).
        if region.stability <= 50:
            label = region.get_stability_label()
            return {
                "success": False,
                "message": f"Berthier advises caution. '{recruitment_location} is in {label} (stability {region.stability}/100). The populace will not answer our call until stability exceeds 50.'"
            }

        # --- Manpower pool check (BEFORE gold check) ---
        pool = world.manpower_pools.get(acting_nation, {})
        available = pool.get(recruit_type, 0)
        if available < NEW_TROOPS:
            if recruit_type == "artillery":
                regen_rate = world.get_artillery_regen_rate(acting_nation)
            elif recruit_type == "cavalry":
                regen_rate = world.get_cavalry_regen_rate(acting_nation)
            else:
                regen_rate = INFANTRY_BASE_REGEN
            turns_until = max(1, (NEW_TROOPS - available + regen_rate - 1) // regen_rate)
            plural = "s" if turns_until > 1 else ""
            return {
                "success": False,
                "message": f"Berthier consults his ledgers. 'Sire, our {recruit_type} reserves are insufficient. "
                           f"Pool: {available:,}, need: {NEW_TROOPS:,}. "
                           f"Recovering +{regen_rate:,}/turn — available in ~{turns_until} turn{plural}.'"
            }

        # --- Gold cost calculation ---
        if recruit_type == "artillery":
            cost_base = ARTILLERY_RECRUIT_GOLD_COST_BASE
        elif recruit_type == "cavalry":
            cost_base = CAVALRY_RECRUIT_GOLD_COST_BASE
        else:
            cost_base = INFANTRY_RECRUIT_GOLD_COST_BASE
        gold_cost = self._calculate_recruit_cost(region, world, base_cost=cost_base)

        nation_treasury = world.nation_gold.get(acting_nation, 0)
        if nation_treasury < gold_cost:
            return {
                "success": False,
                "message": f"Berthier shakes his head. 'The treasury cannot support this, Sire. Need {gold_cost} gold, have {nation_treasury}.'"
            }

        # Phase 6.2 Audit Fix #6: Training Ground morale bonus buffed from +15% to +30%
        if region.has_building("training_ground"):
            RECRUIT_MORALE = 70

        # --- Draw from manpower pool ---
        world.manpower_pools[acting_nation][recruit_type] -= NEW_TROOPS
        pool_after = world.manpower_pools[acting_nation][recruit_type]

        # Trigger 6: Manpower pool depleted notification
        if pool_after == 0 and acting_nation == getattr(world, 'player_nation', 'France'):
            from backend.notifications import (
                create_notification, NotificationPriority, MANPOWER_DEPLETED,
            )
            world.notifications.add(create_notification(
                notification_type=MANPOWER_DEPLETED,
                priority=NotificationPriority.HIGH,
                title=f"{recruit_type.title()} pool exhausted",
                message=f"Our {recruit_type} manpower reserves are completely spent. Recruitment will be unavailable until reserves regenerate.",
                turn_created=int(world.current_turn),
                details={"pool_type": recruit_type, "nation": acting_nation},
            ))

        # --- Morale dilution ---
        marshal = world.get_marshal(recipient)
        old_strength = marshal.strength
        old_morale = marshal.morale

        # Weighted average: existing troops at current morale + new troops at RECRUIT_MORALE
        new_morale = int(
            (old_strength * old_morale + NEW_TROOPS * RECRUIT_MORALE)
            / (old_strength + NEW_TROOPS)
        )

        # Set morale BEFORE add_troops (add_troops only modifies strength)
        marshal.morale = new_morale
        marshal.add_troops(NEW_TROOPS)
        world.nation_gold[acting_nation] = int(nation_treasury - gold_cost)
        world.record_gold_spent(acting_nation, gold_cost)

        # --- Build result message ---
        is_capital_discount = region.region_type == "capital"
        is_stability_premium = (51 <= region.stability <= 75) and not is_capital_discount

        cost_note = ""
        if is_capital_discount:
            cost_note = " (capital discount)"
        elif is_stability_premium:
            cost_note = " (unstable region premium)"

        # Pool status line
        pool_line = f"\n{recruit_type.title()} pool: {available:,} -> {pool_after:,}"

        # --- Morale warning (Session 31) ---
        morale_warning = ""
        if new_morale < 25:
            morale_warning = f" [DANGER] Morale critically low at {new_morale}% — troops may break in combat!"
        elif new_morale < 40:
            morale_warning = f" [WARNING] Morale dropped to {new_morale}% — consider drilling before battle."

        # Log recruitment event
        world.log_event({
            "type": "recruitment",
            "marshal": recipient,
            "nation": acting_nation,
            "amount": int(NEW_TROOPS),
            "recruit_type": recruit_type,
            "location": recruitment_location,
        })

        return {
            "success": True,
            "message": f"{soft_correction}{base_message} - Cost: {gold_cost} gold{cost_note}. Morale: {old_morale}% -> {new_morale}%{pool_line}{morale_warning}",
            "events": [{
                "type": "recruit",
                "marshal": recipient,
                "location": recruitment_location,
                "recruit_type": recruit_type,
                "troops_added": int(NEW_TROOPS),
                "gold_cost": int(gold_cost),
                "morale_before": int(old_morale),
                "morale_after": int(new_morale),
                "new_strength": int(marshal.strength),
                "stability_premium": is_stability_premium,
                "capital_discount": is_capital_discount,
                "pool_before": int(available),
                "pool_after": int(pool_after),
            }],
            "new_state": game_state
        }

    # ========================================
    # BUILDING SYSTEM (Phase 6.2.E)
    # ========================================

    def _extract_building_type(self, command: Dict) -> str:
        """Extract building type from command text or target field.

        Simple keyword matching — full parser rework in 6.2.G.
        """
        raw = (command.get("raw_command") or command.get("target") or "").lower()
        # Also check the original raw_input if available
        if not raw:
            raw = ""
        if "supply" in raw or "depot" in raw:
            return "supply_depot"
        elif "fort" in raw or "wall" in raw or "defense" in raw:
            return "fortification"
        elif "train" in raw:
            return "training_ground"
        elif "market" in raw or "trade" in raw:
            return "market"
        elif "stable" in raw or "horse" in raw:
            return "stables"
        elif "watch" in raw or "tower" in raw:
            return "watchtower"
        # Try building_type field directly (set by tests)
        bt = command.get("building_type")
        if bt:
            return bt
        return ""

    # ════════════════════════════════════════════════════════════════════════════
    # GARRISON COMMAND (Session 31): Detach troops to defend a region
    # ════════════════════════════════════════════════════════════════════════════

    GARRISON_DETACHMENT_SIZE = 3000
    GARRISON_MIN_MARSHAL_STRENGTH = 8000
    GARRISON_MAX_PER_NATION = 3  # Cap includes capital garrisons

    def _execute_garrison(self, command: Dict, game_state: Dict) -> Dict:
        """Detach troops to garrison the marshal's current region.

        Session 31: Detachment garrisons use the same garrison_strength field as
        capital garrisons, but with garrison_detachment=True. Detachment garrisons
        don't regen and fight to destruction (no 5k collapse threshold).

        Used by both player and AI (Building Blocks principle). AI heuristic in
        enemy_ai.py P6.75: garrison behind front lines with excess strength.
        """
        world: WorldState = game_state.get("world")
        marshal_name = (command.get("marshal") or "").strip()

        if not marshal_name:
            return {
                "success": False,
                "message": "Berthier clears his throat. 'Which marshal should garrison, Your Majesty?'"
            }

        marshal = world.marshals.get(marshal_name)
        if not marshal:
            return {
                "success": False,
                "message": f"Berthier frowns. 'I know no marshal named {marshal_name}, Your Majesty.'"
            }

        # Auto-break square formation (Session 67)
        self._auto_break_square(marshal, "garrison")

        region_name = marshal.location
        region = world.regions.get(region_name)
        if not region:
            return {
                "success": False,
                "message": f"{marshal_name} is in an unknown region, Your Majesty."
            }

        # Validation: region must be owned by marshal's nation
        if region.controller != marshal.nation:
            return {
                "success": False,
                "message": f"We do not control {region_name}, Your Majesty. We cannot garrison enemy territory."
            }

        # Validation: no enemy marshals present
        enemies_present = [m for m in world.marshals.values()
                          if m.location == region_name and m.nation != marshal.nation and m.strength > 0]
        if enemies_present:
            return {
                "success": False,
                "message": f"Enemy forces contest {region_name}. We cannot garrison while under threat, Your Majesty."
            }

        # Validation: region doesn't already have a garrison
        if region.garrison_strength > 0:
            return {
                "success": False,
                "message": f"A garrison already holds {region_name}, Your Majesty."
            }

        # Validation: nation garrison cap (includes capital garrisons)
        nation_garrisons = sum(
            1 for r in world.regions.values()
            if r.garrison_strength > 0 and r.controller == marshal.nation
        )
        if nation_garrisons >= self.GARRISON_MAX_PER_NATION:
            return {
                "success": False,
                "message": (f"Berthier shakes his head. 'We already maintain {nation_garrisons} garrisons, "
                           f"Your Majesty. Our supply lines cannot support another. "
                           f"Maximum {self.GARRISON_MAX_PER_NATION} garrisons per nation.'")
            }

        # Validation: marshal has enough troops
        if marshal.strength < self.GARRISON_MIN_MARSHAL_STRENGTH:
            return {
                "success": False,
                "message": (f"{marshal_name}'s forces are too depleted to spare a garrison, Your Majesty. "
                           f"We need at least {self.GARRISON_MIN_MARSHAL_STRENGTH:,} men to leave troops behind.")
            }

        # Execute: detach troops
        marshal.strength -= self.GARRISON_DETACHMENT_SIZE
        region.garrison_strength = self.GARRISON_DETACHMENT_SIZE
        region.garrison_detachment = True

        # Event log
        world.log_event({
            "type": "garrison_placed",
            "marshal": marshal_name,
            "region": region_name,
            "troops": int(self.GARRISON_DETACHMENT_SIZE),
            "marshal_remaining": int(marshal.strength),
        })

        return {
            "success": True,
            "message": (f"{marshal_name} detaches {self.GARRISON_DETACHMENT_SIZE:,} troops to garrison {region_name}. "
                       f"Army strength: {marshal.strength:,}."),
            "action_info": {"remaining": world.actions_remaining},
        }

    def _execute_build(self, command: Dict, game_state: Dict) -> Dict:
        """Build a building at a region. Costs admin AP + gold.

        Phase 6.2.E: supply_depot (300g/2t), fortification (400g/3t), training_ground (250g/2t).
        Phase 6 Fog: watchtower (250g/2t) — dedicated field, bypasses slot system.
        """
        from backend.models.region import BUILDING_TYPES

        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state available"}

        region_name = command.get("target")
        building_type = command.get("building_type") or self._extract_building_type(command)

        if not region_name:
            return {"success": False, "message": "Specify a region. Example: 'build supply depot at Lyon'"}

        # ════════════════════════════════════════════════════════════
        # WATCHTOWER: Dedicated field, bypasses slot system (Phase 6 Fog - Session 35)
        # Every region type can have exactly one watchtower.
        # ════════════════════════════════════════════════════════════
        if building_type == "watchtower":
            return self._execute_build_watchtower(command, game_state, region_name)

        if not building_type or building_type not in BUILDING_TYPES:
            return {
                "success": False,
                "message": f"Unknown building type. Valid types: {', '.join(BUILDING_TYPES.keys())}, watchtower"
            }

        region = world.get_region(region_name)
        if not region:
            return {"success": False, "message": f"Unknown region: {region_name}"}

        # Determine acting nation: from _acting_nation (AI), marshal, or player default
        build_acting_nation = command.get("_acting_nation") or world.player_nation
        if not command.get("_acting_nation"):
            build_marshal_name = command.get("marshal")
            if build_marshal_name:
                build_marshal_obj = world.get_marshal(build_marshal_name)
                if build_marshal_obj:
                    build_acting_nation = build_marshal_obj.nation
        if region.controller != build_acting_nation:
            return {"success": False, "message": f"Cannot build in {region_name} — not controlled by {build_acting_nation}"}

        # Region type must allow buildings
        if region.max_building_slots() == 0:
            return {"success": False, "message": f"Cannot build in {region_name} — {region.region_type} regions don't support buildings (need city or larger)"}

        # Allowed region type for this building
        btype_info = BUILDING_TYPES[building_type]
        if region.region_type not in btype_info["allowed_in"]:
            return {"success": False, "message": f"Cannot build {building_type.replace('_', ' ')} in {region.region_type} region"}

        # Already constructing (check before slot count since construction uses a slot)
        if region.building_under_construction:
            return {"success": False, "message": f"Already constructing {region.building_under_construction['type'].replace('_', ' ')} in {region_name}"}

        # Available slots
        if region.available_building_slots() <= 0:
            return {"success": False, "message": f"No building slots available in {region_name} ({len(region.buildings)}/{region.max_building_slots()})"}

        # Stability gate (same as recruit: need > 50)
        if region.stability <= 50:
            return {"success": False, "message": f"Cannot build in {region_name} — region stability too low ({region.stability}/100). Need 51+."}

        # Duplicate check
        if region.has_building(building_type, functional_only=False):
            return {"success": False, "message": f"{region_name} already has a {building_type.replace('_', ' ')}"}

        # Gold check (use acting nation's treasury)
        gold_cost = btype_info["gold_cost"]
        build_treasury = world.nation_gold.get(build_acting_nation, 0)
        if build_treasury < gold_cost:
            return {"success": False, "message": f"Insufficient gold! Need {gold_cost}, have {build_treasury}"}

        # Start construction
        region.building_under_construction = {
            "type": building_type,
            "turns_remaining": btype_info["build_time"]
        }
        world.nation_gold[build_acting_nation] = int(build_treasury - gold_cost)
        world.record_gold_spent(build_acting_nation, gold_cost)

        display_name = building_type.replace('_', ' ').title()

        # Log building_started event
        world.log_event({
            "type": "building_started",
            "region": region_name,
            "building": building_type,
            "nation": build_acting_nation,
        })

        return {
            "success": True,
            "message": f"Construction started: {display_name} in {region_name} ({btype_info['build_time']} turns, {gold_cost} gold)",
            "events": [{
                "type": "build_started",
                "region": region_name,
                "building": building_type,
                "gold_cost": int(gold_cost),
                "turns": btype_info["build_time"],
            }],
            "new_state": game_state
        }

    # Watchtower cost constants (Phase 6 Fog - Session 35)
    WATCHTOWER_GOLD_COST = 250
    WATCHTOWER_BUILD_TIME = 2

    def _execute_build_watchtower(self, command: Dict, game_state: Dict, region_name: str) -> Dict:
        """Build a watchtower at a region. Dedicated field, bypasses slot system.

        Phase 6 Fog of War - Session 35:
        - Cost: 250 gold, 2 turns construction
        - No slot required — every region type can have one
        - Provides PARTIAL visibility on all adjacent regions when active
        """
        world: WorldState = game_state.get("world")

        region = world.get_region(region_name)
        if not region:
            return {"success": False, "message": f"Unknown region: {region_name}"}

        # Determine acting nation
        build_acting_nation = command.get("_acting_nation") or world.player_nation
        if not command.get("_acting_nation"):
            build_marshal_name = command.get("marshal")
            if build_marshal_name:
                build_marshal_obj = world.get_marshal(build_marshal_name)
                if build_marshal_obj:
                    build_acting_nation = build_marshal_obj.nation

        # Control check
        if region.controller != build_acting_nation:
            return {"success": False, "message": f"Cannot build in {region_name} — not controlled by {build_acting_nation}"}

        # Already has watchtower (active or damaged)
        if region.watchtower in ("active", "damaged"):
            status = "an active" if region.watchtower == "active" else "a damaged"
            return {"success": False, "message": f"{region_name} already has {status} watchtower"}

        # Already constructing watchtower
        if region.watchtower == "under_construction":
            return {"success": False, "message": f"Already constructing a watchtower in {region_name}"}

        # Stability gate
        if region.stability <= 50:
            return {"success": False, "message": f"Cannot build in {region_name} — region stability too low ({region.stability}/100). Need 51+."}

        # Gold check
        build_treasury = world.nation_gold.get(build_acting_nation, 0)
        if build_treasury < self.WATCHTOWER_GOLD_COST:
            return {"success": False, "message": f"Insufficient gold! Need {self.WATCHTOWER_GOLD_COST}, have {build_treasury}"}

        # Start construction
        region.watchtower = "under_construction"
        region.watchtower_turns_remaining = self.WATCHTOWER_BUILD_TIME
        world.nation_gold[build_acting_nation] = int(build_treasury - self.WATCHTOWER_GOLD_COST)
        world.record_gold_spent(build_acting_nation, self.WATCHTOWER_GOLD_COST)

        # Log event
        world.log_event({
            "type": "building_started",
            "region": region_name,
            "building": "watchtower",
            "nation": build_acting_nation,
        })

        return {
            "success": True,
            "message": f"Construction started: Watchtower in {region_name} ({self.WATCHTOWER_BUILD_TIME} turns, {self.WATCHTOWER_GOLD_COST} gold)",
            "events": [{
                "type": "build_started",
                "region": region_name,
                "building": "watchtower",
                "gold_cost": int(self.WATCHTOWER_GOLD_COST),
                "turns": self.WATCHTOWER_BUILD_TIME,
            }],
            "new_state": game_state
        }

    def _execute_repair(self, command: Dict, game_state: Dict) -> Dict:
        """Repair war damage or a damaged building. Costs admin AP + 150 gold.

        Phase 6.2.E: 1 admin AP + 150 gold.
        - No building_type: repair war damage (-0.15)
        - With building_type: repair that building (damaged -> functional)
        """
        REPAIR_COST = 150

        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state available"}

        region_name = command.get("target")
        if not region_name:
            return {"success": False, "message": "Specify a region. Example: 'repair Lyon'"}

        region = world.get_region(region_name)
        if not region:
            return {"success": False, "message": f"Unknown region: {region_name}"}

        # Determine acting nation: from _acting_nation (AI), marshal, or player default
        repair_acting_nation = command.get("_acting_nation") or world.player_nation
        if not command.get("_acting_nation"):
            repair_marshal_name = command.get("marshal")
            if repair_marshal_name:
                repair_marshal_obj = world.get_marshal(repair_marshal_name)
                if repair_marshal_obj:
                    repair_acting_nation = repair_marshal_obj.nation

        if region.controller != repair_acting_nation:
            return {"success": False, "message": f"Cannot repair in {region_name} — not controlled by {repair_acting_nation}"}

        repair_treasury = world.nation_gold.get(repair_acting_nation, 0)
        if repair_treasury < REPAIR_COST:
            return {"success": False, "message": f"Insufficient gold! Need {REPAIR_COST}, have {repair_treasury}"}

        # Check if repairing a building or war damage
        building_type = command.get("building_type") or self._extract_building_type(command)

        if building_type:
            # Watchtower repair (Phase 6 Fog - Session 35): dedicated field, not in buildings list
            if building_type == "watchtower":
                wt = getattr(region, 'watchtower', 'none')
                if wt != "damaged":
                    return {"success": False, "message": f"No damaged watchtower in {region_name}"}
                region.watchtower = "under_construction"
                region.watchtower_turns_remaining = 2  # Same as build time
                world.nation_gold[repair_acting_nation] = int(repair_treasury - REPAIR_COST)
                world.record_gold_spent(repair_acting_nation, REPAIR_COST)
                return {
                    "success": True,
                    "message": f"Watchtower repair started in {region_name} (2 turns, {REPAIR_COST} gold)",
                    "events": [{"type": "repair_building", "region": region_name, "building": "watchtower"}],
                    "new_state": game_state
                }

            # Find the damaged building
            for b in region.buildings:
                if b["type"] == building_type and b.get("damaged", False):
                    b["damaged"] = False
                    world.nation_gold[repair_acting_nation] = int(repair_treasury - REPAIR_COST)
                    world.record_gold_spent(repair_acting_nation, REPAIR_COST)
                    return {
                        "success": True,
                        "message": f"Repaired {building_type.replace('_', ' ').title()} in {region_name} ({REPAIR_COST} gold)",
                        "events": [{"type": "repair_building", "region": region_name, "building": building_type}],
                        "new_state": game_state
                    }
            return {"success": False, "message": f"No damaged {building_type.replace('_', ' ')} in {region_name}"}

        # Repair war damage
        if region.war_damage <= 0:
            return {"success": False, "message": f"No war damage to repair in {region_name}"}

        region.recover_war_damage(0.15)
        world.nation_gold[repair_acting_nation] = int(repair_treasury - REPAIR_COST)
        world.record_gold_spent(repair_acting_nation, REPAIR_COST)
        return {
            "success": True,
            "message": f"War damage repaired in {region_name} ({REPAIR_COST} gold). War damage: {region.war_damage:.0%}",
            "events": [{"type": "repair_war_damage", "region": region_name, "remaining_damage": int(region.war_damage * 100)}],
            "new_state": game_state
        }

    # ========================================
    # TACTICAL STATE ACTIONS (Phase 2.6)
    # ========================================

    def _execute_drill(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute drill order - 2-turn commitment for +20% attack bonus.

        Turn N: Order drill → drilling = True
        Turn N+1: Locked (drilling_locked = True, cannot receive orders)
        Turn N+2+: drill_complete_turn reached → shock_bonus = 2 (+20% attack)

        The bonus persists until the marshal enters combat (first attack clears it).
        """
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Auto-break square formation (Session 67)
        self._auto_break_square(marshal, "drill")

        # Check if already drilling
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return {
                "success": False,
                "message": f"{marshal.name} is already engaged in drill exercises."
            }

        # Check if fortified (can't drill while fortified)
        if getattr(marshal, 'fortified', False):
            return {
                "success": False,
                "message": f"{marshal.name} is fortified and cannot drill. Abandon fortification first."
            }

        # Check if retreating (can't drill while recovering)
        if getattr(marshal, 'retreating', False):
            return {
                "success": False,
                "message": f"{marshal.name} is recovering from retreat and cannot drill yet."
            }

        # Check for enemies at current location (can't drill with enemy present)
        # Use nation-aware lookup so enemies can drill too (not just player marshals)
        enemy_at_location = world.get_enemy_at_location_for_nation(marshal.location, marshal.nation)
        if enemy_at_location and enemy_at_location.strength > 0:
            return {
                "success": False,
                "message": f"{marshal.name} cannot drill with enemy forces ({enemy_at_location.name}) present at {marshal.location}!"
            }

        # Check for enemies in adjacent regions (too risky to drill)
        # Use nation-aware lookup so enemies can drill too
        current_region = world.get_region(marshal.location)
        if current_region:
            for adj_name in current_region.adjacent_regions:
                for enemy in world.get_enemies_of_nation(marshal.nation):
                    if enemy.location == adj_name and enemy.strength > 0:
                        return {
                            "success": False,
                            "message": f"{marshal.name} cannot drill with enemy forces nearby! "
                                      f"{enemy.name} is at {adj_name}, just one region away."
                        }

        # Start drilling - will be locked next turn
        marshal.drilling = True
        marshal.drilling_locked = False  # Not locked yet (locked on turn advance)
        # Timeline: Turn N order → End N locks → Turn N+1 locked → End N+1 completes → Turn N+2 ready
        marshal.drill_complete_turn = world.current_turn + 1  # Completes at end of NEXT turn

        return {
            "success": True,
            "message": f"{marshal.name} begins intensive drill exercises at {marshal.location}. "
                      f"Troops will be locked in training next turn, "
                      f"bonus ready turn {marshal.drill_complete_turn + 1}.",
            "events": [{
                "type": "drill_started",
                "marshal": marshal.name,
                "location": marshal.location,
                "complete_turn": int(marshal.drill_complete_turn),
                "ready_turn": int(marshal.drill_complete_turn + 1)
            }],
            "new_state": game_state
        }

    def _execute_fortify(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute fortify order - Defensive lockdown with growing defense bonus.

        REQUIRES DEFENSIVE STANCE:
        - If AGGRESSIVE: Block with error message
        - If NEUTRAL: Auto-transition to DEFENSIVE first (+1 action cost)
        - If DEFENSIVE: Execute fortify

        While fortified:
        - Cannot move or attack
        - Starts at +2% defense, grows +2% per turn (max 15%)
        - Permanent until ordered to un-fortify
        """
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Auto-break square formation (Session 67) — fortify replaces square
        self._auto_break_square(marshal, "fortify")

        # Check if already fortified
        if getattr(marshal, 'fortified', False):
            current_bonus = int(getattr(marshal, 'defense_bonus', 0) * 100)
            return {
                "success": False,
                "message": f"{marshal.name} is already fortified at {marshal.location} (+{current_bonus}% defense)."
            }

        # Check if drilling (can't fortify while drilling)
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return {
                "success": False,
                "message": f"{marshal.name} is engaged in drill exercises and cannot fortify."
            }

        # Check if retreating (can't fortify while recovering)
        if getattr(marshal, 'retreating', False):
            return {
                "success": False,
                "message": f"{marshal.name} is recovering from retreat and cannot fortify yet."
            }

        # ════════════════════════════════════════════════════════════
        # ENGAGEMENT CHECK: Cannot fortify while engaged with enemy
        # ════════════════════════════════════════════════════════════
        enemies_in_region = [
            m for m in world.marshals.values()
            if m.location == marshal.location
            and m.nation != marshal.nation
            and m.strength > 0
        ]
        if enemies_in_region:
            enemy_names = [e.name for e in enemies_in_region]
            return {
                "success": False,
                "message": f"{marshal.name} cannot fortify while engaged with enemy forces! "
                          f"Enemy present: {', '.join(enemy_names)}. "
                          f"Attack or retreat first."
            }

        # ════════════════════════════════════════════════════════════
        # STANCE CHECK: Fortify requires defensive stance
        # ════════════════════════════════════════════════════════════
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)
        stance_transition_cost = 0
        stance_message = ""

        if current_stance == Stance.AGGRESSIVE:
            # Block - aggressive marshals cannot fortify
            return {
                "success": False,
                "message": f"{marshal.name} is in AGGRESSIVE stance and cannot fortify! "
                          f"An aggressive posture is incompatible with defensive preparations. "
                          f"Use 'defend' to switch to defensive stance first.",
                "suggestion": f"Try: '{marshal.name}, defend' to change stance, then fortify"
            }
        elif current_stance == Stance.NEUTRAL:
            # Auto-transition to defensive (costs 1 extra action)
            stance_transition_cost = 1
            total_cost = 1 + stance_transition_cost  # fortify + stance change

            # Check if player has enough actions
            if world.actions_remaining < total_cost:
                return {
                    "success": False,
                    "message": f"Fortifying from neutral stance requires {total_cost} actions "
                              f"(1 for stance change + 1 for fortify), but only {world.actions_remaining} remaining."
                }

            # Execute stance change first
            marshal.stance = Stance.DEFENSIVE
            stance_message = "[Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] "

        # ════════════════════════════════════════════════════════════
        # PERSONALITY-SPECIFIC FORTIFY (Phase 2.8)
        # ════════════════════════════════════════════════════════════
        from backend.models.personality_modifiers import (
            get_max_fortify_bonus, get_fortify_rate, get_instant_fortify_bonus
        )

        personality = getattr(marshal, 'personality', 'unknown')
        max_fortify = get_max_fortify_bonus(personality)
        fortify_rate = get_fortify_rate(personality)
        instant_bonus = get_instant_fortify_bonus(personality)

        # Enter fortified state
        marshal.fortified = True
        # Base +2% plus instant bonus (Davout gets +5% instant = +7% total on first fortify)
        base_bonus = 0.02
        marshal.defense_bonus = base_bonus + instant_bonus

        # Build message with personality-specific info
        personality_message = ""
        if personality == "cautious":
            personality_message = f" (Iron Marshal: +{int(instant_bonus * 100)}% instant, +{int(fortify_rate * 100)}%/turn, max {int(max_fortify * 100)}%)"
        elif personality == "aggressive":
            personality_message = f" (Aggressive: max {int(max_fortify * 100)}% only)"

        current_bonus_pct = int(marshal.defense_bonus * 100)
        rate_pct = int(fortify_rate * 100)
        max_pct = int(max_fortify * 100)

        message = stance_message + f"{marshal.name} fortifies position at {marshal.location}. "
        message += f"Defense bonus: +{current_bonus_pct}% (grows +{rate_pct}% per turn, max {max_pct}%){personality_message}. "
        message += "Cannot move or attack while fortified. Use 'unfortify' to become mobile."

        events = [{
            "type": "fortified",
            "marshal": marshal.name,
            "location": marshal.location,
            "defense_bonus": current_bonus_pct,  # Display as percentage
            "personality_bonus": personality_message
        }]

        # Add stance change event if transitioned
        if stance_transition_cost > 0:
            events.insert(0, {
                "type": "stance_change",
                "marshal": marshal.name,
                "from_stance": "neutral",
                "to_stance": "defensive",
                "action_cost": stance_transition_cost,
                "auto_transition": True
            })

        # Return with variable action cost if stance transition occurred
        result = {
            "success": True,
            "message": message,
            "events": events,
            "new_state": game_state
        }

        if stance_transition_cost > 0:
            # Total cost = fortify (1) + stance change (1) = 2
            # But main execute() will add 1 for fortify, so we signal extra 1
            result["variable_action_cost"] = 1 + stance_transition_cost

        return result

    # ════════════════════════════════════════════════════════════════════════
    # SQUARE FORMATION (Phase 7b, Session 67) — Tactical Triangle Part A
    # ════════════════════════════════════════════════════════════════════════

    def _auto_break_square(self, marshal, action_name: str = "") -> str:
        """Auto-break square formation when marshal takes an active action.

        Called at the TOP of _execute_attack, _execute_move, _execute_fortify,
        _execute_drill, _execute_recruit, _execute_garrison, _execute_stance_change,
        _execute_glorious_charge. NOT called for form_square, break_square, wait, end_turn.

        Returns message string if square was broken, empty string otherwise.
        """
        if not getattr(marshal, 'square_formation', False):
            return ""
        marshal.square_formation = False
        # Cancel any strategic order (breaking formation to act)
        if getattr(marshal, 'strategic_order', None):
            marshal.strategic_order = None
        display = _action_display_name(action_name) if action_name else "act"
        msg = f"\n[Square broken — {marshal.name} breaks formation to {display}]"
        # Store for execute() to prepend to result message
        self._pending_square_break_msg = msg
        return msg

    def _execute_form_square(self, command: Dict, game_state: Dict) -> Dict:
        """
        Form square formation — infantry anti-cavalry defense.

        Costs 1 AP. Infantry only. Mutually exclusive with fortify.
        Provides +5% defense, -40% incoming cavalry damage, +50% incoming artillery damage.
        Cancels any active strategic order.
        """
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Already in square
        if getattr(marshal, 'square_formation', False):
            return {
                "success": False,
                "message": f"{marshal.name} is already in square formation."
            }

        # Infantry only — cavalry and artillery cannot form square
        if getattr(marshal, 'cavalry', False):
            return {
                "success": False,
                "message": f"{marshal.name}'s cavalry cannot form an infantry square!"
            }
        if getattr(marshal, 'artillery', False):
            return {
                "success": False,
                "message": f"{marshal.name}'s artillery cannot form an infantry square!"
            }

        # Cannot form square while broken/retreating
        if getattr(marshal, 'broken', False):
            return {
                "success": False,
                "message": f"{marshal.name}'s troops are broken and cannot form square."
            }
        if getattr(marshal, 'retreating', False):
            return {
                "success": False,
                "message": f"{marshal.name} is retreating and cannot form square."
            }

        # Mutual exclusion: square ↔ fortify — forming square auto-breaks fortification
        fortify_break_msg = ""
        if getattr(marshal, 'fortified', False):
            old_bonus = int(getattr(marshal, 'defense_bonus', 0) * 100)
            marshal.fortified = False
            marshal.defense_bonus = 0.0
            fortify_break_msg = (
                f"[{marshal.name} abandons fortified position (+{old_bonus}% defense) to form square]\n"
            )

        # Cannot form square while drilling
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return {
                "success": False,
                "message": f"{marshal.name} is drilling and cannot form square."
            }

        # Form square
        marshal.square_formation = True

        # Cancel strategic order (forming square is a defensive stance commitment)
        strategic_cancel_msg = ""
        if getattr(marshal, 'strategic_order', None):
            old_order = marshal.strategic_order
            marshal.strategic_order = None
            if old_order.command_type == "HOLD":
                marshal.holding_position = False
                marshal.hold_region = ""
            strategic_cancel_msg = f" Strategic order ({old_order.command_type}) cancelled."

        message = fortify_break_msg + (
            f"{marshal.name} forms square at {marshal.location}! "
            f"Bayonets bristle in all directions. (+5% defense, cavalry -40%, "
            f"but artillery +50% damage vs packed ranks){strategic_cancel_msg}\n"
            f"Any order — even one that fails — will break the discipline required to hold square."
        )

        return {
            "success": True,
            "message": message,
            "events": [{
                "type": "form_square",
                "marshal": marshal.name,
                "location": marshal.location,
            }],
            "new_state": game_state
        }

    def _execute_break_square(self, command: Dict, game_state: Dict) -> Dict:
        """
        Break square formation — free action (0 AP).

        Returns troops to normal line formation.
        """
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        if not getattr(marshal, 'square_formation', False):
            return {
                "success": False,
                "message": f"{marshal.name} is not in square formation."
            }

        marshal.square_formation = False

        message = (
            f"{marshal.name} breaks square and returns to line formation at {marshal.location}."
        )

        return {
            "success": True,
            "message": message,
            "free_action": True,
            "events": [{
                "type": "break_square",
                "marshal": marshal.name,
                "location": marshal.location,
            }],
            "new_state": game_state
        }

    def _execute_unfortify(self, command: Dict, game_state: Dict) -> Dict:
        """
        Remove fortification from a marshal.

        DAVOUT FREE UNFORTIFY (Phase 2.8):
        - Davout (cautious) can unfortify for free
        - Other marshals pay 1 action
        """
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        if not getattr(marshal, 'fortified', False):
            return {
                "success": False,
                "message": f"{marshal.name} is not currently fortified."
            }

        # ════════════════════════════════════════════════════════════
        # DAVOUT FREE UNFORTIFY (Phase 2.8)
        # Cautious marshals can efficiently break camp
        # ════════════════════════════════════════════════════════════
        personality = getattr(marshal, 'personality', '')
        is_free_unfortify = personality == 'cautious'

        # Remove fortification
        marshal.fortified = False
        marshal.defense_bonus = 0
        marshal.turns_fortified = 0  # Reset decay counter

        # Build message with ability note
        if is_free_unfortify:
            message = f"{marshal.name} efficiently breaks camp. (Free Unfortify: no action cost) "
            message += "Army is now mobile."
        else:
            message = f"{marshal.name} abandons fortified position at {marshal.location}. "
            message += "Army is now mobile."

        result = {
            "success": True,
            "message": message,
            "events": [{
                "type": "unfortified",
                "marshal": marshal.name,
                "location": marshal.location,
                "free_ability": is_free_unfortify
            }],
            "new_state": game_state
        }

        # Mark as free action for Davout
        if is_free_unfortify:
            result["free_action"] = True

        return result

    # ========================================
    # DEBUG COMMANDS (Phase 2.8)
    # ========================================

    def _execute_debug(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute debug commands for testing personality abilities and AI.

        Supported debug commands:
        - /debug counter_punch <marshal>: Set counter_punch_available = True
        - /debug restless <marshal>: Set turns_in_defensive_stance to trigger restlessness
        - /debug cavalry <marshal>: Toggle cavalry status
        - /debug hold <marshal>: Set holding_position = True
        - /debug ai_turn <nation>: Force AI turn for nation (Britain/Prussia/Austria/Saxony)
        - /debug ai_state <marshal>: Show AI evaluation for marshal
        - /debug set_retreat <marshal>: Set retreated_this_turn = True
        - /debug set_recovery <marshal> <turns>: Set retreat_recovery (0-3)
        - /debug set_strength <marshal> <amount>: Set marshal strength
        - /debug set_morale <marshal> <amount>: Set marshal morale (0-100)
        - /debug set_trust <marshal> <0-100>: Set marshal trust (for testing objections)
        - /debug set_relationship <marshal> <target> <-2 to 2>: Set relationship (-2=hostile to 2=devoted)
        - /debug set_fortified <marshal>: Toggle fortified status
        - /debug set_manpower <nation> <infantry|cavalry> <amount>: Set manpower pool

        Usage: /debug <command> <args>
        """
        # Check if debug mode is enabled
        debug_mode = game_state.get("debug_mode", False)
        if not debug_mode:
            return {
                "success": False,
                "message": "Debug commands are disabled. Set DEBUG_MODE = True in main.py to enable."
            }

        target = command.get("target", "")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Parse debug command: "counter_punch Davout" -> ability="counter_punch", marshal="Davout"
        parts = target.split() if target else []
        if len(parts) < 1:
            return {
                "success": False,
                "message": "Debug command format: /debug <command> <args>\n"
                          "\n== Personality Testing ==\n"
                          "  • counter_punch <marshal> - Set counter-punch (free attack)\n"
                          "  • restless <marshal> - Set turns_in_defensive_stance=5 (restlessness)\n"
                          "  • cavalry <marshal> - Toggle cavalry status\n"
                          "  • hold <marshal> - Set holding_position (Immovable)\n"
                          "\n== Cavalry Recklessness (Phase 3) ==\n"
                          "  • set_recklessness <marshal> <0-4> - Set recklessness level\n"
                          "    (3 = popup, 4 = auto-charge)\n"
                          "\n== Pressure System (Phase 3) ==\n"
                          "  • set_exhaustion <marshal> <0-4> - Set attacks this turn\n"
                          "  • set_fortify_turns <marshal> <turns> - Set turns fortified\n"
                          "    (decay starts at turn 4-8 depending on personality)\n"
                          "\n== AI Testing ==\n"
                          "  • freeze_enemies - Toggle freeze ALL enemies (AI skips them)\n"
                          "  • ai_turn <nation> - Force AI turn (Britain/Prussia/Austria/Saxony)\n"
                          "  • ai_state <marshal> - Show AI evaluation\n"
                          "\n== State Manipulation ==\n"
                          "  • set_location <marshal> <region> - Teleport ANY marshal\n"
                          "  • set_retreat <marshal> - Set retreated_this_turn=True\n"
                          "  • set_recovery <marshal> <0-3> - Set retreat_recovery\n"
                          "  • set_strength <marshal> <amount> - Set troop strength\n"
                          "  • set_morale <marshal> <0-100> - Set morale\n"
                          "  • set_fortified <marshal> - Toggle fortified\n"
                          "  • freeze <marshal> - Toggle AI freeze (marshal won't act)\n"
                          "  • set_autonomy <marshal> [turns] - Toggle autonomous (Phase 2.5)\n"
                          "  • set_trust <marshal> <0-100> - Set trust level\n"
                          "  • set_vindication <marshal> <-5 to 5> - Set vindication score\n"
                          "  • set_relationship <marshal> <target> <-2 to 2> - Set relationship\n"
                          "  • set_authority <0-100> - Set player authority level\n"
                          "\n== Redemption Testing (Phase 3) ==\n"
                          "  • dismiss <marshal> - Directly dismiss (bypass disobedience)\n"
                          "  • admin <marshal> - Toggle administrative role\n"
                          "\n== Economy Testing (Phase 6.2) ==\n"
                          "  • damage_building <region> - Damage first building in region\n"
                          "  • set_stability <region> <0-100> - Set region stability\n"
                          "  • set_gold <amount> - Set player gold\n"
                          "  • set_manpower <nation> <infantry|cavalry> <amount> - Set manpower pool\n"
                          "  • set_controller <region> <nation> - Set region controller\n"
                          "  • add_building <region> <type> - Add building (supply_depot/fortification/training_ground/market/watchtower/stables)\n"
                          "\n== Info ==\n"
                          "  • list_marshals - Show all marshals and locations\n"
                          "  • list_regions - Show all regions and who's there"
            }

        ability = parts[0].lower()

        # === AI TESTING COMMANDS (don't require marshal) ===

        if ability == "freeze_enemies":
            # Toggle freeze on ALL enemy marshals at once
            player_nation = getattr(world, 'player_nation', 'France')
            enemy_marshals = [m for m in world.marshals.values() if m.nation != player_nation]

            if not enemy_marshals:
                return {"success": False, "message": "No enemy marshals found."}

            # Check current state - if any are unfrozen, freeze all; else unfreeze all
            any_unfrozen = any(not getattr(m, '_debug_frozen', False) for m in enemy_marshals)
            new_state = any_unfrozen  # If any unfrozen, freeze all; else unfreeze all

            frozen_names = []
            for m in enemy_marshals:
                m._debug_frozen = new_state
                frozen_names.append(f"{m.name} ({m.nation})")

            action = "FROZEN" if new_state else "UNFROZEN"
            return {
                "success": True,
                "message": f"🧊 DEBUG: All enemies {action}\n"
                          f"Affected: {', '.join(frozen_names)}\n"
                          f"Enemy AI will {'skip these marshals' if new_state else 'act normally'}."
            }

        elif ability == "ai_turn":
            if len(parts) < 2:
                return {"success": False, "message": "Usage: /debug ai_turn <nation>\nNations: Britain, Prussia, Austria, Saxony"}
            nation = parts[1].capitalize()
            if nation not in world.enemy_nations:
                return {"success": False, "message": f"Unknown nation: {nation}\nAvailable: {', '.join(world.enemy_nations)}"}

            # Import and run AI
            from backend.ai.enemy_ai import EnemyAI
            ai = EnemyAI(self)
            results = ai.process_nation_turn(nation, world, game_state)

            # Format results
            action_summary = []
            for r in results:
                ai_action = r.get("ai_action", {})
                action_summary.append(f"  {ai_action.get('marshal', '?')}: {ai_action.get('action', '?')} -> {ai_action.get('target', '')}")

            return {
                "success": True,
                "message": f"🤖 DEBUG: Forced {nation} AI turn\n"
                          f"Actions taken: {len(results)}\n" +
                          "\n".join(action_summary) if action_summary else "No actions taken",
                "ai_results": results
            }

        elif ability == "ai_state":
            if len(parts) < 2:
                return {"success": False, "message": "Usage: /debug ai_state <marshal>"}
            marshal_name = parts[1]
            marshal, error = self._fuzzy_match_marshal(marshal_name, world)
            if error:
                return error

            # Gather state info
            from backend.models.marshal import Stance
            stance = getattr(marshal, 'stance', Stance.NEUTRAL)
            state_info = [
                f"=== AI State: {marshal.name} ({marshal.nation}) ===",
                f"Location: {marshal.location}",
                f"Strength: {marshal.strength:,} / {marshal.starting_strength:,} ({marshal.strength/marshal.starting_strength*100:.0f}%)",
                f"Morale: {marshal.morale}%",
                f"Personality: {marshal.personality}",
                f"Stance: {stance.value}",
                "",
                "== Tactical State ==",
                f"Fortified: {getattr(marshal, 'fortified', False)} (bonus: {getattr(marshal, 'defense_bonus', 0)*100:.0f}%)",
                f"Drilling: {getattr(marshal, 'drilling', False)} / Locked: {getattr(marshal, 'drilling_locked', False)}",
                f"Shock bonus: {getattr(marshal, 'shock_bonus', 0)}",
                f"Retreat recovery: {getattr(marshal, 'retreat_recovery', 0)}",
                f"Retreated this turn: {getattr(marshal, 'retreated_this_turn', False)}",
                f"Counter-punch: {getattr(marshal, 'counter_punch_available', False)}",
                "",
                "== Attack Thresholds ==",
            ]

            # Show attack threshold
            from backend.ai.enemy_ai import EnemyAI
            threshold = EnemyAI.ATTACK_THRESHOLDS.get(marshal.personality, 1.0)
            state_info.append(f"Attack threshold: {threshold} (needs {threshold}x enemy strength to attack)")

            # Find nearby enemies
            enemies = world.get_enemies_of_nation(marshal.nation)
            if enemies:
                state_info.append("")
                state_info.append("== Nearby Enemies ==")
                for enemy in enemies:
                    dist = world.get_distance(marshal.location, enemy.location)
                    ratio = marshal.strength / enemy.strength if enemy.strength > 0 else 999
                    would_attack = "YES" if ratio >= threshold else "NO"
                    state_info.append(f"  {enemy.name}: {enemy.strength:,} at {enemy.location} (dist={dist}, ratio={ratio:.2f}, attack={would_attack})")

            return {
                "success": True,
                "message": "\n".join(state_info)
            }

        # === INFO COMMANDS (no marshal needed) ===

        elif ability == "list_marshals" or ability == "marshals":
            lines = ["=== All Marshals ==="]
            for name, m in world.marshals.items():
                status = "DEAD" if m.strength <= 0 else f"{m.strength:,} troops"
                retreated = " [RETREATED]" if getattr(m, 'retreated_this_turn', False) else ""
                lines.append(f"  {name} ({m.nation}): {m.location} - {status}{retreated}")
            return {
                "success": True,
                "message": "\n".join(lines)
            }

        elif ability == "list_regions" or ability == "regions":
            lines = ["=== All Regions ==="]
            for name, r in world.regions.items():
                marshals_here = [m.name for m in world.marshals.values() if m.location == name and m.strength > 0]
                marshal_str = f" <- {', '.join(marshals_here)}" if marshals_here else ""
                lines.append(f"  {name} ({r.controller}){marshal_str}")
            return {
                "success": True,
                "message": "\n".join(lines)
            }

        # === ECONOMY TESTING (Phase 6.2) — region-based, no marshal needed ===

        elif ability == "damage_building":
            # Damage first building in a region (for testing repair command)
            if len(parts) < 2:
                return {"success": False, "message": "Usage: /debug damage_building <region>"}
            region_name = " ".join(parts[1:])
            region = world.get_region(region_name)
            if not region:
                # Fuzzy match
                for rn in world.regions:
                    if region_name.lower() in rn.lower():
                        region = world.regions[rn]
                        region_name = rn
                        break
            if not region:
                return {"success": False, "message": f"Region '{region_name}' not found."}
            if not region.buildings:
                return {"success": False, "message": f"{region_name} has no buildings."}
            for b in region.buildings:
                if not b.get("damaged"):
                    b["damaged"] = True
                    return {"success": True, "message": f"DEBUG: Damaged {b['type']} in {region_name}."}
            return {"success": True, "message": f"DEBUG: All buildings in {region_name} already damaged."}

        elif ability == "set_stability":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_stability <region> <0-100>"}
            try:
                value = int(parts[-1])
            except ValueError:
                return {"success": False, "message": "Stability must be a number 0-100."}
            region_name = " ".join(parts[1:-1])
            region = world.get_region(region_name)
            if not region:
                for rn in world.regions:
                    if region_name.lower() in rn.lower():
                        region = world.regions[rn]
                        region_name = rn
                        break
            if not region:
                return {"success": False, "message": f"Region '{region_name}' not found."}
            old = region.stability
            region.stability = max(0, min(100, value))
            return {"success": True, "message": f"DEBUG: {region_name} stability: {old} -> {region.stability}"}

        elif ability == "set_gold":
            if len(parts) < 2:
                return {"success": False, "message": "Usage: /debug set_gold <amount>"}
            try:
                value = int(parts[1])
            except ValueError:
                return {"success": False, "message": "Gold must be a number."}
            old = world.gold
            world.gold = value
            return {"success": True, "message": f"DEBUG: Gold: {old} -> {world.gold}"}

        elif ability == "set_manpower":
            # /debug set_manpower <nation> <infantry|cavalry> <amount>
            if len(parts) < 4:
                return {"success": False, "message": "Usage: /debug set_manpower <nation> <infantry|cavalry> <amount>"}
            nation = parts[1].capitalize()
            pool_type = parts[2].lower()
            if pool_type not in ("infantry", "cavalry"):
                return {"success": False, "message": "Pool type must be 'infantry' or 'cavalry'."}
            try:
                value = int(parts[3])
            except ValueError:
                return {"success": False, "message": "Amount must be a number."}
            if nation not in world.manpower_pools:
                return {"success": False, "message": f"Unknown nation: {nation}. Available: {list(world.manpower_pools.keys())}"}
            old = world.manpower_pools[nation][pool_type]
            world.manpower_pools[nation][pool_type] = max(0, value)
            return {"success": True, "message": f"DEBUG: {nation} {pool_type}: {old:,} -> {world.manpower_pools[nation][pool_type]:,}"}

        elif ability == "set_authority":
            if len(parts) < 2:
                return {"success": False, "message": "Usage: /debug set_authority <0-100>"}
            try:
                value = int(parts[1])
                value = max(0, min(100, value))
            except ValueError:
                return {"success": False, "message": "Authority must be a number 0-100"}
            old = int(world.authority_tracker.authority)
            world.authority_tracker.authority = value
            label = world.authority_tracker.get_authority_label()
            return {"success": True, "message": f"DEBUG: Authority: {old} -> {value} ({label})"}

        elif ability == "set_controller":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_controller <region> <nation>\nNations: France, Britain, Prussia, Austria, Saxony (or 'none')"}
            nation = parts[-1]
            region_name = " ".join(parts[1:-1])
            region = world.get_region(region_name)
            if not region:
                for rn in world.regions:
                    if region_name.lower() in rn.lower():
                        region = world.regions[rn]
                        region_name = rn
                        break
            if not region:
                return {"success": False, "message": f"Region '{region_name}' not found."}
            old_ctrl = region.controller or "none"
            if nation.lower() == "none":
                region.controller = None
            else:
                region.controller = nation.capitalize()
            new_ctrl = region.controller or "none"
            return {"success": True, "message": f"DEBUG: {region_name} controller: {old_ctrl} -> {new_ctrl}"}

        elif ability == "add_building":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug add_building <region> <type>\nTypes: supply_depot, fortification, training_ground, market, watchtower"}
            building_type = parts[-1].lower()
            valid_types = {"supply_depot", "fortification", "training_ground", "market", "watchtower"}
            if building_type not in valid_types:
                return {"success": False, "message": f"Invalid building type '{building_type}'.\nValid: {', '.join(sorted(valid_types))}"}
            region_name = " ".join(parts[1:-1])
            region = world.get_region(region_name)
            if not region:
                for rn in world.regions:
                    if region_name.lower() in rn.lower():
                        region = world.regions[rn]
                        region_name = rn
                        break
            if not region:
                return {"success": False, "message": f"Region '{region_name}' not found."}
            # Watchtower uses dedicated field (Phase 6 Fog - Session 35)
            if building_type == "watchtower":
                region.watchtower = "active"
                region.watchtower_turns_remaining = 0
                return {"success": True, "message": f"DEBUG: Added watchtower to {region_name}. Watchtower: active"}
            region.buildings.append({"type": building_type, "damaged": False})
            return {"success": True, "message": f"DEBUG: Added {building_type} to {region_name}. Buildings: {len(region.buildings)}"}

        # === COMMANDS THAT NEED MARSHAL ===

        if len(parts) < 2:
            return {
                "success": False,
                "message": f"Command '{ability}' requires a marshal name.\n"
                          f"Usage: /debug {ability} <marshal>"
            }

        ability = parts[0].lower()
        marshal_name = parts[1]

        # Find marshal
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Handle different debug abilities
        if ability == "counter_punch":
            if marshal.personality != 'cautious':
                return {
                    "success": False,
                    "message": f"Counter-Punch is only available for cautious marshals (Davout, Wellington). "
                              f"{marshal.name} is {marshal.personality}."
                }
            marshal.counter_punch_available = True
            marshal.counter_punch_turns = 2  # Survives one turn transition
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s counter_punch_available = True\n"
                          f"Next attack by {marshal.name} will be FREE!\n"
                          f"(Note: In normal play, this triggers when any cautious marshal successfully defends)"
            }

        elif ability == "restless":
            if marshal.personality != 'aggressive':
                return {
                    "success": False,
                    "message": f"Restlessness is only available for aggressive marshals (Ney). "
                              f"{marshal.name} is {marshal.personality}."
                }
            marshal.turns_in_defensive_stance = 5
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s turns_in_defensive_stance = 5\n"
                          f"Will trigger restlessness check at turn start with high probability."
            }

        elif ability == "set_exhaustion":
            # /debug set_exhaustion Ney 3
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_exhaustion <marshal> <count>"}
            try:
                count = int(parts[2])
            except ValueError:
                return {"success": False, "message": "Count must be a number (0-4)"}
            marshal.attacks_this_turn = max(0, min(4, count))
            penalty = marshal._get_exhaustion_penalty() * 100
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s attacks_this_turn = {marshal.attacks_this_turn}\n"
                          f"Next attack will have {penalty:.0f}% exhaustion penalty."
            }

        elif ability == "set_fortify_turns":
            # /debug set_fortify_turns Davout 8
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_fortify_turns <marshal> <turns>"}
            try:
                turns = int(parts[2])
            except ValueError:
                return {"success": False, "message": "Turns must be a number"}
            marshal.turns_fortified = max(0, turns)
            # Also ensure marshal is fortified
            if not marshal.fortified:
                marshal.fortified = True
                marshal.defense_bonus = 0.10
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s turns_fortified = {marshal.turns_fortified}\n"
                          f"fortified = {marshal.fortified}, defense_bonus = {marshal.defense_bonus*100:.0f}%\n"
                          f"End turn to see decay effect."
            }

        elif ability == "cavalry":
            current = getattr(marshal, 'cavalry', False)
            marshal.cavalry = not current
            marshal.movement_range = 2 if marshal.cavalry else 1
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s cavalry = {marshal.cavalry}\n"
                          f"Movement range: {marshal.movement_range} (can attack {marshal.movement_range} region(s) away)"
            }

        elif ability == "hold":
            if marshal.personality != 'literal':
                return {
                    "success": False,
                    "message": f"Immovable (hold) is only available for literal marshals (Grouchy). "
                              f"{marshal.name} is {marshal.personality}."
                }
            marshal.holding_position = True
            marshal.hold_region = marshal.location
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s holding_position = True (at {marshal.location})\n"
                          f"Will receive +15% defense bonus while defending here (Immovable ability)."
            }

        elif ability == "set_retreat":
            marshal.retreated_this_turn = True
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s retreated_this_turn = True\n"
                          f"Ally cover system will now protect this marshal if attacked with ally present."
            }

        elif ability == "set_recovery":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_recovery <marshal> <turns>\nTurns: 0-3 (0=max penalty, 3=recovered)"}
            try:
                turns = int(parts[2])
                turns = max(0, min(3, turns))
            except ValueError:
                return {"success": False, "message": "Turns must be a number 0-3"}

            marshal.retreat_recovery = turns
            marshal.retreating = turns > 0
            penalties = {0: "-45%", 1: "-30%", 2: "-15%", 3: "0% (recovered)"}
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s retreat_recovery = {turns}\n"
                          f"Combat effectiveness penalty: {penalties.get(turns, '?')}\n"
                          f"Blocked actions: attack, fortify, drill, aggressive stance"
            }

        elif ability == "set_strength":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_strength <marshal> <amount>"}
            try:
                amount = int(parts[2])
                amount = max(0, amount)
            except ValueError:
                return {"success": False, "message": "Amount must be a number"}

            old_strength = marshal.strength
            marshal.strength = amount
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s strength: {old_strength:,} -> {amount:,}"
            }

        elif ability == "set_morale":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_morale <marshal> <0-100>"}
            try:
                amount = int(parts[2])
                amount = max(0, min(100, amount))
            except ValueError:
                return {"success": False, "message": "Morale must be a number 0-100"}

            old_morale = marshal.morale
            marshal.morale = amount
            forced_retreat = amount <= 25
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s morale: {old_morale} -> {amount}\n"
                          f"{'⚠️ BROKEN! Will force retreat in combat.' if forced_retreat else ''}"
            }

        elif ability == "set_trust":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_trust <marshal> <0-100>"}
            try:
                amount = int(parts[2])
                amount = max(0, min(100, amount))
            except ValueError:
                return {"success": False, "message": "Trust must be a number 0-100"}

            # Get old trust value (Trust object has .value property)
            old_trust = marshal.trust.value if hasattr(marshal.trust, 'value') else marshal.trust

            # Use Trust.set() method to properly set the value
            if hasattr(marshal.trust, 'set'):
                marshal.trust.set(amount)
            else:
                # Fallback if trust is just an int (shouldn't happen)
                marshal.trust = amount

            trust_status = ""
            if amount <= 20:
                trust_status = " [REDEMPTION THRESHOLD - can trigger redemption events]"
            elif amount <= 40:
                trust_status = " [LOW TRUST - frequent objections]"
            return {
                "success": True,
                "message": f"DEBUG: {marshal.name}'s trust: {old_trust} -> {amount}{trust_status}"
            }

        elif ability == "set_vindication":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_vindication <marshal> <-5 to 5>"}
            try:
                amount = int(parts[2])
                amount = max(-5, min(5, amount))
            except ValueError:
                return {"success": False, "message": "Vindication must be a number -5 to 5"}

            old_vind = getattr(marshal, 'vindication_score', 0)
            marshal.vindication_score = amount
            effect = ""
            if amount > 0:
                effect = " [ESCALATES objections +1 level, INCREASES defiance chance]"
            elif amount < 0:
                effect = " [DE-ESCALATES objections -1 level, DECREASES defiance chance]"
            return {
                "success": True,
                "message": f"DEBUG: {marshal.name}'s vindication: {old_vind} -> {amount}{effect}"
            }

        elif ability == "set_relationship":
            if len(parts) < 4:
                return {"success": False, "message": "Usage: /debug set_relationship <marshal> <target_marshal> <-2 to 2>"}
            target_name = parts[2]
            target_marshal, t_error = self._fuzzy_match_marshal(target_name, world)
            if t_error:
                return t_error
            if target_marshal.name == marshal.name:
                return {"success": False, "message": "A marshal cannot have a relationship with themselves."}
            try:
                value = int(parts[3])
                value = max(-2, min(2, value))
            except ValueError:
                return {"success": False, "message": "Relationship must be a number -2 to 2"}

            old_rel = marshal.get_relationship(target_marshal.name)
            marshal.set_relationship(target_marshal.name, value)
            label = marshal.get_relationship_label(value)
            return {
                "success": True,
                "message": f"DEBUG: {marshal.name}'s relationship with {target_marshal.name}: {old_rel} -> {value} ({label})"
            }

        elif ability == "set_fortified":
            current = getattr(marshal, 'fortified', False)
            marshal.fortified = not current
            if marshal.fortified:
                marshal.defense_bonus = 0.05  # Start with 5%
            else:
                marshal.defense_bonus = 0
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s fortified = {marshal.fortified}\n"
                          f"Defense bonus: {marshal.defense_bonus * 100:.0f}%"
            }

        elif ability == "set_recklessness":
            # Phase 3 Cavalry Recklessness - set recklessness level for testing popup
            if not marshal.is_reckless_cavalry:
                return {
                    "success": False,
                    "message": f"Recklessness is only for reckless cavalry (aggressive + cavalry).\n"
                              f"{marshal.name}: cavalry={getattr(marshal, 'cavalry', False)}, "
                              f"personality={marshal.personality}"
                }
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_recklessness <marshal> <0-4>"}
            try:
                level = int(parts[2])
                level = max(0, min(4, level))
            except ValueError:
                return {"success": False, "message": "Recklessness must be a number 0-4"}

            old_reck = getattr(marshal, 'recklessness', 0)
            marshal.recklessness = level

            # Explain what this level does
            effects = {
                0: "No bonus/penalty",
                1: "+5% attack, -5% defense",
                2: "+10% attack, -5% defense, cannot go defensive",
                3: "+15% attack, -10% defense, POPUP before attack (Glorious Charge choice)",
                4: "+20% attack, -15% defense, AUTO-CHARGE (no popup)"
            }
            return {
                "success": True,
                "message": f"🐴 DEBUG: {marshal.name}'s recklessness: {old_reck} -> {level}\n"
                          f"Effect: {effects.get(level, '?')}\n"
                          f"Now try: '{marshal.name}, attack Wellington' to trigger the popup!"
            }

        elif ability == "set_autonomy":
            # Parse optional turns parameter
            turns = 3  # default
            if len(parts) >= 3:
                try:
                    turns = int(parts[2])
                    turns = max(1, min(10, turns))
                except ValueError:
                    pass

            # Only works on player marshals
            if marshal.nation != world.player_nation:
                return {
                    "success": False,
                    "message": f"{marshal.name} is not a {world.player_nation} marshal. "
                              f"Only player marshals can be made autonomous."
                }

            # Toggle autonomy
            if getattr(marshal, 'autonomous', False):
                # Turn off autonomy
                marshal.autonomous = False
                marshal.autonomy_turns = 0
                marshal.autonomy_reason = ""
                return {
                    "success": True,
                    "message": f"🔧 DEBUG: {marshal.name} is no longer autonomous.\n"
                              f"Player can command normally."
                }
            else:
                # Turn on autonomy
                marshal.autonomous = True
                marshal.autonomy_turns = turns
                marshal.autonomy_reason = "debug"
                marshal.autonomous_battles_won = 0
                marshal.autonomous_battles_lost = 0
                marshal.autonomous_regions_captured = 0
                return {
                    "success": True,
                    "message": f"🔧 DEBUG: {marshal.name} is now AUTONOMOUS for {turns} turns.\n"
                              f"• Will act independently at turn start using Enemy AI\n"
                              f"• Player commands will be blocked\n"
                              f"• Use 'end turn' to see Independent Command Report"
                }

        elif ability == "set_location" or ability == "move":
            if len(parts) < 3:
                regions = list(world.regions.keys()) if world.regions else []
                return {
                    "success": False,
                    "message": f"Usage: /debug set_location <marshal> <region>\n"
                              f"Regions: {', '.join(regions)}"
                }
            region_name = parts[2]

            # Fuzzy match region
            matched_region = None
            for r in world.regions.keys():
                if r.lower() == region_name.lower():
                    matched_region = r
                    break
            if not matched_region:
                # Try partial match
                for r in world.regions.keys():
                    if region_name.lower() in r.lower():
                        matched_region = r
                        break

            if not matched_region:
                regions = list(world.regions.keys())
                return {
                    "success": False,
                    "message": f"Unknown region: {region_name}\n"
                              f"Available: {', '.join(regions)}"
                }

            old_location = marshal.location
            marshal.location = matched_region
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name} teleported: {old_location} -> {matched_region}"
            }

        elif ability == "freeze":
            # Toggle AI freeze — frozen marshals are skipped by enemy AI
            frozen = getattr(marshal, '_debug_frozen', False)
            marshal._debug_frozen = not frozen
            state = "FROZEN (AI will skip)" if marshal._debug_frozen else "UNFROZEN (AI acts normally)"
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name} is now {state}"
            }

        elif ability == "list_marshals" or ability == "marshals":
            lines = ["=== All Marshals ==="]
            for name, m in world.marshals.items():
                status = "DEAD" if m.strength <= 0 else f"{m.strength:,} troops"
                admin_status = " [ADMIN]" if getattr(m, 'administrative', False) else ""
                auto_status = f" [AUTO {m.autonomy_turns}t]" if getattr(m, 'autonomous', False) else ""
                lines.append(f"  {name} ({m.nation}): {m.location} - {status}{admin_status}{auto_status}")
            return {
                "success": True,
                "message": "\n".join(lines)
            }

        elif ability == "dismiss":
            # Directly dismiss a marshal (for testing redemption without triggering disobedience)
            if marshal.nation != world.player_nation:
                return {
                    "success": False,
                    "message": f"{marshal.name} is not a {world.player_nation} marshal."
                }

            # Check last marshal protection
            field_marshals = world.get_field_marshals()
            if len(field_marshals) <= 1:
                return {
                    "success": False,
                    "message": f"Cannot dismiss {marshal.name} - last field marshal!"
                }

            # Transfer troops to nearest ally within 3 regions
            troop_count = marshal.strength
            result = world.find_nearest_marshal_within_range(
                from_location=marshal.location,
                nation=marshal.nation,
                max_distance=3,
                exclude_marshal=marshal.name
            )

            if result:
                nearest, distance = result
                nearest.add_troops(troop_count)
                transfer_msg = f"{troop_count:,} troops transferred to {nearest.name}."
            else:
                transfer_msg = f"{troop_count:,} troops dispersed (no ally within 3 regions)."

            # Remove marshal
            del world.marshals[marshal.name]

            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name} DISMISSED. {transfer_msg}"
            }

        elif ability == "admin" or ability == "administrative":
            # Directly put marshal in administrative role (for testing)
            if marshal.nation != world.player_nation:
                return {
                    "success": False,
                    "message": f"{marshal.name} is not a {world.player_nation} marshal."
                }

            # Check if already admin
            if getattr(marshal, 'administrative', False):
                # Toggle off
                marshal.administrative = False
                strength = getattr(marshal, 'administrative_strength', 0)
                location = getattr(marshal, 'administrative_location', 'Paris')
                marshal.strength = strength
                marshal.location = location
                world.bonus_actions = max(0, getattr(world, 'bonus_actions', 0) - 1)
                return {
                    "success": True,
                    "message": f"🔧 DEBUG: {marshal.name} restored from admin. "
                              f"{strength:,} troops at {location}. "
                              f"Max actions now: {world.calculate_max_actions()}"
                }

            # Check last marshal protection
            field_marshals = world.get_field_marshals()
            if len(field_marshals) <= 1:
                return {
                    "success": False,
                    "message": f"Cannot put {marshal.name} in admin - last field marshal!"
                }

            # Check admin cap
            admin_marshals = world.get_admin_marshals()
            if len(admin_marshals) >= 1:
                return {
                    "success": False,
                    "message": f"Already have admin: {admin_marshals[0].name}. Max 1 admin allowed."
                }

            # Put in admin
            marshal.administrative = True
            marshal.administrative_strength = marshal.strength
            marshal.administrative_location = marshal.location
            marshal.strength = 0
            marshal.location = None
            world.bonus_actions = getattr(world, 'bonus_actions', 0) + 1

            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name} -> ADMIN ROLE. "
                          f"{marshal.administrative_strength:,} troops frozen. "
                          f"Max actions now: {world.calculate_max_actions()}"
            }

        # Economy debug commands (damage_building, set_stability, set_gold)
        # moved above marshal resolution block — they take regions, not marshals.

        elif ability == "list_regions" or ability == "regions":
            lines = ["=== All Regions ==="]
            for name, r in world.regions.items():
                marshals_here = [m.name for m in world.marshals.values() if m.location == name and m.strength > 0]
                marshal_str = f" <- {', '.join(marshals_here)}" if marshals_here else ""
                lines.append(f"  {name} ({r.controller}){marshal_str}")
            return {
                "success": True,
                "message": "\n".join(lines)
            }

        else:
            return {
                "success": False,
                "message": f"Unknown debug command: {ability}\n"
                          "Use /debug without args to see all commands."
            }

    # ========================================
    # STANCE SYSTEM (Phase 2.7)
    # ========================================

    def _get_stance_change_cost(self, current_stance: Stance, target_stance: Stance) -> int:
        """
        Calculate action cost for stance transition.

        Action Costs:
        - Any → Neutral: FREE (0 actions)
        - Neutral → Defensive: 1 action
        - Neutral → Aggressive: 1 action
        - Defensive ↔ Aggressive: 2 actions (must go through neutral mentally)

        Args:
            current_stance: Marshal's current stance
            target_stance: Target stance to transition to

        Returns:
            Action cost (0, 1, or 2)
        """
        if current_stance == target_stance:
            return 0  # No change needed

        # Returning to neutral is always free
        if target_stance == Stance.NEUTRAL:
            return 0

        # From neutral to any stance costs 1
        if current_stance == Stance.NEUTRAL:
            return 1

        # Direct transition between defensive and aggressive costs 2
        # (Defensive ↔ Aggressive without going through neutral)
        return 2

    def _execute_stance_change(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute stance change order.

        Stance transitions affect combat modifiers:
        - NEUTRAL: 0% attack, 0% defense (default)
        - DEFENSIVE: -10% attack, +15% defense
        - AGGRESSIVE: +15% attack, -10% defense

        The action cost is calculated dynamically:
        - Any → Neutral: FREE
        - Neutral → Def/Agg: 1 action
        - Def ↔ Agg: 2 actions
        """
        marshal_name = command.get("marshal")
        # Support both "target_stance" and "target" as parameter names
        # (AI uses "target", player commands may use "target_stance")
        # Parse results may have None fields — guard before .lower()/.strip()
        target_stance_str = command.get("target_stance") or command.get("target")
        if not target_stance_str:
            return {
                "success": False,
                "message": "No stance specified. Valid stances: neutral, defensive, aggressive"
            }
        target_stance_str = target_stance_str.lower()
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Auto-break square formation (Session 67)
        self._auto_break_square(marshal, "stance_change")

        # Parse target stance
        stance_map = {
            "neutral": Stance.NEUTRAL,
            "defensive": Stance.DEFENSIVE,
            "defense": Stance.DEFENSIVE,
            "defend": Stance.DEFENSIVE,
            "aggressive": Stance.AGGRESSIVE,
            "attack": Stance.AGGRESSIVE,
            "offense": Stance.AGGRESSIVE,
        }
        target_stance = stance_map.get(target_stance_str)

        if not target_stance:
            return {
                "success": False,
                "message": f"Unknown stance: '{target_stance_str}'. Valid stances: neutral, defensive, aggressive"
            }

        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)

        # Check if already in target stance
        if current_stance == target_stance:
            return {
                "success": False,
                "message": f"{marshal.name} is already in {target_stance.value.upper()} stance."
            }

        # Check if drilling (can't change stance while drilling)
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return {
                "success": False,
                "message": f"{marshal.name} is engaged in drill exercises and cannot change stance."
            }

        # Check if retreating (can't change to aggressive while recovering)
        if getattr(marshal, 'retreating', False) and target_stance == Stance.AGGRESSIVE:
            return {
                "success": False,
                "message": f"{marshal.name} is recovering from retreat and cannot adopt aggressive stance."
            }

        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS CHECK (Phase 3)
        # High recklessness blocks defensive/neutral stances
        # ════════════════════════════════════════════════════════════
        can_use, block_reason = marshal.can_use_stance(target_stance.value)
        if not can_use:
            return {
                "success": False,
                "message": block_reason,
                "recklessness": getattr(marshal, 'recklessness', 0)
            }

        # Calculate action cost
        action_cost = self._get_stance_change_cost(current_stance, target_stance)

        # Check if player has enough actions (for non-free transitions)
        if action_cost > 0 and world.actions_remaining < action_cost:
            return {
                "success": False,
                "message": f"Stance change requires {action_cost} action(s), but only {world.actions_remaining} remaining."
            }

        # Execute the stance change
        old_stance = current_stance
        marshal.stance = target_stance

        # Build descriptive message
        stance_effects = {
            Stance.NEUTRAL: "balanced posture (no modifiers)",
            Stance.DEFENSIVE: "-10% attack, +15% defense",
            Stance.AGGRESSIVE: "+15% attack, -10% defense"
        }

        message = f"{marshal.name} shifts from {old_stance.value.upper()} to {target_stance.value.upper()} stance. "
        message += f"Effect: {stance_effects[target_stance]}."

        if action_cost == 0:
            message += " (Free action)"
        elif action_cost == 2:
            message += f" (Cost: {action_cost} actions - major tactical shift)"

        # NOTE: Action consumption is handled by the main execute() method
        # We return a special flag to indicate variable action cost
        return {
            "success": True,
            "message": message,
            "variable_action_cost": action_cost,  # Special: variable cost
            "events": [{
                "type": "stance_change",
                "marshal": marshal.name,
                "from_stance": old_stance.value,
                "to_stance": target_stance.value,
                "action_cost": action_cost
            }],
            "new_state": game_state
        }

    # ════════════════════════════════════════════════════════════
    # CAVALRY RECKLESSNESS SYSTEM (Phase 3)
    # ════════════════════════════════════════════════════════════

    def _execute_charge(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute Glorious Charge - powerful cavalry attack with 2x damage.

        Requirements:
        - Marshal must be reckless cavalry (cavalry + aggressive)
        - Recklessness must be >= 1
        - Must have valid attack target

        Effects:
        - 2x damage dealt AND taken
        - Resets recklessness to 0 after (win or lose)

        Unlike normal attacks at recklessness 3+, the explicit "charge"
        command bypasses the popup and executes immediately.

        If no marshal specified, checks for pending glorious charge and uses that.
        """
        marshal_name = command.get("marshal")
        target = command.get("target")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Game state error"}

        # If no marshal specified, check for pending glorious charge
        if not marshal_name:
            # Look for marshal with pending charge
            for m in world.marshals.values():
                if getattr(m, 'pending_glorious_charge', False) and m.nation == world.player_nation:
                    # Found pending charge - route to respond handler
                    return self.respond_to_glorious_charge("charge", world)

            return {"success": False, "message": "Charge requires a marshal. Try: 'Ney, charge Wellington'"}

        marshal = world.get_marshal(marshal_name)
        if not marshal:
            return {"success": False, "message": f"Marshal '{marshal_name}' not found"}

        # Must be reckless cavalry
        if not marshal.is_reckless_cavalry:
            if not getattr(marshal, 'cavalry', False):
                return {
                    "success": False,
                    "message": f"{marshal.name} is not cavalry and cannot execute a Glorious Charge."
                }
            else:
                return {
                    "success": False,
                    "message": f"{marshal.name} is cavalry but not aggressive enough for Glorious Charge. "
                              f"Only reckless cavalry commanders (aggressive cavalry) can charge."
                }

        # Must have recklessness >= 1
        recklessness = getattr(marshal, 'recklessness', 0)
        if recklessness < 1:
            return {
                "success": False,
                "message": f"{marshal.name} needs to build momentum first! "
                          f"Win battles as attacker to increase recklessness (currently {recklessness}).",
                "recklessness": recklessness
            }

        # Must have target
        if not target:
            return {
                "success": False,
                "message": f"Charge requires a target! Try: '{marshal.name}, charge [enemy name]'"
            }

        # Execute as a Glorious Charge attack
        return self._execute_glorious_charge(marshal, target, world, game_state)

    def _execute_restrain(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute restrain - choose normal attack instead of Glorious Charge.

        This is used when the player types 'restrain' to respond to a
        Glorious Charge popup with a normal attack instead.
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Game state error"}

        # Look for marshal with pending charge
        for m in world.marshals.values():
            if getattr(m, 'pending_glorious_charge', False) and m.nation == world.player_nation:
                # Found pending charge - route to respond handler
                return self.respond_to_glorious_charge("restrain", world)

        return {
            "success": False,
            "message": "No pending Glorious Charge to restrain. Use 'attack' for normal attacks."
        }

    # ════════════════════════════════════════════════════════════
    # CANCEL STRATEGIC ORDER (Phase E)
    # ════════════════════════════════════════════════════════════

    def _execute_cancel(self, command: Dict, game_state: Dict) -> Dict:
        """
        Cancel a marshal's active strategic order.

        Costs 1 action. Applies -3 trust.
        If no active order, returns error (no cost).
        """
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "Game state error"}

        marshal_name = command.get("marshal")
        if not marshal_name:
            # Try to find a marshal with an active strategic order
            for m in world.marshals.values():
                if m.nation == world.player_nation and m.in_strategic_mode:
                    marshal_name = m.name
                    break
            if not marshal_name:
                return {"success": False,
                        "message": "No marshal has an active strategic order to cancel."}

        marshal = world.get_marshal(marshal_name)
        if not marshal:
            return {"success": False, "message": f"Marshal '{marshal_name}' not found."}

        if not marshal.in_strategic_mode and not getattr(marshal, 'pending_interrupt', None):
            # Graceful cancel — may be canceling from a clarification popup
            # (before order was created) or just no active order
            return {"success": True, "no_action_cost": True,
                    "message": f"{marshal.name} awaits further orders."}

        # Get order details for flavorful message
        old_order = marshal.strategic_order
        old_command = old_order.command_type if old_order else None
        old_target = old_order.target if old_order else None

        # Cancel the order
        marshal.strategic_order = None
        marshal.pending_interrupt = None

        # Clear HOLD state if applicable
        if getattr(marshal, 'holding_position', False):
            marshal.holding_position = False
            marshal.hold_region = ""

        # Trust penalty: -3 for mid-march, 0 for first-step cancel
        is_first_step = (old_order and old_order.started_turn == world.current_turn)
        trust_change = 0 if is_first_step else -3
        if trust_change != 0 and hasattr(marshal, 'trust'):
            marshal.trust.modify(trust_change)

        # Flavorful message varies by order type
        if old_command == "MOVE_TO":
            msg = f"{marshal.name} halts his march and awaits new orders."
        elif old_command == "PURSUE":
            msg = f"{marshal.name} breaks off the pursuit."
        elif old_command == "HOLD":
            msg = f"{marshal.name} abandons the position."
        elif old_command == "SUPPORT":
            msg = f"{marshal.name} breaks off from supporting {old_target}."
        else:
            msg = f"{marshal.name} acknowledges. Standing down."

        return {
            "success": True,
            "message": msg,
            "trust_change": trust_change,
            "order_cleared": True,
        }

    def _execute_glorious_charge(self, marshal, target: str, world: WorldState, game_state: Dict) -> Dict:
        """
        Execute the actual Glorious Charge combat.

        This is the internal method that performs the 2x damage attack.
        Called by:
        - _execute_charge (explicit charge command)
        - respond_to_glorious_charge (popup response)
        - auto-charge at recklessness 4+
        """
        # Auto-break square formation (Session 67)
        self._auto_break_square(marshal, "attack")

        # ARTILLERY: Guns don't charge
        if getattr(marshal, 'artillery', False):
            return {
                "success": False,
                "message": f"{marshal.name}'s artillery cannot execute a Glorious Charge. Guns don't charge."
            }

        # Find target
        target_marshal = None

        # Try exact name match first
        for m in world.marshals.values():
            if m.name.lower() == target.lower() and m.nation != marshal.nation:
                target_marshal = m
                break

        # Try fuzzy match
        if not target_marshal:
            target_region = world.get_region(target)
            if target_region:
                # Find enemy in that region
                for m in world.marshals.values():
                    if m.location == target_region.name and m.nation != marshal.nation:
                        target_marshal = m
                        break

        if not target_marshal:
            return {
                "success": False,
                "message": f"Cannot find target '{target}' for Glorious Charge."
            }

        if target_marshal.strength <= 0:
            return {
                "success": False,
                "message": f"{target_marshal.name} has no troops to fight!"
            }

        # ════════════════════════════════════════════════════════════
        # TERRAIN CHARGE BLOCKING (Phase 6.1): Safety net fallthrough
        # Mountains/forest/urban block cavalry charges — fall through
        # to normal attack so the attack still happens without bonus
        # ════════════════════════════════════════════════════════════
        charge_region = world.get_region(target_marshal.location)
        if charge_region and charge_region.terrain in CHARGE_BLOCKED_TERRAIN:
            terrain_name = charge_region.terrain.replace("_", " ").title()
            print(f"  [CHARGE BLOCKED] {terrain_name} terrain blocks charge — falling through to normal attack")
            result = self._execute_attack(marshal, target, world, game_state, skip_reckless_popup=True)
            result["charge_blocked_by_terrain"] = True
            result["terrain"] = charge_region.terrain
            if result.get("success"):
                result["message"] = (
                    f"🐴⛔ {marshal.name}'s cavalry cannot charge in {terrain_name} terrain! "
                    f"Attacking without charge bonus.\n\n{result.get('message', '')}"
                )
            return result

        # Check range (cavalry can charge 2 regions)
        distance = world.get_distance(marshal.location, target_marshal.location)
        if distance > marshal.movement_range:
            return {
                "success": False,
                "message": f"{target_marshal.name} is too far for Glorious Charge! "
                          f"Distance: {distance}, Range: {marshal.movement_range}"
            }

        # Check for leapfrog (same as normal attack)
        if distance == 2:
            origin_region = world.get_region(marshal.location)
            target_location = target_marshal.location
            middle_regions = []
            for adj in origin_region.adjacent_regions:
                if world.get_distance(adj, target_location) == 1:
                    middle_regions.append(adj)

            for middle in middle_regions:
                enemies_in_middle = [
                    m for m in world.get_marshals_in_region(middle)
                    if m.nation != marshal.nation and m.strength > 0
                ]
                if enemies_in_middle:
                    blocking_enemy = enemies_in_middle[0]
                    return {
                        "success": False,
                        "message": f"Cannot charge through {middle} - {blocking_enemy.name} blocks the path!",
                        "blocked_by": blocking_enemy.name
                    }

        # Execute combat with 2x damage multiplier
        recklessness_before = getattr(marshal, 'recklessness', 0)

        # Read terrain from defender's region
        charge_defender_region = world.get_region(target_marshal.location)
        charge_terrain = charge_defender_region.terrain if charge_defender_region else "plains"
        charge_fort_bonus = 0.25 if charge_defender_region and charge_defender_region.has_building("fortification") else 0.0

        # Capture pre-battle strengths for war damage threshold (Phase 6.2.C)
        pre_battle_atk = marshal.strength
        pre_battle_def = target_marshal.strength
        charge_battle_region = target_marshal.location

        # Get combat result with glorious charge flag
        combat_result = self.combat_resolver.resolve_battle(
            attacker=marshal,
            defender=target_marshal,
            terrain=charge_terrain,
            glorious_charge=True,  # 2x damage multiplier
            fortification_bonus=charge_fort_bonus
        )

        # Log battle event
        self._log_battle_event(combat_result, charge_battle_region, world)

        # Fog of War (Session 34A): Battle grants FULL visibility on battle region
        world.update_intel_from_battle(charge_battle_region, world.current_turn)

        # Apply war damage + stability hit to battle region (Phase 6.2.C)
        self._apply_battle_effects_to_region(
            charge_battle_region, pre_battle_atk, pre_battle_def, world
        )

        # Record battle for cannon fire detection
        world = game_state.get("world")
        if world:
            world.record_battle(target_marshal.location, marshal.name, target_marshal.name,
                                combat_result.get("outcome", "unknown"))

        # Record battle for diplomacy war score
        from backend.game_logic.diplomacy import record_battle as record_diplo_battle
        outcome = combat_result.get("outcome", "")
        atk_won = "attacker" in outcome and "victory" in outcome
        def_won = "defender" in outcome and "victory" in outcome
        diplo_winner = marshal.nation if atk_won else (target_marshal.nation if def_won else None)
        if diplo_winner:
            record_diplo_battle(
                world,
                attacker_nation=marshal.nation,
                defender_nation=target_marshal.nation,
                winner_nation=diplo_winner,
                attacker_casualties=int(combat_result.get("attacker", {}).get("casualties", 0)),
                defender_casualties=int(combat_result.get("defender", {}).get("casualties", 0)),
            )

        # ALWAYS reset recklessness after Glorious Charge
        marshal.reset_recklessness()

        # Move attacker if victorious and still alive
        attacker_won = combat_result.get("attacker_won", False)
        movement_msg = ""
        if attacker_won and marshal.strength > 0:
            target_location = target_marshal.location
            if marshal.location != target_location:
                marshal.move_to(target_location)
                # Movement attrition on charge advance (Phase 6.2.F)
                charge_attrition = self._calculate_movement_attrition(marshal, target_location, world)
                combat_result["attacker_moved"] = True
                combat_result["attacker_new_location"] = target_location
                movement_msg = f" {marshal.name} advances into {target_location}."
                if charge_attrition["total_losses"] > 0:
                    charge_march_note = f" ({charge_attrition['total_losses']:,} lost to march"
                    if charge_attrition.get("depot_bonus"):
                        charge_march_note += " — forward supply lines reduce losses"
                    charge_march_note += ")"
                    movement_msg += charge_march_note

        # Check if enemy was destroyed
        enemy_destroyed_msg = ""
        if target_marshal.strength <= 0:
            enemy_destroyed_msg = f" {target_marshal.name}'s army is destroyed!"

        # Build charge message - use "description" key from combat resolver
        charge_message = f"🐴⚔️ GLORIOUS CHARGE! {marshal.name} leads a devastating cavalry assault!\n\n"
        charge_message += combat_result.get("description", "")
        charge_message += enemy_destroyed_msg + movement_msg
        charge_message += f"\n\n[color=#cd6b6b]Recklessness reset: {recklessness_before} → 0[/color]"

        charge_result = {
            "success": True,
            "message": charge_message,
            "glorious_charge": True,
            "damage_multiplier": 2,
            "recklessness_before": recklessness_before,
            "recklessness_after": 0,
            "combat_result": combat_result,
            "events": [{
                "type": "glorious_charge",
                "marshal": marshal.name,
                "target": target_marshal.name,
                "attacker_won": attacker_won,
                "recklessness_reset": True
            }],
            "new_state": game_state
        }
        # Berthier's After-Action Report
        if combat_result.get("battle_report"):
            charge_result["battle_report"] = combat_result["battle_report"]
        return charge_result

    def respond_to_glorious_charge(self, response: str, world: WorldState) -> Dict:
        """
        Handle player response to Glorious Charge popup.

        Called when player responds to the popup that appears at recklessness 3.

        Args:
            response: "charge" or "restrain"
            world: WorldState instance

        Returns:
            Result dict
        """
        # Find marshal with pending charge
        pending_marshal = None
        for m in world.marshals.values():
            if getattr(m, 'pending_glorious_charge', False) and m.nation == world.player_nation:
                pending_marshal = m
                break

        if not pending_marshal:
            return {
                "success": False,
                "message": "No pending Glorious Charge to respond to."
            }

        target = getattr(pending_marshal, 'pending_charge_target', '')
        print(f"[GLORIOUS CHARGE] Marshal: {pending_marshal.name}, stored target: '{target}'")

        # Clear pending state
        pending_marshal.pending_glorious_charge = False
        pending_marshal.pending_charge_target = ""

        # Verify target still exists and is reachable
        target_marshal = world.get_marshal(target)
        print(f"[GLORIOUS CHARGE] get_marshal('{target}') returned: {target_marshal}")
        print(f"[GLORIOUS CHARGE] Available marshals: {list(world.marshals.keys())}")
        if not target_marshal:
            # Try to find by location
            for m in world.marshals.values():
                if m.location == target and m.nation != pending_marshal.nation:
                    target_marshal = m
                    break

        if not target_marshal or target_marshal.strength <= 0:
            return {
                "success": False,
                "message": "Target has retreated or been destroyed! The charge cannot proceed."
            }

        # Check if target is still in range
        distance = world.get_distance(pending_marshal.location, target_marshal.location)
        if distance > pending_marshal.movement_range:
            return {
                "success": False,
                "message": f"{target_marshal.name} is no longer in range! The charge cannot proceed."
            }

        game_state = {"world": world}

        if response.lower() == "charge":
            # Execute Glorious Charge
            return self._execute_glorious_charge(pending_marshal, target_marshal.name, world, game_state)
        else:
            # Restrain - execute normal attack, recklessness continues
            # Pass skip_reckless_popup=True to avoid retriggering the popup
            result = self._execute_attack(pending_marshal, target_marshal.name, world, game_state, skip_reckless_popup=True)
            if result.get("success"):
                result["message"] = f"[{pending_marshal.name} is restrained - normal attack]\n\n" + result.get("message", "")
            return result

    def _execute_retreat_action(self, marshal, world: WorldState, game_state: Dict) -> Dict:
        """
        Execute retreat order - FREE ACTION, initiates recovery from combat penalty.

        Retreat is a strategic withdrawal that:
        - Moves marshal 1 region toward friendly territory (Paris)
        - Initiates recovery state (recovery from penalty to 0%)
        - Costs 0 actions (free to order retreat)

        STANCE-BASED PENALTIES:
        - AGGRESSIVE: -55% initial, PLUS 5% troop loss (caught overextended!)
        - NEUTRAL: -45% initial (standard)
        - DEFENSIVE: -35% initial (orderly withdrawal)

        Recovery stages (all stances recover same rate):
        - Stage 0: Initial penalty (varies by stance)
        - Stage 1: -30% effectiveness
        - Stage 2: -15% effectiveness
        - Stage 3: 0% (recovered, state cleared)

        BUG FIXES (BUG-008/009/010):
        - Only allows retreat when actually in danger
        - Uses safe pathfinding to avoid enemy threat zones
        - Triggers Fighting Retreat for Ney when enemies adjacent
        """
        # Find retreat destination
        current_region = world.get_region(marshal.location)
        if not current_region:
            return {"success": False, "message": f"Invalid location: {marshal.location}"}

        # ════════════════════════════════════════════════════════════
        # BUG FIX: Prevent double retreat in same turn
        # A marshal can only retreat once per turn (forced or ordered)
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'retreated_this_turn', False):
            return {
                "success": False,
                "message": f"{marshal.name} has already retreated this turn. Cannot retreat again."
            }

        # ════════════════════════════════════════════════════════════
        # BUG-010 FIX: Check if marshal is actually in danger
        # ════════════════════════════════════════════════════════════
        if not world.is_in_danger(marshal.name):
            return {
                "success": False,
                "message": f"{marshal.name} is not in danger. No retreat necessary. Use 'move' to reposition."
            }

        # ════════════════════════════════════════════════════════════
        # BUG-009 FIX: Find SAFE retreat destination (avoids threat zones)
        # Pass nearest threat location to retreat AWAY from danger
        # ════════════════════════════════════════════════════════════
        threats = world.get_threatening_enemies(marshal.name)
        nearest_threat_location = threats[0].location if threats else None
        best_region = world.get_safe_retreat_destination(marshal.name, nearest_threat_location)

        if not best_region:
            # Get threatening enemies for message
            threat_names = ", ".join([t.name for t in threats[:3]])  # Show first 3
            return {
                "success": False,
                "message": f"{marshal.name} is surrounded! No safe retreat route. Threatening enemies: {threat_names}"
            }

        # ════════════════════════════════════════════════════════════
        # STANCE-BASED RETREAT PENALTIES
        # ════════════════════════════════════════════════════════════
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)
        troop_loss = 0
        troop_loss_msg = ""
        stance_penalty_msg = ""

        if current_stance == Stance.AGGRESSIVE:
            # Aggressive retreat is costly - caught overextended!
            initial_penalty = "-55%"
            troop_loss_percent = 0.05  # 5% troop loss
            troop_loss = int(marshal.strength * troop_loss_percent)
            marshal.take_casualties(troop_loss)
            troop_loss_msg = f" Lost {troop_loss:,} troops in the chaotic withdrawal!"
            stance_penalty_msg = " (Aggressive stance made retreat costly)"
        elif current_stance == Stance.DEFENSIVE:
            # Defensive retreat is more orderly
            initial_penalty = "-35%"
            stance_penalty_msg = " (Defensive stance enabled orderly withdrawal)"
        else:
            # Neutral - standard retreat
            initial_penalty = "-45%"

        # ════════════════════════════════════════════════════════════
        # FIGHTING RETREAT (Phase 2.8)
        # TRIGGER: Ney (aggressive + cavalry) retreats with enemies threatening
        # EFFECT: Attack enemies while retreating with +10% bonus
        # - Attacks STRONGEST enemy first
        # - If multiple enemies in same tile, fights ALL of them
        # ════════════════════════════════════════════════════════════
        fighting_retreat_message = ""
        fighting_retreat_events = []
        old_location = marshal.location

        is_cavalry = getattr(marshal, 'cavalry', False)
        is_aggressive = getattr(marshal, 'personality', '') == 'aggressive'

        if is_cavalry and is_aggressive:
            threatening_enemies = world.get_threatening_enemies(marshal.name)

            if threatening_enemies:
                fighting_retreat_message = (
                    f"\n========================================\n"
                    f"  [!] FIGHTING RETREAT! (+10% bonus) [!]  \n"
                    f"========================================\n"
                    f"{marshal.name}'s cavalry refuses to flee quietly!\n"
                )

                # Group enemies by location, prioritize same tile
                enemies_same_tile = [e for e in threatening_enemies if e.location == old_location]
                enemies_adjacent = [e for e in threatening_enemies if e.location != old_location]

                # Fight ALL enemies in same tile, then strongest adjacent
                enemies_to_fight = []
                if enemies_same_tile:
                    # Fight ALL enemies in same tile (sorted by strength, strongest first)
                    enemies_to_fight = sorted(enemies_same_tile, key=lambda e: e.strength, reverse=True)
                else:
                    # Fight the STRONGEST adjacent enemy
                    strongest = max(enemies_adjacent, key=lambda e: e.strength)
                    enemies_to_fight = [strongest]

                total_casualties = 0
                for target_enemy in enemies_to_fight:
                    # Calculate damage (10% bonus from Fighting Retreat ability)
                    fighting_retreat_bonus = 0.10
                    base_damage = int(target_enemy.strength * 0.05)  # 5% base damage
                    bonus_damage = int(base_damage * (1 + fighting_retreat_bonus))  # +10% from ability

                    # Apply casualties to enemy
                    target_enemy.take_casualties(bonus_damage)
                    target_enemy.adjust_morale(-5)  # Minor morale hit
                    total_casualties += bonus_damage

                    fighting_retreat_message += f"  -> Cavalry charges {target_enemy.name}! {bonus_damage:,} casualties inflicted.\n"

                    fighting_retreat_events.append({
                        "type": "fighting_retreat",
                        "marshal": marshal.name,
                        "target": target_enemy.name,
                        "casualties_inflicted": bonus_damage,
                        "ability": "Fighting Retreat",
                        "bonus": "+10% attack"
                    })

                fighting_retreat_message += f"[FIGHTING RETREAT] Total enemy casualties: {total_casualties:,} (+10% cavalry bonus)\n"

        # Execute retreat
        marshal.move_to(best_region)

        # Movement attrition on retreat (Phase 6.2.F) — halved rate
        retreat_attrition = self._calculate_movement_attrition(marshal, best_region, world, is_retreat=True)

        # Track if drill was cancelled for message
        drill_was_active = getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)

        # Enter retreat recovery state
        marshal.retreating = True
        marshal.retreat_recovery = 0  # Intentional: retreating again resets recovery progress
        marshal.retreated_this_turn = True  # Mark for ally covering system

        # Clear any offensive states
        marshal.drilling = False
        marshal.drilling_locked = False
        marshal.drill_complete_turn = -1
        marshal.shock_bonus = 0

        # Reset stance to NEUTRAL on retreat (can't maintain aggressive/defensive while retreating)
        old_stance_value = current_stance.value
        marshal.stance = Stance.NEUTRAL

        # Build message with optional drill cancellation note
        retreat_message = fighting_retreat_message  # Start with fighting retreat message if any
        retreat_message += f"{marshal.name} retreats from {old_location} to {best_region}.{troop_loss_msg} "
        if drill_was_active:
            retreat_message += "Drill cancelled. "
        if retreat_attrition["total_losses"] > 0:
            retreat_message += f" ({retreat_attrition['total_losses']:,} lost to march)"
        retreat_message += f" Army begins recovery (currently at {initial_penalty} effectiveness).{stance_penalty_msg} "
        retreat_message += "Will recover over 3 turns."

        # Add final fighting retreat message
        if fighting_retreat_events:
            retreat_message += f"\n{marshal.name} withdraws to {best_region}, bloodied but defiant."

        # Build events list
        events = [{
            "type": "retreat",
            "marshal": marshal.name,
            "from": old_location,
            "to": best_region,
            "recovery_stage": 0,
            "penalty": initial_penalty,
            "previous_stance": old_stance_value,
            "troop_loss": troop_loss
        }]

        # Add fighting retreat events if they occurred
        for fr_event in fighting_retreat_events:
            events.insert(0, fr_event)

        return {
            "success": True,
            "message": retreat_message,
            "events": events,
            "new_state": game_state
        }

    # ========================================
    # DISOBEDIENCE SYSTEM (Phase 2)
    # ========================================

    def _handle_strategic_objection_from_endpoint(self, choice: str, game_state: Dict) -> Dict:
        """
        Handle strategic objection response from /respond_to_objection endpoint.

        Maps frontend choices ("trust", "insist", "compromise") to strategic
        response types ("preferred", "proceed", "compromise") and re-executes
        the strategic command with objection_response set.

        Args:
            choice: 'trust', 'insist', or 'compromise'
            game_state: Current game state dict with 'world' key

        Returns:
            Result dict with execution outcome
        """
        world: WorldState = game_state.get("world")
        objection = world.pending_strategic_objection

        # Map frontend choice to strategic response
        choice_mapping = {
            "trust": "preferred",
            "insist": "proceed",
            "compromise": "compromise"
        }
        strategic_response = choice_mapping.get(choice, "proceed")

        # Get stored objection data
        marshal_name = objection.get("marshal_name")
        original_command = objection.get("original_command", {})
        parsed_command = objection.get("parsed_command", {})
        strategic_type = objection.get("strategic_type")
        path = objection.get("path", [])
        target = objection.get("target")

        # Get the marshal
        marshal = world.get_marshal(marshal_name)
        if not marshal:
            world.pending_strategic_objection = None
            return {
                "success": False,
                "message": f"Marshal {marshal_name} not found"
            }

        # Add objection response and preferred/compromise data to command
        original_command["objection_response"] = strategic_response
        original_command["preferred_action"] = objection.get("options", [{}])[1] if len(objection.get("options", [])) > 1 else None
        # Extract inner "compromise" dict from the options entry (the entry has type/text/compromise structure)
        options_list = objection.get("options", [])
        compromise_option = options_list[2] if len(options_list) > 2 else {}
        original_command["compromise"] = compromise_option.get("compromise") if isinstance(compromise_option, dict) else None

        # V2: Pass scaled trust values through to response handler
        original_command["v2_insist_penalty"] = objection.get("insist_penalty", -10)
        original_command["v2_trust_gain"] = objection.get("trust_gain", 3)
        original_command["v2_compromise_gain"] = objection.get("compromise_gain", COMPROMISE_TRUST_GAIN)

        # Clear the pending strategic objection BEFORE re-execution
        world.pending_strategic_objection = None

        # Record response in authority tracker (V2b: enriched with turn)
        authority_event = world.authority_tracker.record_response(choice, world.current_turn)

        # ════════════════════════════════════════════════════════════
        # C1 fix: V2b STRATEGIC DEFIANCE CHECK
        # Mirror of tactical defiance (Step 17): after "insist" + STRONG/EXTREME
        # ════════════════════════════════════════════════════════════
        concern_level_str = objection.get("concern_level", "NONE")
        concern_level_val = ConcernLevel[concern_level_str] if concern_level_str in ConcernLevel.__members__ else ConcernLevel.NONE

        if choice == "insist" and marshal and concern_level_val >= ConcernLevel.STRONG:
            from backend.commands.defiance import (
                calculate_defiance_chance, get_defiant_action,
                defiance_succeeded, apply_defiance_outcome
            )
            from backend.notifications import (
                create_notification, NotificationPriority, MARSHAL_DEFIED_ORDER
            )

            # Apply insist trust penalty up front (normally done by
            # _handle_strategic_objection_response, but defiance may return early).
            # Track via flag so we can skip it in the fallthrough path.
            v2_insist_penalty = original_command.get("v2_insist_penalty", -10)
            _trust_penalty_applied = False
            if hasattr(marshal, 'modify_trust'):
                marshal.modify_trust(v2_insist_penalty)
                _trust_penalty_applied = True

            # N7 fix: No defiance if marshal is broken/retreating (stale objection via save/load)
            if getattr(marshal, 'broken', False) or getattr(marshal, 'retreating', False):
                defiance_chance = 0.0
            else:
                defiance_chance = calculate_defiance_chance(marshal, concern_level_val, world)
            defiance_roll = random.random()

            if defiance_roll < defiance_chance:
                # ═══ STRATEGIC DEFIANCE FIRES ═══
                print(f"  [DEFIANCE] {marshal_name} defies strategic order ({strategic_type})! "
                      f"(roll={defiance_roll:.2f} < chance={defiance_chance:.2f})")

                original_action = strategic_type  # e.g., "HOLD", "SUPPORT", "PURSUE"
                defiant_action = get_defiant_action(marshal, original_action)

                if defiant_action is None:
                    defiant_action = "wait"

                # N3 fix: AP follows action taken — defiant action is always tactical (1 AP)
                # The marshal ignores the strategic order and does their own thing.
                defiance_free_actions = ["retreat", "break_square"]
                if defiant_action not in defiance_free_actions:
                    world.use_action(defiant_action)

                pre_battle_strength = marshal.strength
                defiant_command = {"action": defiant_action, "marshal": marshal_name}

                if defiant_action == "bombardment":
                    nearest = world.find_nearest_enemy(marshal.location)
                    if nearest and nearest[1] <= 2:
                        defiant_execution = self._execute_bombardment(
                            marshal, nearest[0], world, game_state
                        )
                    else:
                        defiant_action = "wait"
                        defiant_execution = self._execute_wait(marshal, world, game_state)
                elif defiant_action == "attack":
                    nearest = world.find_nearest_enemy(marshal.location)
                    if nearest:
                        defiant_execution = self._execute_attack(marshal, nearest[0].name, world, game_state)
                    else:
                        defiant_action = "wait"
                        defiant_execution = self._execute_wait(marshal, world, game_state)
                    if not defiant_execution.get("success"):
                        defiant_action = "wait"
                        defiant_execution = self._execute_wait(marshal, world, game_state)
                elif defiant_action == "fortify":
                    defiant_execution = self._execute_fortify(
                        {"marshal": marshal_name}, game_state
                    )
                    if not defiant_execution.get("success"):
                        defiant_action = "wait"
                        defiant_execution = self._execute_wait(marshal, world, game_state)
                else:
                    defiant_execution = self._execute_wait(marshal, world, game_state)

                # Evaluate outcome
                battle_result = defiant_execution.get("battle_result") or defiant_execution.get("bombardment_result")
                outcome = defiance_succeeded(marshal, defiant_action, battle_result, pre_battle_strength)

                # Apply outcome table
                outcome_result = apply_defiance_outcome(marshal, outcome, world)

                # Redemption check: insist penalty or defiance outcome may push trust <= 20
                _strat_redemption = world.disobedience_system.check_redemption_threshold(marshal, world)

                # M3 fix: register defensive vindication for deferred evaluation
                if defiant_action == "fortify" and defiant_execution.get("success"):
                    world.vindication_tracker.pending_defensive_vindication[marshal_name] = {
                        "turn": world.current_turn,
                        "source": "defiance",
                    }

                # Fire notification
                world.notifications.add(create_notification(
                    MARSHAL_DEFIED_ORDER,
                    NotificationPriority.HIGH,
                    f"{marshal_name} defied your strategic order!",
                    f"{marshal_name} defied your order to {_action_display_name(strategic_type)} "
                    f"and chose to {_action_display_name(defiant_action)} instead.",
                    world.current_turn,
                ))

                # Log campaign event
                world.log_event({
                    "type": "defiance",
                    "marshal": marshal_name,
                    "original_action": strategic_type,
                    "defiance_action": defiant_action,
                    "outcome": outcome_result["outcome_type"],
                    "turn": world.current_turn,
                })

                # Build response
                action_desc = _action_display_name(defiant_action)
                defiance_message = (
                    f"Despite your insistence, {marshal_name} {action_desc} instead of "
                    f"{_action_display_name(strategic_type)}!\n\n"
                    f"{outcome_result['berthier_text']}"
                )
                if defiant_execution.get("message"):
                    defiance_message += f"\n\n{defiant_execution['message']}"

                result = {
                    "success": True,
                    "message": defiance_message,
                    "objection_resolved": True,
                    "choice": choice,
                    "disobeyed": False,
                    "defiance": True,
                    "defiance_action": defiant_action,
                    "defiance_outcome": outcome_result["outcome_type"],
                    "trust_change": v2_insist_penalty + outcome_result["trust_change"],
                    "authority_change": outcome_result["authority_change"],
                    "berthier_text": outcome_result["berthier_text"],
                    "events": defiant_execution.get("events", []),
                    "action_info": defiant_execution.get("action_info", {"remaining": world.actions_remaining}),
                    "action_summary": world.get_action_summary(),
                    "new_state": game_state,
                }
                if defiant_execution.get("battle_report"):
                    result["battle_report"] = defiant_execution["battle_report"]
                if authority_event:
                    result["authority_event"] = authority_event
                if _strat_redemption:
                    result["redemption_event"] = _strat_redemption
                    result["state"] = "awaiting_redemption_choice"
                return result

            else:
                # ═══ STRATEGIC DEFIANCE ROLL FAILS — marshal obeys reluctantly ═══
                print(f"  [DEFIANCE] Strategic roll failed for {marshal_name} "
                      f"(roll={defiance_roll:.2f} >= chance={defiance_chance:.2f})")
                from backend.commands.defiance import apply_defiance_outcome
                outcome_result = apply_defiance_outcome(marshal, "failed_roll", world)
                _failed_roll_berthier = outcome_result["berthier_text"]

            # Trust penalty was already applied above — zero out to prevent
            # _handle_strategic_objection_response from applying it again.
            if _trust_penalty_applied:
                original_command["v2_insist_penalty"] = 0
        else:
            _failed_roll_berthier = None

        # Re-execute the strategic command with objection_response
        result = self._handle_strategic_objection_response(
            marshal=marshal,
            command=original_command,
            parsed_command=parsed_command,
            response=strategic_response,
            world=world,
            game_state=game_state,
            path=path,
            target=target,
            strategic_type=strategic_type
        )

        # If _handle_strategic_objection_response returns None, it means "proceed"
        # In that case, we need to continue with strategic order creation
        if result is None:
            # Rebuild parsed_command with objection_response
            parsed_command["command"] = original_command
            parsed_command["command"]["objection_response"] = strategic_response

            # Execute the strategic command (this will skip objection check)
            result = self._execute_strategic_command(parsed_command, original_command, game_state)

        # Append failed-roll Berthier text if defiance roll failed
        if _failed_roll_berthier and result and result.get("message"):
            result["message"] = result["message"] + "\n\n" + _failed_roll_berthier

        if not result:
            result = {
                "success": False,
                "message": "Failed to process strategic objection response"
            }

        # ════════════════════════════════════════════════════════════
        # AP CONSUMPTION for strategic objection response (non-defiance)
        # Defiance consumes AP in the defiance block above.
        # Trust → tactical preferred goes through execute() which already consumed AP.
        # All other paths (insist/proceed, trust → strategic, compromise) need AP here.
        # ════════════════════════════════════════════════════════════
        if (result.get("success") and not result.get("_ap_consumed_by_execute")
                and not result.get("pending_objection")):
            variable_cost = result.get("variable_action_cost", 2)
            if variable_cost > 0:
                for _ in range(min(variable_cost, world.actions_remaining)):
                    world.use_action(strategic_type or "strategic")
                result["action_info"] = {
                    "cost": variable_cost,
                    "remaining": world.actions_remaining,
                    "turn_advanced": False,
                    "new_turn": None,
                }

        # M2 fix: pass through authority threshold event if one crossed
        if authority_event and isinstance(result, dict):
            result["authority_event"] = authority_event

        # Redemption check: proceed penalty, failed_roll -3, or strategic response
        # trust change may have crossed threshold
        if result and isinstance(result, dict) and not result.get("redemption_event"):
            _final_redemption = world.disobedience_system.check_redemption_threshold(marshal, world)
            if _final_redemption:
                result["redemption_event"] = _final_redemption
                result["state"] = "awaiting_redemption_choice"

        return result

    # ============================================================
    # CAPTURE CHOICE SYSTEM (Phase 6.2.E)
    # ============================================================

    def handle_capture_choice(self, choice: str, game_state: Dict) -> Dict:
        """Handle player's plunder/secure choice after capturing a region.

        Args:
            choice: 'plunder' or 'secure'
            game_state: Current game state dict with 'world' key

        Returns:
            Result dict with effects applied
        """
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state available"}

        pending = world.pending_capture_choice
        if not pending:
            return {"success": False, "message": "No pending capture choice."}

        region_name = pending["region"]
        capturer_name = pending["capturer"]
        region = world.get_region(region_name)

        if not region:
            world.pending_capture_choice = None
            return {"success": False, "message": f"Region {region_name} not found."}

        if choice == "plunder":
            result = self._apply_plunder(region, world)
            world.pending_capture_choice = None
            # Log region_captured event
            world.log_event({
                "type": "region_captured",
                "region": region_name,
                "captured_by": world.player_nation,
                "captured_from": pending.get("previous_controller", ""),
                "method": "plunder",
            })
            return {
                "success": True,
                "message": (f"{capturer_name}'s troops plunder {region_name}! "
                            f"Gained {result['gold_gained']} gold. "
                            f"Buildings destroyed. Stability set to 10."),
                "events": [{
                    "type": "plunder",
                    "region": region_name,
                    "capturer": capturer_name,
                    "gold_gained": result["gold_gained"],
                }],
                "capture_choice": "plunder",
            }
        elif choice == "secure":
            self._apply_secure(region)
            world.pending_capture_choice = None
            damaged_count = len([b for b in region.buildings if b.get("damaged")])
            # Log region_captured event
            world.log_event({
                "type": "region_captured",
                "region": region_name,
                "captured_by": world.player_nation,
                "captured_from": pending.get("previous_controller", ""),
                "method": "secure",
            })
            return {
                "success": True,
                "message": (f"{capturer_name} secures {region_name}. "
                            f"Stability set to 25. Order is maintained."
                            + (f" {damaged_count} building(s) damaged." if damaged_count else "")),
                "events": [{
                    "type": "secure",
                    "region": region_name,
                    "capturer": capturer_name,
                }],
                "capture_choice": "secure",
            }
        else:
            return {
                "success": False,
                "message": f"Invalid choice: '{choice}'. Choose 'plunder' or 'secure'."
            }

    # Plunder Gold Multiplier (Phase 6.2 Audit Fix #4)
    # 1.75x creates genuine short-term vs long-term tradeoff:
    # Paris plundered: 300 * 1.75 = 525 gold immediately, but 0 income for ~9 turns
    # Paris secured: 0 gold immediately, but ~75/turn from turn 1 (stability 25 = 25%)
    # Breakeven: ~7 turns — plunder pays off in short campaigns, secure in long ones
    PLUNDER_GOLD_MULTIPLIER = 1.75

    def _apply_plunder(self, region, world, nation: str = None) -> Dict:
        """Apply plunder effects to a captured region.

        Args:
            nation: Nation receiving the gold. MUST be passed explicitly for AI nations.
                    Do NOT use world.gold (property targeting player_nation) for AI plunder.
                    Defaults to player_nation for backward compat only.
        """
        region.stability = 10
        region.apply_war_damage(0.35)
        region.plundered = True
        # Immediate gold = 175% of BASE income (not effective)
        gold_gained = int(region.income_value * self.PLUNDER_GOLD_MULTIPLIER)
        # IMPORTANT: Use nation_gold dict directly, NOT world.gold (which always targets player_nation)
        receiving_nation = nation or world.player_nation
        world.nation_gold[receiving_nation] = world.nation_gold.get(receiving_nation, 0) + gold_gained
        # Log building_damaged for each destroyed building
        for building in region.buildings:
            world.log_event({
                "type": "building_damaged",
                "region": region.name,
                "building": building["type"],
                "cause": "plunder",
            })
        # Destroy all buildings
        region.buildings = []
        region.building_under_construction = None
        # Destroy watchtower (Phase 6 Fog - Session 35)
        if getattr(region, 'watchtower', 'none') != "none":
            world.log_event({
                "type": "building_damaged",
                "region": region.name,
                "building": "watchtower",
                "cause": "plunder",
            })
            region.watchtower = "none"
            region.watchtower_turns_remaining = 0
        return {"gold_gained": int(gold_gained)}

    def _apply_secure(self, region) -> None:
        """Apply secure effects to a captured region."""
        region.stability = 25
        # No additional war damage
        region.plundered = False
        # No immediate gold
        # Damage existing buildings (not destroyed)
        for building in region.buildings:
            building["damaged"] = True
        # Cancel construction
        region.building_under_construction = None
        # Damage watchtower (Phase 6 Fog - Session 35)
        if getattr(region, 'watchtower', 'none') == "active":
            region.watchtower = "damaged"
        elif getattr(region, 'watchtower', 'none') == "under_construction":
            region.watchtower = "none"
            region.watchtower_turns_remaining = 0

    def _get_ai_capture_choice(self, marshal) -> str:
        """AI decides plunder vs secure based on personality."""
        from backend.models.personality import Personality
        personality = getattr(marshal, 'personality_type', None)
        if personality == Personality.AGGRESSIVE:
            return "plunder"
        return "secure"

    def _apply_ai_capture_choice(self, marshal, region, world, old_controller: str = "") -> str:
        """Apply AI's automatic capture choice (no popup). Returns the choice made."""
        choice = self._get_ai_capture_choice(marshal)
        if choice == "plunder":
            self._apply_plunder(region, world, nation=marshal.nation)
        else:
            self._apply_secure(region)
        # Log region_captured event for AI captures
        world.log_event({
            "type": "region_captured",
            "region": region.name,
            "captured_by": marshal.nation,
            "captured_from": old_controller,
            "method": choice,
        })
        return choice

    def _attempt_region_capture(self, marshal, region_name, world, game_state, had_garrison=False) -> dict:
        """Handle capture attempt, respecting fortification holdout.

        Args:
            marshal: Capturing marshal
            region_name: Region being captured
            world: WorldState
            game_state: Full game state dict
            had_garrison: True if defenders were beaten this turn (2-turn occupation)

        Returns:
            {"captured": bool, "occupation_started": bool, "message": str, ...}
        """
        region = world.get_region(region_name)
        if not region:
            return {"captured": False, "occupation_started": False, "message": ""}

        # Check for functional fortification (damaged forts don't block)
        has_fort = region.has_building("fortification")

        if has_fort:
            # CONTESTED CAPTURE: Start occupation timer
            turns_required = 2 if had_garrison else 1
            marshal.occupation_region = region_name
            marshal.occupation_turns_held = 0
            marshal.occupation_turns_required = turns_required

            return {
                "captured": False,
                "occupation_started": True,
                "turns_required": turns_required,
                "message": f"{region_name} is fortified! {marshal.name} must hold for "
                           f"{turns_required} turn(s) to capture.",
            }
        else:
            # INSTANT CAPTURE (existing behavior)
            old_controller = region.controller
            world.capture_region(region_name, marshal.nation)

            # Phase 6.2.E: Plunder/Secure choice
            ai_choice = None
            if marshal.nation == world.player_nation:
                world.pending_capture_choice = {
                    "region": region_name,
                    "capturer": marshal.name,
                    "previous_controller": old_controller,
                }
            else:
                # AI capture — auto-decide by personality
                ai_choice = self._apply_ai_capture_choice(marshal, region, world, old_controller=old_controller)

            return {
                "captured": True,
                "occupation_started": False,
                "old_controller": old_controller,
                "capture_choice": ai_choice,
                "message": "",
            }

    # ════════════════════════════════════════════════════════════
    # DIPLOMATIC COMMANDS (Phase 8 Session 3)
    # ════════════════════════════════════════════════════════════

    def _execute_diplomatic(self, command: Dict, game_state: Dict) -> Dict:
        """Route diplomatic commands to the appropriate handler."""
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "Error: No world state"}

        diplomatic_data = command.get("diplomatic_data", {})
        action = diplomatic_data.get("action", command.get("action", ""))

        # Error case: military command to Talleyrand
        if action == "diplomatic_error":
            return {
                "success": False,
                "message": diplomatic_data.get("message",
                    "Sire, I am a diplomat, not a general. Perhaps you meant to address one of your marshals?"),
            }

        # Check Talleyrand state — can't negotiate while in transit (EC-Q)
        talleyrand_state = getattr(world, 'talleyrand_state', 'IDLE')
        if talleyrand_state == "IN_TRANSIT" and action != "diplomatic_feasibility":
            return {
                "success": False,
                "message": "Talleyrand is currently en route to a foreign court. He cannot negotiate until he returns.",
            }

        # Unknown nation error (R93: include vassals)
        target_nation = diplomatic_data.get("target_nation")
        from backend.game_logic.diplomatic_dialogue import get_known_nations
        known = get_known_nations(world)
        if target_nation and target_nation not in known:
            nations_list = ", ".join(sorted(known))
            return {
                "success": False,
                "message": f"Sire, I am not aware of a nation called '{target_nation}'. "
                           f"Our diplomatic landscape includes {nations_list}.",
            }

        if action == "diplomatic_proposal":
            return self._execute_diplomatic_proposal(diplomatic_data, world)
        elif action == "diplomatic_mission":
            return self._execute_diplomatic_mission(diplomatic_data, world)
        elif action == "diplomatic_feasibility":
            return self._execute_diplomatic_feasibility(diplomatic_data, world)
        elif action == "diplomatic_advisory":
            return self._execute_diplomatic_advisory(diplomatic_data, world)
        elif action == "diplomatic_break":
            return self._execute_diplomatic_break(diplomatic_data, world)
        elif action == "diplomatic_downgrade":
            return self._execute_diplomatic_downgrade(diplomatic_data, world)
        elif action == "diplomatic_declare_war":
            return self._execute_diplomatic_declare_war(diplomatic_data, world)
        elif action == "diplomatic_ultimatum":
            return self._execute_diplomatic_ultimatum(diplomatic_data, world)
        else:
            return {"success": False, "message": f"Unknown diplomatic action: {action}"}

    def _execute_diplomatic_proposal(self, diplomatic_data: Dict, world) -> Dict:
        """Handle a diplomatic proposal command. Generates dialogue for player choice."""
        from backend.game_logic.diplomatic_dialogue import (
            classify_diplomatic_intent, generate_dialogue,
        )
        from backend.game_logic.diplomacy import get_dp_cost, get_transition_dp_cost

        target_nation = diplomatic_data.get("target_nation")

        if not target_nation:
            # No target — ask which nation
            world.pending_diplomatic_dialogue = {
                "type": "proposal_options",
                "target_nation": "",
                "talleyrand_text": "Sire, which nation shall I approach? Our diplomatic landscape includes Britain, Prussia, Austria, and Saxony.",
                "options": [
                    {"label": "Britain", "description": "Currently at war.", "action": "expand_options",
                     "terms": {"target_nation": "Britain"}},
                    {"label": "Prussia", "description": "Currently at war.", "action": "expand_options",
                     "terms": {"target_nation": "Prussia"}},
                    {"label": "Austria", "description": "At peace.", "action": "expand_options",
                     "terms": {"target_nation": "Austria"}},
                    {"label": "Saxony", "description": "Open borders.", "action": "expand_options",
                     "terms": {"target_nation": "Saxony"}},
                ],
                "context": {},
                "turn_created": int(world.current_turn),
                "blocking": False,
            }
            return {
                "success": True,
                "message": world.pending_diplomatic_dialogue["talleyrand_text"],
                "diplomatic_dialogue": world.pending_diplomatic_dialogue,
            }

        # §4a: Proposal for current or lower state pre-check
        from backend.game_logic.diplomacy import _UPGRADE_ORDER
        current_diplo_state = world.get_diplomatic_state("France", target_nation) if target_nation else "PEACE"
        _state_map_4a = {"peace": "PEACE", "alliance": "ALLIANCE", "defensive_alliance": "DEFENSIVE_ALLIANCE",
                         "non_aggression": "NON_AGGRESSION", "open_borders": "OPEN_BORDERS", "armistice": "ARMISTICE"}
        proposal_type_raw = diplomatic_data.get("proposal_type")
        if proposal_type_raw:
            target_diplo_state = _state_map_4a.get(proposal_type_raw, "")
            if target_diplo_state in _UPGRADE_ORDER and current_diplo_state in _UPGRADE_ORDER:
                if _UPGRADE_ORDER.index(target_diplo_state) <= _UPGRADE_ORDER.index(current_diplo_state):
                    from backend.game_logic.diplomacy import _STATE_DISPLAY_NAMES
                    display = _STATE_DISPLAY_NAMES.get(current_diplo_state, current_diplo_state)
                    return {
                        "success": False,
                        "message": f"We already have {display} with {target_nation}. "
                                   f"Talleyrand sees no purpose in proposing what we already possess.",
                    }

        # Check proposal cooldown
        cooldowns = getattr(world, 'player_proposal_cooldowns', {})
        if target_nation in cooldowns and cooldowns[target_nation] > 0:
            remaining = cooldowns[target_nation]
            return {
                "success": False,
                "message": f"Talleyrand advises patience, Sire. {target_nation} rejected our last proposal only {remaining} turns ago.",
            }
        proposal_type = diplomatic_data.get("proposal_type")
        if proposal_type:
            type_key = f"{target_nation}_{proposal_type}"
            if type_key in cooldowns and cooldowns[type_key] > 0:
                remaining = cooldowns[type_key]
                return {
                    "success": False,
                    "message": f"Talleyrand advises patience, Sire. {target_nation} rejected our {_proposal_display_name(proposal_type)} proposal only {remaining} turns ago.",
                }

        # Check DP (with jump cost for multi-step transitions)
        dp_action = f"propose_{proposal_type}" if proposal_type else "propose_peace"
        talleyrand = world.diplomats.get("France")
        skill = talleyrand.skill if talleyrand else 5
        # R98: Compute cumulative DP for jump transitions
        _state_map = {"peace": "PEACE", "alliance": "ALLIANCE", "defensive_alliance": "DEFENSIVE_ALLIANCE",
                      "non_aggression": "NON_AGGRESSION", "open_borders": "OPEN_BORDERS", "armistice": "ARMISTICE"}
        current_diplo = world.get_diplomatic_state("France", target_nation) if target_nation else "PEACE"
        target_diplo = _state_map.get(proposal_type, "PEACE") if proposal_type else "PEACE"
        jump_cost = get_transition_dp_cost(current_diplo, target_diplo)
        cost = get_dp_cost(dp_action, skill, transition_base=jump_cost)
        if world.diplomatic_points < cost:
            # Notification: DP insufficient (Session 8C)
            from backend.notifications import (
                create_notification, NotificationPriority, DP_INSUFFICIENT,
            )
            world.notifications.add(create_notification(
                DP_INSUFFICIENT,
                NotificationPriority.NORMAL,
                "Insufficient DP",
                f"Insufficient diplomatic points. {int(cost)} DP required, {int(world.diplomatic_points)} available.",
                int(world.current_turn),
            ))
            return {
                "success": False,
                "message": f"Insufficient Diplomatic Points. This proposal costs {int(cost)} DP, but we only have {int(world.diplomatic_points)}.",
                "diplomatic_dialogue": None,
                "awaiting_diplomatic_response": False,
            }

        # Classify intent and generate dialogue
        intent = classify_diplomatic_intent(diplomatic_data, world)
        dialogue = generate_dialogue(intent, diplomatic_data, world)

        # Set pending dialogue
        world.pending_diplomatic_dialogue = dialogue

        return {
            "success": True,
            "message": dialogue.get("talleyrand_text", ""),
            "diplomatic_dialogue": dialogue,
        }

    def _execute_diplomatic_mission(self, diplomatic_data: Dict, world) -> Dict:
        """Handle a diplomatic mission command."""
        from backend.game_logic.diplomatic_dialogue import (
            generate_mission_dialogue, MISSION_DP_COSTS,
        )

        target_nation = diplomatic_data.get("target_nation")
        mission_type = diplomatic_data.get("mission_type")

        if not target_nation or not mission_type:
            dialogue = generate_mission_dialogue(diplomatic_data, world)
            world.pending_diplomatic_dialogue = dialogue
            return {
                "success": True,
                "message": dialogue.get("talleyrand_text", ""),
                "diplomatic_dialogue": dialogue,
            }

        # Cancel mission
        if mission_type == "CANCEL":
            existing = getattr(world, 'active_diplomatic_mission', None)
            if not existing:
                return {"success": False, "message": "There is no active diplomatic mission to cancel."}
            world.active_diplomatic_mission = None
            world.talleyrand_state = "IDLE"
            return {
                "success": True,
                "message": f"Talleyrand's mission to {existing.get('target', 'unknown')} has been cancelled.",
            }

        # Check DP
        cost = MISSION_DP_COSTS.get(mission_type, 1)
        if world.diplomatic_points < cost:
            # Notification: DP insufficient (Session 8C)
            from backend.notifications import (
                create_notification as _cn, NotificationPriority as _NP, DP_INSUFFICIENT as _DPI,
            )
            world.notifications.add(_cn(
                _DPI, _NP.NORMAL, "Insufficient DP",
                f"Insufficient diplomatic points. {int(cost)} DP required, {int(world.diplomatic_points)} available.",
                int(world.current_turn),
            ))
            return {
                "success": False,
                "message": f"Insufficient DP for this mission. Costs {int(cost)} DP per turn.",
                "diplomatic_dialogue": None,
                "awaiting_diplomatic_response": False,
            }

        # Generate mission confirmation dialogue
        dialogue = generate_mission_dialogue(diplomatic_data, world)
        world.pending_diplomatic_dialogue = dialogue
        return {
            "success": True,
            "message": dialogue.get("talleyrand_text", ""),
            "diplomatic_dialogue": dialogue,
        }

    def _execute_diplomatic_feasibility(self, diplomatic_data: Dict, world) -> Dict:
        """Handle a feasibility check (0 DP cost).

        R31: Enhanced with numerical component breakdown from calculate_acceptance().
        """
        from backend.game_logic.diplomatic_dialogue import generate_feasibility_dialogue
        from backend.game_logic.diplomacy import calculate_acceptance

        dialogue = generate_feasibility_dialogue(diplomatic_data, world)
        world.pending_diplomatic_dialogue = dialogue

        # R31: Run acceptance formula to get component breakdown
        target_nation = diplomatic_data.get("target_nation", "")
        proposal_type = diplomatic_data.get("proposal_type", "peace")
        acceptance_breakdown = None
        if target_nation:
            hypothetical = {
                "type": proposal_type,
                "proposer_nation": "France",
                "target_nation": target_nation,
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            }
            acceptance_result = calculate_acceptance(hypothetical, world)
            acceptance_breakdown = {
                "score": int(acceptance_result.get("score", 0)),
                "outcome": acceptance_result.get("outcome", "REJECT"),
                "components": acceptance_result.get("components", {}),
            }

        # Dispatch event (Session 8D)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_feasibility_report",
                            {"difficulty_tier": dialogue.get("context", {}).get("difficulty_tier", "unknown"),
                             "hint": "", "nation": target_nation}, "always")

        result = {
            "success": True,
            "message": dialogue.get("talleyrand_text", ""),
            "diplomatic_dialogue": dialogue,
        }
        if acceptance_breakdown:
            result["acceptance_breakdown"] = acceptance_breakdown
        return result

    def _execute_diplomatic_advisory(self, diplomatic_data: Dict, world) -> Dict:
        """Handle advisory questions via diplomatic_advisory.py."""
        from backend.game_logic.diplomatic_advisory import (
            detect_advisory_type, generate_advisory,
        )

        target_nation = diplomatic_data.get("target_nation", "")
        raw_text = diplomatic_data.get("raw_text", "")

        # Detect advisory subtype from player's question text
        advisory_type = detect_advisory_type(raw_text) if raw_text else None
        if not advisory_type:
            # Default based on whether a nation was mentioned
            advisory_type = "assess_nation" if target_nation else "compare_threats"

        dialogue = generate_advisory(target_nation or None, advisory_type, world)
        world.pending_diplomatic_dialogue = dialogue
        return {
            "success": True,
            "message": dialogue.get("talleyrand_text", ""),
            "diplomatic_dialogue": dialogue,
        }

    def _execute_diplomatic_break(self, diplomatic_data: Dict, world) -> Dict:
        """Handle break treaty command. Costs 1 DP."""
        from backend.game_logic.diplomacy import break_treaty

        target_nation = diplomatic_data.get("target_nation")
        if not target_nation:
            return {
                "success": False,
                "message": "Sire, which nation's treaty shall I break? Specify: Britain, Prussia, Austria, or Saxony.",
            }

        player = world.player_nation
        pair_key = world._make_diplo_key(player, target_nation)

        # §4c: Pre-validate treaty exists with Talleyrand-voiced message
        active_treaties = getattr(world, 'active_treaties', {})
        if pair_key not in active_treaties:
            return {
                "success": False,
                "message": f"There is no treaty with {target_nation} to break, Your Excellency.",
            }

        result = break_treaty(pair_key, player, world)

        # R23: Marshal trust reactions for treaty broken
        if result.get("success"):
            self._apply_diplomatic_trust_reactions(world, "treaty_broken", target_nation)

        return result

    def _execute_diplomatic_downgrade(self, diplomatic_data: Dict, world) -> Dict:
        """Handle voluntary downgrade command. Costs 1 DP per downgrade step."""
        from backend.game_logic.diplomacy import execute_downgrade

        target_nation = diplomatic_data.get("target_nation")
        if not target_nation:
            return {
                "success": False,
                "message": "Sire, which nation's relations shall I downgrade? Specify: Britain, Prussia, Austria, or Saxony.",
            }

        player = world.player_nation

        # §4d: Pre-validate not already at minimum downgradable state
        from backend.game_logic.diplomacy import _DOWNGRADE_ORDER
        current_state = world.get_diplomatic_state(player, target_nation)
        if current_state not in _DOWNGRADE_ORDER:
            return {
                "success": False,
                "message": f"Our relations with {target_nation} are already at their most basic level.",
            }
        idx = _DOWNGRADE_ORDER.index(current_state)
        if idx >= len(_DOWNGRADE_ORDER) - 1:
            return {
                "success": False,
                "message": f"Our relations with {target_nation} are already at their most basic level.",
            }

        # Check DP before calling (execute_downgrade doesn't check DP itself)
        dp_cost = 1
        if world.diplomatic_points < dp_cost:
            return {
                "success": False,
                "message": f"Insufficient Diplomatic Points. Downgrade costs {dp_cost} DP, but we only have {int(world.diplomatic_points)}.",
                "diplomatic_dialogue": None,
                "awaiting_diplomatic_response": False,
            }

        result = execute_downgrade(world, player, target_nation)
        if result.get("success"):
            # Deduct DP (execute_downgrade returns dp_cost but doesn't deduct)
            world.diplomatic_points -= dp_cost
        return result

    def _execute_diplomatic_declare_war(self, diplomatic_data: Dict, world) -> Dict:
        """Handle war declaration command (R10). Costs 1 DP."""
        from backend.game_logic.diplomacy import declare_war

        target_nation = diplomatic_data.get("target_nation")
        if not target_nation:
            return {
                "success": False,
                "message": "Sire, against which nation shall we declare war? Specify: Britain, Prussia, Austria, or Saxony.",
            }

        player = world.player_nation

        # Already at war?
        current_state = world.get_diplomatic_state(player, target_nation)
        if current_state == "WAR":
            return {
                "success": False,
                "message": f"We are already at war with {target_nation}, Sire.",
            }

        # §4e: Armistice cooldown — include remaining turns in message
        diplo_key_war = world._make_diplo_key(player, target_nation)
        arm_cd = getattr(world, 'armistice_cooldowns', {}).get(diplo_key_war, 0)
        if arm_cd > 0:
            return {
                "success": False,
                "message": f"The armistice with {target_nation} holds for {arm_cd} more turns. "
                           f"We cannot declare war until it expires.",
            }

        # Treaty warning — declaring war on an ally requires confirmation
        diplo_key_treaty = world._make_diplo_key(player, target_nation)
        existing_treaty = world.active_treaties.get(diplo_key_treaty)
        if existing_treaty and not world.diplomatic_objection_popup:
            treaty_type = existing_treaty.get("type", "treaty")
            treaty_display = treaty_type.replace("_", " ").title()
            world.pending_diplomatic_dialogue = {
                "type": "force_declare_war_confirmation",
                "target_nation": target_nation,
                "message": (f"Sire! We have a {treaty_display} with {target_nation}. "
                            f"Declaring war would break this treaty and mark us as oath-breakers "
                            f"in the eyes of all Europe. Shall I proceed regardless?"),
                "options": [
                    {"label": "Proceed — break the treaty", "action": "force_declare_war",
                     "target_nation": target_nation},
                    {"label": "Reconsider", "action": "reconsider"},
                ],
                "turn_created": int(world.current_turn),
                "blocking": True,
            }
            return {
                "success": True,
                "message": world.pending_diplomatic_dialogue["message"],
                "diplomatic_dialogue": world.pending_diplomatic_dialogue,
                "awaiting_diplomatic_response": True,
            }

        # DP check (1 DP)
        dp_cost = 1
        if world.diplomatic_points < dp_cost:
            return {
                "success": False,
                "message": f"Insufficient Diplomatic Points. War declaration costs {dp_cost} DP, but we have {int(world.diplomatic_points)}.",
                "diplomatic_dialogue": None,
                "awaiting_diplomatic_response": False,
            }

        # Talleyrand STRONG objection if target is neutral and threat is high
        threat_level = getattr(world, 'threat_level', 0)
        if current_state != "WAR" and threat_level > 50:
            # Check if objection already pending (don't double-fire)
            if not world.diplomatic_objection_popup:
                world.diplomatic_objection_popup = {
                    "type": "talleyrand_objection",
                    "severity": "STRONG",
                    "message": (f"Sire, I must strongly advise against declaring war on {target_nation}. "
                                f"Our threat level stands at {int(threat_level)} — the courts of Europe "
                                f"already whisper of coalition. Another war will only hasten their union against us."),
                    "action": "diplomatic_declare_war",
                    "target_nation": target_nation,
                }
                return {
                    "success": True,
                    "message": world.diplomatic_objection_popup["message"],
                    "diplomatic_objection_popup": world.diplomatic_objection_popup,
                }

        # Execute war declaration
        result = declare_war(world, player, target_nation,
                             casus_belli=world.casus_belli.get(world._make_diplo_key(player, target_nation), False))

        if result.get("success"):
            world.diplomatic_points -= dp_cost
            # R23: Marshal trust reactions for war declaration
            self._apply_diplomatic_trust_reactions(world, "war_declaration", target_nation)

        return result

    def _execute_diplomatic_ultimatum(self, diplomatic_data: Dict, world) -> Dict:
        """Handle ultimatum command (R21). Costs 2 DP."""
        from backend.game_logic.diplomacy import calculate_acceptance

        target_nation = diplomatic_data.get("target_nation")
        if not target_nation:
            return {
                "success": False,
                "message": "Sire, to which nation shall we deliver this ultimatum? Specify: Britain, Prussia, Austria, or Saxony.",
            }

        player = world.player_nation
        current_state = world.get_diplomatic_state(player, target_nation)

        if current_state == "WAR":
            return {
                "success": False,
                "message": f"We are already at war with {target_nation}, Sire. An ultimatum is meaningless.",
            }

        # §4b: Ultimatum cooldown check (5-turn per target)
        ultimatum_cooldowns = getattr(world, 'ultimatum_cooldowns', {})
        ult_cd = ultimatum_cooldowns.get(target_nation, 0)
        if ult_cd > 0:
            return {
                "success": False,
                "message": f"Talleyrand advises patience, Sire. Our last ultimatum to {target_nation} "
                           f"was too recent — we must wait {ult_cd} more turns.",
            }

        # DP check (2 DP)
        dp_cost = 2
        if world.diplomatic_points < dp_cost:
            return {
                "success": False,
                "message": f"Insufficient Diplomatic Points. Ultimatum costs {dp_cost} DP, but we have {int(world.diplomatic_points)}.",
                "diplomatic_dialogue": None,
                "awaiting_diplomatic_response": False,
            }

        # Talleyrand STRONG objection if threat is high
        threat_level = getattr(world, 'threat_level', 0)
        if threat_level > 50 and not world.diplomatic_objection_popup:
            world.diplomatic_objection_popup = {
                "type": "talleyrand_objection",
                "severity": "STRONG",
                "message": (f"Sire, an ultimatum to {target_nation} while our threat level stands at "
                            f"{int(threat_level)} is most unwise. The other powers will see this as "
                            f"further aggression."),
                "action": "diplomatic_ultimatum",
                "target_nation": target_nation,
            }
            return {
                "success": True,
                "message": world.diplomatic_objection_popup["message"],
                "diplomatic_objection_popup": world.diplomatic_objection_popup,
            }

        # Calculate military threat bonus: +15 if French marshal adjacent to target's marshal, else +10
        military_threat = 10
        for m_name, m_obj in world.marshals.items():
            if m_obj.nation == player and m_obj.strength > 0:
                m_region = world.regions.get(m_obj.location)
                if not m_region:
                    continue
                for e_name, e_obj in world.marshals.items():
                    if e_obj.nation == target_nation and e_obj.location in getattr(m_region, 'connections', []):
                        military_threat = 15
                        break
                if military_threat == 15:
                    break

        # -10 relation regardless of outcome
        world.modify_nation_relation(player, target_nation, -10)

        # Deduct DP
        world.diplomatic_points -= dp_cost

        # Determine acceptance (ultimatums get military_threat bonus)
        acceptance_base = 0
        try:
            proposal = {
                "type": "peace",
                "proposer_nation": player,
                "target_nation": target_nation,
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            }
            acceptance_result = calculate_acceptance(proposal, world)
            acceptance_base = acceptance_result.get("score", 0) if isinstance(acceptance_result, dict) else 20
        except Exception:
            acceptance_base = 20

        # Add military threat bonus
        total_acceptance = acceptance_base + military_threat

        import random
        roll = random.randint(1, 100)
        accepted = roll <= total_acceptance

        diplo_key = world._make_diplo_key(player, target_nation)

        if accepted:
            # Ultimatum accepted — transition to peace or non-aggression
            # Deep audit fix 4: Use cleanup_war_end for proper war data cleanup
            current = world.get_diplomatic_state(player, target_nation)
            if current == "WAR":
                world.diplomatic_states[diplo_key] = "PEACE"
                from backend.game_logic.diplomacy import cleanup_war_end
                cleanup_war_end(world, diplo_key)
                outcome_msg = f"{target_nation} has accepted our ultimatum and sued for peace!"
            else:
                world.diplomatic_states[diplo_key] = "NON_AGGRESSION"
                outcome_msg = f"{target_nation} has bowed to our ultimatum and agreed to non-aggression!"
            # Deep audit fix 4: Clear active treaty
            active_treaties = getattr(world, 'active_treaties', {})
            active_treaties.pop(diplo_key, None)
        else:
            # Ultimatum rejected — casus belli granted
            world.casus_belli[diplo_key] = True
            outcome_msg = (f"{target_nation} has rejected our ultimatum! "
                           f"We now have casus belli — war declaration penalties will be halved.")

        # §4b: Set ultimatum cooldown (5 turns per target)
        ultimatum_cooldowns = getattr(world, 'ultimatum_cooldowns', {})
        ultimatum_cooldowns[target_nation] = 5
        world.ultimatum_cooldowns = ultimatum_cooldowns

        # R23: Marshal trust reactions
        self._apply_diplomatic_trust_reactions(world, "ultimatum_issued", target_nation)

        # Log diplomatic history
        diplomatic_history = getattr(world, 'diplomatic_history', [])
        diplomatic_history.append({
            "turn": int(world.current_turn),
            "type": "ultimatum",
            "target": target_nation,
            "accepted": accepted,
            "military_threat": military_threat,
        })
        # Cap at 20 entries
        if len(diplomatic_history) > 20:
            diplomatic_history[:] = diplomatic_history[-20:]
        world.diplomatic_history = diplomatic_history

        return {
            "success": True,
            "message": outcome_msg,
            "accepted": accepted,
            "military_threat": military_threat,
            "dp_cost": dp_cost,
        }

    def _apply_diplomatic_trust_reactions(self, world, event_type: str, target_nation: str = None):
        """Apply marshal trust reactions for diplomatic events (R23).

        Event types: war_declaration, treaty_signed, treaty_broken,
                     ultimatum_issued, vassal_created, alliance_formed
        """
        # Trust reaction table: event_type -> personality_string -> trust_delta
        _DIPLOMATIC_TRUST_REACTIONS = {
            "war_declaration": {
                "aggressive": 3, "cautious": -3, "literal": 0, "balanced": 0,
            },
            "treaty_signed": {
                "aggressive": -2, "cautious": 3, "literal": 1, "balanced": 1,
            },
            "treaty_broken": {
                "aggressive": 1, "cautious": -3, "literal": -2, "balanced": -1,
            },
            "ultimatum_issued": {
                "aggressive": 2, "cautious": -2, "literal": 0, "balanced": 0,
            },
            "vassal_created": {
                "aggressive": 2, "cautious": -1, "literal": 1, "balanced": 1,
            },
            "alliance_formed": {
                "aggressive": -1, "cautious": 2, "literal": 1, "balanced": 1,
            },
        }

        reactions = _DIPLOMATIC_TRUST_REACTIONS.get(event_type, {})
        if not reactions:
            return

        # Track per-turn cap (+/-5 per turn from diplomatic events)
        diplo_trust_key = f"_diplomatic_trust_this_turn_{world.current_turn}"

        for m_name, m_obj in world.marshals.items():
            if m_obj.nation != world.player_nation:
                continue

            personality = getattr(m_obj, 'personality', None)
            if not personality:
                continue

            delta = reactions.get(personality, 0)
            if delta == 0:
                continue

            # Per-turn cap tracking
            applied = getattr(m_obj, diplo_trust_key, 0)
            remaining = 5 - abs(applied)
            if remaining <= 0:
                continue
            clamped_delta = max(-remaining, min(remaining, delta))

            m_obj.trust.modify(clamped_delta)
            setattr(m_obj, diplo_trust_key, applied + clamped_delta)

    def handle_diplomatic_dialogue_response(self, choice, game_state: Dict) -> Dict:
        """Handle player's response to a diplomatic dialogue.

        Args:
            choice: int (1-based option index) or str (keyword match)
            game_state: Current game state

        Returns:
            Result dict with success, message, and any new state.
        """
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "Error: No world state"}

        if world.pending_diplomatic_dialogue is None:
            return {"success": False, "message": "No diplomatic matter awaits your attention, Sire."}

        dialogue = world.pending_diplomatic_dialogue
        options = dialogue.get("options", [])

        # Resolve choice to option
        selected = None
        if isinstance(choice, int):
            if choice < 1 or choice > len(options):
                return {"success": False, "message": f"Please choose an option (1-{len(options)}), Sire."}
            selected = options[choice - 1]
        elif isinstance(choice, str):
            # Try parsing as int
            try:
                idx = int(choice)
                if 1 <= idx <= len(options):
                    selected = options[idx - 1]
            except (ValueError, TypeError):
                pass
            # Keyword matching
            if not selected:
                choice_lower = choice.lower()
                for opt in options:
                    label_lower = opt.get("label", "").lower()
                    if choice_lower in label_lower or label_lower in choice_lower:
                        selected = opt
                        break
                # Try matching action keywords
                if not selected:
                    # Map keywords to action(s). List means try in order
                    # (e.g. "accept" tries AI proposal accept first, then player proposal send).
                    action_map = {
                        "dismiss": ["dismiss"], "cancel": ["cancel_mission", "dismiss"], "never mind": ["dismiss"],
                        "send": ["send_override", "send", "execute_proposal"],
                        "proceed": ["send_override", "execute_proposal", "force_declare_war"],
                        "yes": ["execute_proposal", "accept_ai_proposal", "force_declare_war"],
                        "reconsider": ["reconsider"], "no": ["reconsider"], "wait": ["reconsider"],
                        "harsh": ["modify_harsh"], "generous": ["modify_generous"],
                        "adjust": ["adjust_terms", "expand_options"],
                        "territory": ["territory_yes", "offer_region"],
                        "enough": ["enough_territory"],
                        "offer": ["offer_region", "offer_gold", "offer_ap"],
                        "skip": ["skip_region", "skip_gold", "skip_ap"],
                        "begin": ["start_mission"], "start": ["start_mission"],
                        "accept": ["accept_with_conflict", "accept_ai_proposal", "execute_proposal"],
                        "agree": ["accept_with_conflict", "accept_ai_proposal", "execute_proposal"],
                        "reject": ["reject_ai_proposal"], "decline": ["reject_ai_proposal"],
                        "counter": ["counter_ai_proposal"],
                        "thank": ["dismiss"],
                        "trust": ["send_suggested"],
                        "elaborate": ["elaborate", "expand_to_proposal"],
                        "more": ["elaborate", "expand_to_proposal"],
                        "review": ["review_counter"],
                        "consider": ["review_counter"],
                    }
                    for keyword, action_matches in action_map.items():
                        if keyword in choice_lower:
                            for action_match in action_matches:
                                for opt in options:
                                    if opt.get("action") == action_match:
                                        selected = opt
                                        break
                                if selected:
                                    break
                            if selected:
                                break
        else:
            return {"success": False, "message": f"Please choose an option (1-{len(options)}), Sire."}

        if not selected:
            return {"success": False, "message": f"Please choose an option (1-{len(options)}), Sire."}

        # Process the selected action
        action = selected.get("action", "dismiss")
        return self._process_dialogue_choice(action, selected, dialogue, world)

    def _process_dialogue_choice(self, action: str, selected: Dict,
                                  dialogue: Dict, world) -> Dict:
        """Process a player's dialogue choice."""
        from backend.game_logic.diplomacy import get_dp_cost, get_transition_dp_cost
        from backend.game_logic.diplomatic_dialogue import (
            MISSION_DP_COSTS, MISSION_DESCRIPTIONS, generate_dialogue,
        )
        from backend.game_logic.diplomatic_templates import generate_suggested_terms

        target_nation = dialogue.get("target_nation", "")

        if action == "dismiss":
            world.pending_diplomatic_dialogue = None
            return {"success": True, "message": "Very well, Sire."}

        elif action == "reconsider":
            world.pending_diplomatic_dialogue = None
            return {"success": True, "message": "Of course, Sire. Take your time."}

        elif action == "force_declare_war":
            # Player confirmed war declaration despite existing treaty
            from backend.game_logic.diplomacy import declare_war
            world.pending_diplomatic_dialogue = None
            fw_target = selected.get("target_nation") or target_nation
            if not fw_target:
                return {"success": False, "message": "No target nation specified."}
            # DP check (1 DP)
            dp_cost = 1
            if world.diplomatic_points < dp_cost:
                return {
                    "success": False,
                    "message": f"Insufficient Diplomatic Points. War declaration costs {dp_cost} DP, but we have {int(world.diplomatic_points)}.",
                }
            result = declare_war(world, world.player_nation, fw_target,
                                 casus_belli=world.casus_belli.get(
                                     world._make_diplo_key(world.player_nation, fw_target), False))
            if result.get("success"):
                world.diplomatic_points -= dp_cost
                self._apply_diplomatic_trust_reactions(world, "war_declaration", fw_target)
            return result

        elif action in ("execute_proposal", "send"):
            terms = selected.get("terms", {})
            proposal_type = terms.get("proposal_type", "peace")

            # Build proposal for acceptance formula
            proposal = {
                "type": proposal_type,
                "proposer_nation": "France",
                "target_nation": target_nation,
                "sweeteners": terms.get("sweeteners", []),
                "demands": terms.get("demands", []),
                "clauses": terms.get("clauses", []),
            }

            # Deduct DP (with jump cost for multi-step transitions)
            talleyrand = world.diplomats.get("France")
            skill = talleyrand.skill if talleyrand else 5
            dp_action = f"propose_{proposal_type}"
            # R98: Compute cumulative DP for jump transitions
            _state_map = {"peace": "PEACE", "alliance": "ALLIANCE", "defensive_alliance": "DEFENSIVE_ALLIANCE",
                          "non_aggression": "NON_AGGRESSION", "open_borders": "OPEN_BORDERS", "armistice": "ARMISTICE"}
            current_diplo = world.get_diplomatic_state("France", target_nation) if target_nation else "PEACE"
            target_diplo = _state_map.get(proposal_type, "PEACE")
            jump_cost = get_transition_dp_cost(current_diplo, target_diplo)
            cost = get_dp_cost(dp_action, skill, transition_base=jump_cost)
            if world.diplomatic_points < cost:
                world.pending_diplomatic_dialogue = None
                return {
                    "success": False,
                    "message": f"Insufficient Diplomatic Points. Need {int(cost)}, have {int(world.diplomatic_points)}.",
                    "diplomatic_dialogue": None,
                    "awaiting_diplomatic_response": False,
                }
            world.diplomatic_points -= cost

            # Set Talleyrand in transit
            # Pause mission if active
            mission = getattr(world, 'active_diplomatic_mission', None)
            if mission and not mission.get("paused"):
                mission["paused"] = True

            world.talleyrand_state = "IN_TRANSIT"
            world.proposal_in_transit = {
                "target": target_nation,
                "proposal": proposal,
                "turn_sent": int(world.current_turn),
            }

            # Log event
            world.log_event({
                "type": "diplomatic_proposal_sent",
                "target": target_nation,
                "proposal_type": proposal_type,
            })

            # R29: Log to diplomatic history
            diplomatic_history = getattr(world, 'diplomatic_history', [])
            diplomatic_history.append({
                "turn": int(world.current_turn),
                "type": "proposal_sent",
                "target": target_nation,
                "proposal_type": proposal_type,
            })
            if len(diplomatic_history) > 20:
                diplomatic_history[:] = diplomatic_history[-20:]
            world.diplomatic_history = diplomatic_history

            # Dispatch event (Session 8D)
            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_proposal_sent",
                                {"nation": target_nation}, "always")

            world.pending_diplomatic_dialogue = None
            return {
                "success": True,
                "message": (
                    f"Talleyrand departs for the {target_nation} court with your {_proposal_display_name(proposal_type)} proposal. "
                    f"Expect a response by next turn. ({int(cost)} DP spent)"
                ),
            }

        elif action == "modify_harsh":
            # Build on PREVIOUS terms (not fresh) so each iteration escalates.
            terms = selected.get("terms", {})
            proposal_type = terms.get("proposal_type", dialogue.get("_proposal_type", "peace"))
            if not proposal_type:
                proposal_type = "peace"

            import copy
            suggested = copy.deepcopy(terms) if terms.get("sweeteners") is not None or terms.get("demands") is not None else generate_suggested_terms(target_nation, proposal_type, world)
            # Ensure proposal metadata
            suggested["proposer_nation"] = suggested.get("proposer_nation", "France")
            suggested["target_nation"] = suggested.get("target_nation", target_nation)
            suggested["type"] = suggested.get("type", proposal_type)

            # Escalate existing demands by 1.5x
            for d in suggested.get("demands", []):
                if d.get("type") not in ("territory_cede",):
                    d["value"] = int(d.get("value", 0) * 1.5)

            # Add a gold demand if none exist
            if not suggested.get("demands"):
                suggested["demands"] = [{"type": "gold_per_turn", "value": 100}]

            # Round 2 escalation: add territory demand if not already present
            context_pre = dict(dialogue.get("context", {}))
            round_num = context_pre.get("modify_count", 0) + 1
            if round_num >= 2:
                has_territory = any(d.get("type") in ("territory_cede", "territory") for d in suggested.get("demands", []))
                if not has_territory:
                    suggested["demands"].append({"type": "territory_cede", "value": 1})

            # Remove sweeteners (harsh = no sweeteners)
            suggested["sweeteners"] = []

            # Bug 5 fix: Use nation-specific smart commentary
            from backend.game_logic.diplomatic_templates import _get_smart_commentary
            suggested["talleyrand_commentary"] = _get_smart_commentary(target_nation, "modified_harsh")

            # BUGFIX (Bug 4C): §9b iteration cap — max 2 modifications.
            # modify_count is carried in dialogue context across round-trips.
            # See BUGFIX_PLAN_PROPOSAL_FLOW.md.
            context = dict(dialogue.get("context", {}))
            modify_count = context.get("modify_count", 0) + 1
            context["modify_count"] = modify_count

            options = [
                {
                    "label": "Send these terms",
                    "description": "Dispatch with these demands.",
                    "action": "execute_proposal",
                    "terms": {**suggested, "proposal_type": proposal_type},
                },
            ]
            if modify_count < 2:
                options.append({
                    "label": "Even harsher",
                    "description": "Push harder.",
                    "action": "modify_harsh",
                    "terms": {**suggested, "proposal_type": proposal_type},
                })
            options.append({"label": "Reconsider", "description": "Let me think.", "action": "reconsider"})

            cap_msg = ""
            if modify_count >= 2:
                cap_msg = " These are the harshest terms possible."

            new_dialogue = {
                "type": "proposal_confirm",
                "target_nation": target_nation,
                "talleyrand_text": (
                    f"As you wish, Sire. I have drafted harsher terms for {target_nation}.{cap_msg}"
                ),
                "options": options,
                "context": context,
                "turn_created": int(world.current_turn),
                "blocking": False,
            }
            from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
            new_dialogue = _enrich_proposal_summary(new_dialogue, target_nation, proposal_type, world)
            world.pending_diplomatic_dialogue = new_dialogue
            return {
                "success": True,
                "message": new_dialogue["talleyrand_text"],
                "diplomatic_dialogue": new_dialogue,
            }

        elif action == "modify_generous":
            terms = selected.get("terms", {})
            proposal_type = terms.get("proposal_type", dialogue.get("_proposal_type", "peace"))
            if not proposal_type:
                proposal_type = "peace"

            # Build on PREVIOUS terms (not fresh) so each iteration escalates.
            # First click: terms come from the original suggested terms on the button.
            # Second click: terms come from round 1's modified terms on the button.
            import copy
            suggested = copy.deepcopy(terms) if terms.get("sweeteners") is not None or terms.get("demands") is not None else generate_suggested_terms(target_nation, proposal_type, world)
            # Ensure proposal metadata
            suggested["proposer_nation"] = suggested.get("proposer_nation", "France")
            suggested["target_nation"] = suggested.get("target_nation", target_nation)
            suggested["type"] = suggested.get("type", proposal_type)

            # Escalate existing sweeteners by 1.5x
            for s in suggested.get("sweeteners", []):
                if s.get("type") not in ("territory_cede", "ap_per_turn"):
                    s["value"] = int(s.get("value", 0) * 1.5)

            # Context-aware gold sweetener if none exist:
            # Peace/armistice → gold_per_turn (ongoing commitment)
            # Alliance/NAP/other → gold_lump (signing bonus)
            if not [s for s in suggested.get("sweeteners", []) if "gold" in s.get("type", "")]:
                player_gold = getattr(world, 'gold', 500)
                offer = max(100, min(500, int(player_gold * 0.1)))
                if proposal_type in ("peace", "armistice", "armistice_losing", "armistice_winning"):
                    suggested.setdefault("sweeteners", []).append({"type": "gold_per_turn", "value": int(offer)})
                else:
                    suggested.setdefault("sweeteners", []).append({"type": "gold_lump", "value": int(offer)})

            # Round 2 escalation: add AP if not already present (creative variety)
            context_pre = dict(dialogue.get("context", {}))
            round_num = context_pre.get("modify_count", 0) + 1
            if round_num >= 2:
                has_ap = any(s.get("type") == "ap_per_turn" for s in suggested.get("sweeteners", []))
                if not has_ap:
                    suggested.setdefault("sweeteners", []).append({"type": "ap_per_turn", "value": 1})

            # Remove demands (generous = no demands)
            suggested["demands"] = []

            # Bug 5 fix: Use nation-specific smart commentary
            from backend.game_logic.diplomatic_templates import _get_smart_commentary
            suggested["talleyrand_commentary"] = _get_smart_commentary(target_nation, "modified_generous")

            # BUGFIX (Bug 4C): §9b iteration cap — max 2 modifications.
            # modify_count is carried in dialogue context across round-trips.
            # See BUGFIX_PLAN_PROPOSAL_FLOW.md.
            context = dict(dialogue.get("context", {}))
            modify_count = context.get("modify_count", 0) + 1
            context["modify_count"] = modify_count

            options = [
                {
                    "label": "Send these terms",
                    "description": "Dispatch with these generous terms.",
                    "action": "execute_proposal",
                    "terms": {**suggested, "proposal_type": proposal_type},
                },
            ]
            if modify_count < 2:
                options.append({
                    "label": "Even more generous",
                    "description": "Offer even more.",
                    "action": "modify_generous",
                    "terms": {**suggested, "proposal_type": proposal_type},
                })
            options.append({"label": "Reconsider", "description": "Let me think.", "action": "reconsider"})

            cap_msg = ""
            if modify_count >= 2:
                cap_msg = (
                    " We are offering everything short of the crown itself. "
                    "Any more and we negotiate from our knees."
                )

            new_dialogue = {
                "type": "proposal_confirm",
                "target_nation": target_nation,
                "talleyrand_text": (
                    f"A magnanimous approach, Sire. More generous terms for {target_nation}.{cap_msg}"
                ),
                "options": options,
                "context": context,
                "turn_created": int(world.current_turn),
                "blocking": False,
            }
            from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
            new_dialogue = _enrich_proposal_summary(new_dialogue, target_nation, proposal_type, world)
            world.pending_diplomatic_dialogue = new_dialogue
            return {
                "success": True,
                "message": new_dialogue["talleyrand_text"],
                "diplomatic_dialogue": new_dialogue,
            }

        elif action == "expand_options":
            # Show available proposal types for a target nation
            terms = selected.get("terms", {})
            expand_target = terms.get("target_nation", target_nation)
            if not expand_target:
                world.pending_diplomatic_dialogue = None
                return {"success": True, "message": "Very well, Sire."}

            # Re-route as a vague proposal with the target set
            diplomatic_data = {
                "action": "diplomatic_proposal",
                "diplomat": "Talleyrand",
                "target_nation": expand_target,
                "proposal_type": None,
                "clauses": [],
                "is_question": False,
                "has_diplomatic_keywords": True,
                "tone": "propose",
                "raw_text": f"propose to {expand_target}",
            }
            world.pending_diplomatic_dialogue = None  # Clear current
            from backend.game_logic.diplomatic_dialogue import (
                classify_diplomatic_intent, generate_dialogue,
            )
            intent = classify_diplomatic_intent(diplomatic_data, world)
            new_dialogue = generate_dialogue(intent, diplomatic_data, world)
            world.pending_diplomatic_dialogue = new_dialogue
            return {
                "success": True,
                "message": new_dialogue.get("talleyrand_text", ""),
                "diplomatic_dialogue": new_dialogue,
            }

        elif action == "adjust_terms":
            # Entry point for conversational terms guidance
            from backend.game_logic.diplomatic_templates import rank_cession_candidates
            from backend.game_logic.diplomacy import get_war_score_for

            context = dict(dialogue.get("context", {}))
            proposal_type = context.get("proposal_type") or dialogue.get("proposal_type", "")
            # Get proposal_type from selected option if available
            sel_terms = selected.get("terms", {})
            if sel_terms.get("proposal_type"):
                proposal_type = sel_terms["proposal_type"]
            # Scan sibling options as fallback (T6 "Send as suggested" carries terms)
            if not proposal_type:
                for opt in dialogue.get("options", []):
                    pt = (opt.get("terms") or {}).get("proposal_type")
                    if pt:
                        proposal_type = pt
                        break
            proposal_type = proposal_type or "peace"
            context["proposal_type"] = proposal_type
            context["target_nation"] = target_nation
            context["approved_regions"] = []
            context["approved_sweeteners"] = []
            context["candidate_index"] = 0
            context["gold_amount"] = 0

            diplo_key = world._make_diplo_key(world.player_nation, target_nation)
            relation = world.nation_relations.get(diplo_key, 0)
            war_score = get_war_score_for(world, world.player_nation, target_nation)

            # Determine if territory is relevant (losing or hostile)
            needs_territory = war_score < 0 or relation < -50

            if needs_territory:
                ranked = rank_cession_candidates(world, world.player_nation, target_nation)
                context["ranked_candidates"] = ranked

                if not ranked:
                    # No non-capital regions to offer
                    context["guidance_state"] = "gold"
                    return self._build_gold_step(context, world, dialogue,
                                                 intro="We have nothing to offer but our capital, Sire. ")
                else:
                    max_cede = 1 if war_score >= -40 else 2
                    context["regions_needed"] = max_cede
                    context["guidance_state"] = "territory"
                    new_dialogue = {
                        "type": "terms_guidance",
                        "target_nation": target_nation,
                        "talleyrand_text": "Shall we discuss concessions, Sire?",
                        "options": [
                            {"label": "Yes, discuss territory", "description": "Let me suggest regions to offer.",
                             "action": "territory_yes"},
                            {"label": "No territory — offer gold", "description": "Skip territory, move to gold.",
                             "action": "territory_no_gold"},
                            {"label": "Offer Action Points", "description": "Skip to AP offering.",
                             "action": "territory_no_ap"},
                        ],
                        "context": context,
                        "turn_created": int(world.current_turn),
                        "blocking": False,
                    }
                    world.pending_diplomatic_dialogue = new_dialogue
                    return {
                        "success": True,
                        "message": new_dialogue["talleyrand_text"],
                        "diplomatic_dialogue": new_dialogue,
                    }
            else:
                # Winning — skip territory, go to gold
                context["ranked_candidates"] = []
                context["regions_needed"] = 0
                context["guidance_state"] = "gold"
                return self._build_gold_step(context, world, dialogue)

        elif action == "territory_yes":
            context = self._copy_guidance_context(dialogue)
            ranked = context.get("ranked_candidates", [])
            idx = context.get("candidate_index", 0)
            if idx < len(ranked):
                candidate_name, reason = ranked[idx]
                context["guidance_state"] = "region_pick"
                new_dialogue = {
                    "type": "terms_guidance",
                    "target_nation": context.get("target_nation", target_nation),
                    "talleyrand_text": f"I suggest {candidate_name} — {reason}",
                    "options": [
                        {"label": "Offer this region", "description": f"Add {candidate_name} to the offer.",
                         "action": "offer_region"},
                        {"label": "Not this one", "description": "Show me the next candidate.",
                         "action": "skip_region"},
                        {"label": "That's enough territory", "description": "Move on to gold.",
                         "action": "enough_territory"},
                    ],
                    "context": context,
                    "turn_created": int(world.current_turn),
                    "blocking": False,
                }
                world.pending_diplomatic_dialogue = new_dialogue
                return {
                    "success": True,
                    "message": new_dialogue["talleyrand_text"],
                    "diplomatic_dialogue": new_dialogue,
                }
            else:
                # No candidates at all
                context["guidance_state"] = "gold"
                return self._build_gold_step(context, world, dialogue)

        elif action == "offer_region":
            context = self._copy_guidance_context(dialogue)
            ranked = context.get("ranked_candidates", [])
            idx = context.get("candidate_index", 0)
            if idx < len(ranked):
                region_name = ranked[idx][0]
                context["approved_regions"].append(region_name)
                context["approved_sweeteners"].append(
                    {"type": "territory_cede", "value": 1, "regions": [region_name]}
                )
                context["candidate_index"] = idx + 1

            regions_needed = context.get("regions_needed", 1)
            approved_count = len(context.get("approved_regions", []))
            next_idx = context.get("candidate_index", 0)

            # More regions needed and candidates available?
            if approved_count < regions_needed and next_idx < len(ranked):
                candidate_name, reason = ranked[next_idx]
                context["guidance_state"] = "region_pick"
                new_dialogue = {
                    "type": "terms_guidance",
                    "target_nation": context.get("target_nation", target_nation),
                    "talleyrand_text": f"Very good. I also suggest {candidate_name} — {reason}",
                    "options": [
                        {"label": "Offer this region", "description": f"Add {candidate_name} to the offer.",
                         "action": "offer_region"},
                        {"label": "Not this one", "description": "Show me the next candidate.",
                         "action": "skip_region"},
                        {"label": "That's enough territory", "description": "Move on to gold.",
                         "action": "enough_territory"},
                    ],
                    "context": context,
                    "turn_created": int(world.current_turn),
                    "blocking": False,
                }
                world.pending_diplomatic_dialogue = new_dialogue
                return {
                    "success": True,
                    "message": new_dialogue["talleyrand_text"],
                    "diplomatic_dialogue": new_dialogue,
                }
            else:
                # Enough regions or no more candidates — move to gold
                context["guidance_state"] = "gold"
                return self._build_gold_step(context, world, dialogue)

        elif action == "skip_region":
            context = self._copy_guidance_context(dialogue)
            ranked = context.get("ranked_candidates", [])
            context["candidate_index"] = context.get("candidate_index", 0) + 1
            next_idx = context["candidate_index"]

            if next_idx < len(ranked):
                candidate_name, reason = ranked[next_idx]
                context["guidance_state"] = "region_pick"
                new_dialogue = {
                    "type": "terms_guidance",
                    "target_nation": context.get("target_nation", target_nation),
                    "talleyrand_text": f"Very well. What about {candidate_name}? {reason}",
                    "options": [
                        {"label": "Offer this region", "description": f"Add {candidate_name} to the offer.",
                         "action": "offer_region"},
                        {"label": "Not this one", "description": "Show me the next candidate.",
                         "action": "skip_region"},
                        {"label": "That's enough territory", "description": "Move on to gold.",
                         "action": "enough_territory"},
                    ],
                    "context": context,
                    "turn_created": int(world.current_turn),
                    "blocking": False,
                }
                world.pending_diplomatic_dialogue = new_dialogue
                return {
                    "success": True,
                    "message": new_dialogue["talleyrand_text"],
                    "diplomatic_dialogue": new_dialogue,
                }
            else:
                # All candidates exhausted
                context["guidance_state"] = "gold"
                new_dialogue = {
                    "type": "terms_guidance",
                    "target_nation": context.get("target_nation", target_nation),
                    "talleyrand_text": "There are no more suitable regions to offer, Sire.",
                    "options": [
                        {"label": "Offer gold", "description": "Move to gold terms.",
                         "action": "territory_no_gold"},
                        {"label": "Offer Action Points", "description": "Skip to AP offering.",
                         "action": "territory_no_ap"},
                        {"label": "Done", "description": "Proceed with what we have.",
                         "action": "skip_ap"},
                    ],
                    "context": context,
                    "turn_created": int(world.current_turn),
                    "blocking": False,
                }
                world.pending_diplomatic_dialogue = new_dialogue
                return {
                    "success": True,
                    "message": new_dialogue["talleyrand_text"],
                    "diplomatic_dialogue": new_dialogue,
                }

        elif action == "enough_territory":
            context = self._copy_guidance_context(dialogue)
            context["guidance_state"] = "gold"
            return self._build_gold_step(context, world, dialogue)

        elif action == "territory_no_gold":
            context = self._copy_guidance_context(dialogue)
            context["guidance_state"] = "gold"
            return self._build_gold_step(context, world, dialogue)

        elif action == "territory_no_ap":
            context = self._copy_guidance_context(dialogue)
            context["guidance_state"] = "ap"
            return self._build_ap_step(context, world, dialogue)

        elif action == "offer_gold":
            context = self._copy_guidance_context(dialogue)
            gold = int(context.get("gold_amount", 50))
            context["approved_sweeteners"].append({"type": "gold_per_turn", "value": int(gold)})
            context["guidance_state"] = "ap"
            return self._build_ap_step(context, world, dialogue)

        elif action == "more_gold":
            context = self._copy_guidance_context(dialogue)
            gold = context.get("gold_amount", 50)
            context["gold_amount"] = int(min(500, gold * 1.5))
            context["guidance_state"] = "gold"
            return self._build_gold_step(context, world, dialogue, rebuild=True)

        elif action == "less_gold":
            context = self._copy_guidance_context(dialogue)
            gold = context.get("gold_amount", 50)
            context["gold_amount"] = int(max(25, gold * 0.7))
            context["guidance_state"] = "gold"
            return self._build_gold_step(context, world, dialogue, rebuild=True)

        elif action == "skip_gold":
            context = self._copy_guidance_context(dialogue)
            context["guidance_state"] = "ap"
            return self._build_ap_step(context, world, dialogue)

        elif action == "offer_ap":
            context = self._copy_guidance_context(dialogue)
            context["approved_sweeteners"].append({"type": "ap_per_turn", "value": 1})
            context["guidance_state"] = "confirm"
            return self._build_confirm_step(context, world, dialogue)

        elif action == "skip_ap":
            context = self._copy_guidance_context(dialogue)
            context["guidance_state"] = "confirm"
            return self._build_confirm_step(context, world, dialogue)

        elif action == "start_mission":
            terms = selected.get("terms", {})
            mission_type = terms.get("mission_type", "IMPROVE_RELATIONS")
            mission_target = terms.get("target_nation", target_nation)

            if not mission_target:
                world.pending_diplomatic_dialogue = None
                return {"success": False, "message": "Which nation, Sire?"}

            # Check DP
            cost = MISSION_DP_COSTS.get(mission_type, 1)
            if world.diplomatic_points < cost:
                world.pending_diplomatic_dialogue = None
                return {
                    "success": False,
                    "message": f"Insufficient DP. Mission costs {int(cost)} DP per turn.",
                }

            # Cancel existing mission
            world.active_diplomatic_mission = {
                "type": mission_type,
                "target": mission_target,
                "turns_active": 0,
                "paused": False,
                "paused_turns": 0,
            }
            world.talleyrand_state = "ON_MISSION"

            description = MISSION_DESCRIPTIONS.get(mission_type, "conduct diplomacy with")

            world.log_event({
                "type": "diplomatic_mission_started",
                "mission_type": mission_type,
                "target": mission_target,
            })

            world.pending_diplomatic_dialogue = None
            return {
                "success": True,
                "message": f"Talleyrand begins efforts to {description} {mission_target}. ({int(cost)} DP/turn)",
            }

        elif action == "cancel_mission":
            existing = getattr(world, 'active_diplomatic_mission', None)
            if not existing:
                world.pending_diplomatic_dialogue = None
                return {"success": False, "message": "No active mission to cancel."}
            old_target = existing.get("target", "unknown")
            world.active_diplomatic_mission = None
            world.talleyrand_state = "IDLE"
            world.pending_diplomatic_dialogue = None
            return {
                "success": True,
                "message": f"Talleyrand's mission to {old_target} has been cancelled.",
            }

        elif action == "accept_ai_proposal":
            return self._handle_accept_ai_proposal(dialogue, world)

        elif action == "reject_ai_proposal":
            return self._handle_reject_ai_proposal(dialogue, world)

        elif action == "counter_ai_proposal":
            return self._handle_counter_ai_proposal(dialogue, world)

        elif action == "expand_to_proposal":
            # Advisory drill-down: re-route to proposal dialogue for a nation
            expand_target = dialogue.get("target_nation", target_nation)
            if not expand_target:
                world.pending_diplomatic_dialogue = None
                return {"success": True, "message": "Very well, Sire."}
            diplomatic_data = {
                "action": "diplomatic_proposal",
                "diplomat": "Talleyrand",
                "target_nation": expand_target,
                "proposal_type": None,
                "clauses": [],
                "is_question": False,
                "has_diplomatic_keywords": True,
                "tone": "propose",
                "raw_text": f"propose to {expand_target}",
            }
            world.pending_diplomatic_dialogue = None
            from backend.game_logic.diplomatic_dialogue import (
                classify_diplomatic_intent, generate_dialogue as gen_dlg,
            )
            intent = classify_diplomatic_intent(diplomatic_data, world)
            new_dialogue = gen_dlg(intent, diplomatic_data, world)
            world.pending_diplomatic_dialogue = new_dialogue
            return {
                "success": True,
                "message": new_dialogue.get("talleyrand_text", ""),
                "diplomatic_dialogue": new_dialogue,
            }

        # ═══════════════════════════════════════════════════════
        # GAP-1: ELABORATE / REVIEW_COUNTER / ACCEPT_WITH_CONFLICT
        # ═══════════════════════════════════════════════════════
        elif action == "elaborate":
            # Same behavior as expand_to_proposal — drill down to proposal for nation
            return self._process_dialogue_choice("expand_to_proposal", selected, dialogue, world)

        elif action == "review_counter":
            # Show counter-offer terms from context for player review
            context = dialogue.get("context", {})
            counter_terms = context.get("counter_terms", {})
            source_nation = context.get("source_nation", target_nation)
            if not counter_terms:
                world.pending_diplomatic_dialogue = None
                return {"success": True, "message": "No counter-offer terms to review, Sire."}
            # Build a new confirmation dialogue showing the counter terms
            from backend.game_logic.diplomatic_dialogue import _format_terms_for_display
            proposal_type = counter_terms.get("type", counter_terms.get("proposal_type", "peace"))
            terms_display = _format_terms_for_display(counter_terms, proposal_type, source_nation)
            new_dialogue = {
                "type": "proposal_confirm",
                "target_nation": source_nation,
                "talleyrand_text": f"Here are the counter-terms from {source_nation}, Sire.",
                "options": [
                    {
                        "label": "Accept counter-offer",
                        "description": f"Ratify {source_nation}'s proposed terms.",
                        "action": "accept_counter_offer",
                    },
                    {
                        "label": "Reject counter-offer",
                        "description": "Decline these terms.",
                        "action": "reject_counter_offer",
                    },
                    {"label": "Dismiss", "description": "Set this aside.", "action": "dismiss"},
                ],
                "context": context,
                "turn_created": int(world.current_turn),
                "blocking": False,
                "proposal_terms_summary": terms_display,
            }
            from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
            new_dialogue = _enrich_proposal_summary(new_dialogue, source_nation, proposal_type, world)
            world.pending_diplomatic_dialogue = new_dialogue
            return {
                "success": True,
                "message": new_dialogue["talleyrand_text"],
                "diplomatic_dialogue": new_dialogue,
            }

        elif action == "accept_with_conflict":
            # Accept AI proposal despite alliance conflict warning
            return self._handle_accept_ai_proposal(dialogue, world)

        # ═══════════════════════════════════════════════════════
        # R37: SABOTAGE CONFRONTATION HANDLERS
        # ═══════════════════════════════════════════════════════
        elif action in ("confront_sabotage", "overlook_sabotage"):
            from backend.commands.diplomatic_defiance import resolve_confrontation
            talleyrand = world.diplomats.get("France")
            if not talleyrand:
                world.pending_diplomatic_dialogue = None
                return {"success": False, "message": "No diplomat available."}
            try:
                result = resolve_confrontation(action, talleyrand, world)
            except Exception:
                world.pending_diplomatic_dialogue = None
                return {"success": True, "message": "The matter has been resolved."}
            world.pending_diplomatic_dialogue = None
            world.diplomatic_sabotage = None
            # Dismiss stale sabotage notification
            from backend.notifications import SABOTAGE_DISCOVERED
            world.notifications.dismiss_by_type(SABOTAGE_DISCOVERED)
            return {
                "success": True,
                "message": result.get("message", "The matter has been resolved."),
            }

        # ═══════════════════════════════════════════════════════
        # R41: TALLEYRAND REDEMPTION HANDLERS
        # ═══════════════════════════════════════════════════════
        elif action in ("redemption_apologize", "redemption_replace", "redemption_continue"):
            from backend.commands.diplomatic_defiance import apply_redemption_choice
            talleyrand = world.diplomats.get("France")
            if not talleyrand:
                world.pending_diplomatic_dialogue = None
                return {"success": False, "message": "No diplomat available."}
            try:
                result = apply_redemption_choice(action, talleyrand, world)
            except Exception:
                world.pending_diplomatic_dialogue = None
                return {"success": True, "message": "The matter has been settled."}
            world.pending_diplomatic_dialogue = None
            world.talleyrand_redemption = None
            return {
                "success": True,
                "message": result.get("message", "The matter has been settled."),
            }

        # ═══════════════════════════════════════════════════════
        # R42: PRE-PROPOSAL OBJECTION OVERRIDE HANDLERS
        # ═══════════════════════════════════════════════════════
        elif action in ("send_override", "send_suggested"):
            terms = selected.get("terms", {})
            if action == "send_suggested":
                # Use Talleyrand's suggested terms from context
                terms = terms or dialogue.get("context", {}).get("suggested_terms", {})
            else:
                # Use original terms from context
                terms = terms or dialogue.get("context", {}).get("original_proposal", {})

            proposal_type = terms.get("proposal_type", "peace")

            # Build proposal and send (reuse execute_proposal path)
            proposal = {
                "type": proposal_type,
                "proposer_nation": "France",
                "target_nation": target_nation,
                "sweeteners": terms.get("sweeteners", []),
                "demands": terms.get("demands", []),
                "clauses": terms.get("clauses", []),
            }

            # Deduct DP (with jump cost for multi-step transitions)
            talleyrand = world.diplomats.get("France")
            skill = talleyrand.skill if talleyrand else 5
            dp_action = f"propose_{proposal_type}"
            # R98: Compute cumulative DP for jump transitions
            _state_map = {"peace": "PEACE", "alliance": "ALLIANCE", "defensive_alliance": "DEFENSIVE_ALLIANCE",
                          "non_aggression": "NON_AGGRESSION", "open_borders": "OPEN_BORDERS", "armistice": "ARMISTICE"}
            current_diplo = world.get_diplomatic_state("France", target_nation) if target_nation else "PEACE"
            target_diplo = _state_map.get(proposal_type, "PEACE")
            jump_cost = get_transition_dp_cost(current_diplo, target_diplo)
            cost = get_dp_cost(dp_action, skill, transition_base=jump_cost)
            if world.diplomatic_points < cost:
                world.pending_diplomatic_dialogue = None
                return {
                    "success": False,
                    "message": f"Insufficient Diplomatic Points. Need {int(cost)}, have {int(world.diplomatic_points)}.",
                    "diplomatic_dialogue": None,
                    "awaiting_diplomatic_response": False,
                }
            world.diplomatic_points -= cost

            # Set Talleyrand in transit
            mission = getattr(world, 'active_diplomatic_mission', None)
            if mission and not mission.get("paused"):
                mission["paused"] = True

            world.talleyrand_state = "IN_TRANSIT"
            world.proposal_in_transit = {
                "target": target_nation,
                "proposal": proposal,
                "turn_sent": int(world.current_turn),
            }

            # Record override if player overrode Talleyrand's objection
            if action == "send_override":
                from backend.commands.diplomatic_defiance import record_override
                record_override(world, proposal_type, "override")

            world.log_event({
                "type": "diplomatic_proposal_sent",
                "target": target_nation,
                "proposal_type": proposal_type,
            })

            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_proposal_sent",
                                {"nation": target_nation}, "always")

            world.pending_diplomatic_dialogue = None
            override_note = " despite Talleyrand's objections" if action == "send_override" else " with Talleyrand's suggested terms"
            return {
                "success": True,
                "message": (
                    f"Talleyrand departs for the {target_nation} court{override_note}. "
                    f"Expect a response by next turn. ({int(cost)} DP spent)"
                ),
            }

        # ═══════════════════════════════════════════════════════
        # R2: COUNTER-OFFER RESPONSE HANDLERS
        # ═══════════════════════════════════════════════════════
        elif action == "accept_counter_offer":
            context = dialogue.get("context", {})
            counter_terms = context.get("counter_terms", {})
            source_nation = context.get("source_nation", target_nation)
            if not source_nation or not counter_terms:
                world.pending_diplomatic_dialogue = None
                return {"success": False, "message": "Error: counter-offer data missing."}
            # Ratify treaty with counter terms (0 DP cost — already paid on original proposal)
            if "proposer_nation" not in counter_terms:
                counter_terms["proposer_nation"] = source_nation
            if "target_nation" not in counter_terms:
                counter_terms["target_nation"] = world.player_nation
            treaty_event = world._ratify_treaty(counter_terms)
            world.pending_diplomatic_dialogue = None
            world.incoming_proposal_popup = None
            # Dismiss stale proposal notification
            from backend.notifications import DIPLOMATIC_PROPOSAL
            world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)
            treaty_msg = treaty_event.get("message", "") if treaty_event else ""
            world.log_event({
                "type": "counter_offer_accepted",
                "source": source_nation,
                "proposal_type": counter_terms.get("type", "unknown"),
            })
            return {
                "success": True,
                "message": f"You have accepted {source_nation}'s counter-proposal. {treaty_msg}",
            }

        elif action == "reject_counter_offer":
            context = dialogue.get("context", {})
            source_nation = context.get("source_nation", target_nation)
            original = context.get("original_proposal", {})
            ptype = original.get("type", "unknown")
            # Apply rejection cooldowns and relation penalty
            if source_nation:
                world.modify_nation_relation("France", source_nation, -5)
                world.player_proposal_cooldowns[source_nation] = 3
                if ptype:
                    world.player_proposal_cooldowns[f"{source_nation}_{ptype}"] = 5
            world.pending_diplomatic_dialogue = None
            world.incoming_proposal_popup = None
            # Dismiss stale proposal notification
            from backend.notifications import DIPLOMATIC_PROPOSAL
            world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)
            world.log_event({
                "type": "counter_offer_rejected",
                "source": source_nation,
                "proposal_type": ptype,
            })
            return {
                "success": True,
                "message": f"You have rejected {source_nation}'s counter-proposal. Relations cooled slightly.",
            }

        # ═══════════════════════════════════════════════════════
        # R74: VASSAL REBELLION IMMINENT HANDLERS
        # ═══════════════════════════════════════════════════════
        elif action == "invest_vassal_rebellion":
            context = dialogue.get("context", {})
            vassal_name = context.get("vassal_name", "")
            if not vassal_name:
                world.pending_diplomatic_dialogue = None
                return {"success": False, "message": "No vassal specified."}
            from backend.game_logic.vassal import invest_in_vassal
            result = invest_in_vassal(world, vassal_name)
            world.pending_diplomatic_dialogue = None
            world.vassal_rebellion_imminent_popup = None
            # Dismiss stale vassal rebellion notification
            from backend.notifications import VASSAL_REBELLION_IMMINENT
            world.notifications.dismiss_by_type(VASSAL_REBELLION_IMMINENT)
            return result

        elif action == "garrison_vassal_rebellion":
            context = dialogue.get("context", {})
            vassal_name = context.get("vassal_name", "")
            if not vassal_name:
                world.pending_diplomatic_dialogue = None
                return {"success": False, "message": "No vassal specified."}
            # Guard: vassal may have been removed between popup and response
            if vassal_name not in world.vassals:
                world.pending_diplomatic_dialogue = None
                world.vassal_rebellion_imminent_popup = None
                return {"success": False, "message": f"{vassal_name} is no longer a vassal."}
            # Deploy garrison: +10 loyalty, costs 2 AP
            if world.actions_remaining < 2:
                world.pending_diplomatic_dialogue = None
                return {
                    "success": False,
                    "message": f"Insufficient AP. Garrison deployment costs 2 AP, you have {int(world.actions_remaining)}.",
                }
            world.actions_remaining -= 2
            vassal_state = world.vassals.get(vassal_name, {})
            old_loyalty = vassal_state.get("loyalty", 0)
            vassal_state["loyalty"] = min(100, old_loyalty + 10)
            world.pending_diplomatic_dialogue = None
            world.vassal_rebellion_imminent_popup = None
            # Dismiss stale vassal rebellion notification
            from backend.notifications import VASSAL_REBELLION_IMMINENT
            world.notifications.dismiss_by_type(VASSAL_REBELLION_IMMINENT)
            return {
                "success": True,
                "message": (
                    f"Imperial garrison deployed to {vassal_name}. "
                    f"Loyalty: {int(old_loyalty)} → {int(vassal_state['loyalty'])}. (2 AP spent)"
                ),
            }

        elif action == "accept_vassal_rebellion":
            world.pending_diplomatic_dialogue = None
            world.vassal_rebellion_imminent_popup = None
            # Dismiss stale vassal rebellion notification
            from backend.notifications import VASSAL_REBELLION_IMMINENT
            world.notifications.dismiss_by_type(VASSAL_REBELLION_IMMINENT)
            context = dialogue.get("context", {})
            vassal_name = context.get("vassal_name", "")
            return {
                "success": True,
                "message": (
                    f"You accept the risk. If {vassal_name}'s loyalty reaches zero, "
                    f"rebellion will follow."
                ),
            }

        # ═══════════════════════════════════════════════════════
        # R12: ALLIANCE PARADOX HANDLERS
        # ═══════════════════════════════════════════════════════
        elif action == "honor_defender":
            terms = selected.get("terms", {})
            attacker_nation = terms.get("attacker", "")
            defender_nation = terms.get("defender", "")
            if not attacker_nation or not defender_nation:
                world.pending_diplomatic_dialogue = None
                return {"success": False, "message": "Error: paradox data missing."}
            from backend.game_logic.diplomacy import declare_war as _paradox_declare_war
            # Honor alliance with defender: declare war on attacker
            war_result = _paradox_declare_war(world, world.player_nation, attacker_nation)
            world.pending_diplomatic_dialogue = None
            world.alliance_paradox_popup = None
            # Dismiss stale alliance cascade notification
            from backend.notifications import ALLIANCE_CASCADE_WAR
            world.notifications.dismiss_by_type(ALLIANCE_CASCADE_WAR)
            msg = (
                f"France honors its alliance with {defender_nation} and declares war on {attacker_nation}!"
            )
            if war_result.get("message"):
                msg += f" {war_result['message']}"
            return {"success": True, "message": msg}

        elif action == "break_defender_alliance":
            terms = selected.get("terms", {})
            attacker_nation = terms.get("attacker", "")
            defender_nation = terms.get("defender", "")
            if not attacker_nation or not defender_nation:
                world.pending_diplomatic_dialogue = None
                return {"success": False, "message": "Error: paradox data missing."}
            from backend.game_logic.diplomacy import execute_downgrade as _paradox_downgrade
            # Break alliance with defender: downgrade step by step to PEACE
            player = world.player_nation
            diplo_key = world._make_diplo_key(player, defender_nation)
            current = world.diplomatic_states.get(diplo_key, "PEACE")
            while current in ("ALLIANCE", "DEFENSIVE_ALLIANCE", "NON_AGGRESSION", "OPEN_BORDERS"):
                dg_result = _paradox_downgrade(world, player, defender_nation)
                if not dg_result.get("success"):
                    break
                current = dg_result.get("new_state", "PEACE")
            # Also remove active treaty
            active_treaties = getattr(world, 'active_treaties', {})
            active_treaties.pop(diplo_key, None)
            world.pending_diplomatic_dialogue = None
            world.alliance_paradox_popup = None
            # Dismiss stale alliance cascade notification
            from backend.notifications import ALLIANCE_CASCADE_WAR
            world.notifications.dismiss_by_type(ALLIANCE_CASCADE_WAR)
            return {
                "success": True,
                "message": (
                    f"France abandons its alliance with {defender_nation}. "
                    f"We side with {attacker_nation} in this conflict."
                ),
            }

        else:
            world.pending_diplomatic_dialogue = None
            return {"success": False, "message": f"Unknown dialogue action: {action}"}

    # ═══════════════════════════════════════════════════════════
    # CONVERSATIONAL TERMS GUIDANCE HELPERS
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _copy_guidance_context(dialogue: dict) -> dict:
        """Deep-copy guidance context so list mutations don't leak to old dialogues."""
        import copy
        ctx = dialogue.get("context", {})
        return copy.deepcopy(ctx)

    def _build_gold_step(self, context: dict, world, dialogue: dict,
                         intro: str = "", rebuild: bool = False) -> dict:
        """Build the gold offering dialogue step."""
        from backend.game_logic.diplomacy import get_war_score_for

        target_nation = context.get("target_nation", "")
        if not rebuild:
            diplo_key = world._make_diplo_key(world.player_nation, target_nation)
            relation = world.nation_relations.get(diplo_key, 0)
            war_score = get_war_score_for(world, world.player_nation, target_nation)
            gold = int(max(25, min(200, max(abs(war_score) * 3, abs(relation)))))
            context["gold_amount"] = gold
        gold = int(context.get("gold_amount", 50))

        text = f"{intro}I suggest offering {int(gold)} gold per turn."
        new_dialogue = {
            "type": "terms_guidance",
            "target_nation": target_nation,
            "talleyrand_text": text,
            "options": [
                {"label": f"Offer {int(gold)} gold", "description": "Add this gold to the offer.",
                 "action": "offer_gold"},
                {"label": "Offer more", "description": "Increase the gold amount.",
                 "action": "more_gold"},
                {"label": "Offer less", "description": "Decrease the gold amount.",
                 "action": "less_gold"},
                {"label": "Skip gold", "description": "Move on without offering gold.",
                 "action": "skip_gold"},
            ],
            "context": context,
            "turn_created": int(world.current_turn),
            "blocking": False,
        }
        world.pending_diplomatic_dialogue = new_dialogue
        return {
            "success": True,
            "message": new_dialogue["talleyrand_text"],
            "diplomatic_dialogue": new_dialogue,
        }

    def _build_ap_step(self, context: dict, world, dialogue: dict) -> dict:
        """Build the AP offering dialogue step."""
        target_nation = context.get("target_nation", "")
        new_dialogue = {
            "type": "terms_guidance",
            "target_nation": target_nation,
            "talleyrand_text": (
                "Offering an Action Point is extraordinary — an entire extra action each turn. "
                "Worth 18 acceptance points, more than ceding a province."
            ),
            "options": [
                {"label": "Offer the AP", "description": "Add 1 AP per turn to the offer.",
                 "action": "offer_ap"},
                {"label": "Too costly", "description": "Skip AP and finalize.",
                 "action": "skip_ap"},
            ],
            "context": context,
            "turn_created": int(world.current_turn),
            "blocking": False,
        }
        world.pending_diplomatic_dialogue = new_dialogue
        return {
            "success": True,
            "message": new_dialogue["talleyrand_text"],
            "diplomatic_dialogue": new_dialogue,
        }

    def _build_confirm_step(self, context: dict, world, dialogue: dict) -> dict:
        """Assemble final terms and show confirmation."""
        from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary

        target_nation = context.get("target_nation", "")
        proposal_type = context.get("proposal_type", "peace")
        sweeteners = context.get("approved_sweeteners", [])

        # Build terms dict for acceptance calculation
        terms = {
            "type": proposal_type,
            "proposal_type": proposal_type,
            "proposer_nation": world.player_nation,
            "target_nation": target_nation,
            "sweeteners": sweeteners,
            "demands": [],
            "clauses": [],
        }
        # Include open borders for peace if relation allows
        diplo_key = world._make_diplo_key(world.player_nation, target_nation)
        relation = world.nation_relations.get(diplo_key, 0)
        if proposal_type == "peace" and relation > -20:
            terms["clauses"].append("open_borders")

        # Build summary text
        parts = []
        for s in sweeteners:
            stype = s.get("type", "")
            if stype == "territory_cede":
                regions = s.get("regions", [])
                parts.append(f"Cede {', '.join(regions)}")
            elif stype == "gold_per_turn":
                parts.append(f"Offer {int(s.get('value', 0))} gold/turn")
            elif stype == "ap_per_turn":
                parts.append(f"Offer {int(s.get('value', 0))} AP/turn")
        summary = "; ".join(parts) if parts else "No concessions"

        new_dialogue = {
            "type": "terms_guidance",
            "target_nation": target_nation,
            "talleyrand_text": f"Here are the assembled terms: {summary}.",
            "options": [
                {"label": "Send", "description": "Dispatch this proposal.",
                 "action": "execute_proposal",
                 "terms": terms},
                {"label": "Start over", "description": "Rebuild the offer from scratch.",
                 "action": "adjust_terms"},
                {"label": "Reconsider", "description": "Dismiss and think it over.",
                 "action": "reconsider"},
            ],
            "context": context,
            "turn_created": int(world.current_turn),
            "blocking": False,
        }
        new_dialogue = _enrich_proposal_summary(new_dialogue, target_nation, proposal_type, world)
        world.pending_diplomatic_dialogue = new_dialogue
        return {
            "success": True,
            "message": new_dialogue["talleyrand_text"],
            "diplomatic_dialogue": new_dialogue,
        }

    # ═══════════════════════════════════════════════════════════
    # AI PROPOSAL RESPONSE HANDLERS (Phase 8 Session 4)
    # ═══════════════════════════════════════════════════════════

    def _handle_accept_ai_proposal(self, dialogue: Dict, world) -> Dict:
        """Accept an incoming AI proposal. Executes the state transition."""
        from backend.game_logic.ai_diplomacy import check_alliance_conflict

        context = dialogue.get("context", {})
        terms = context.get("proposal", {})
        source_nation = context.get("source_nation", "")

        if not source_nation or not terms:
            world.pending_diplomatic_dialogue = None
            return {"success": False, "message": "Error: proposal data missing."}

        proposal_type = terms.get("type", "")

        # Check for conflicting alliances (§5b.3) — only on first pass
        # (conflict_alert dialogue type means we already showed the warning)
        if (dialogue.get("type") != "conflict_alert"
                and proposal_type in ("alliance", "defensive_alliance",
                                       "ALLIANCE", "DEFENSIVE_ALLIANCE")):
            new_state = proposal_type.upper()
            conflict = check_alliance_conflict(source_nation, new_state, world)
            if conflict:
                world.pending_diplomatic_dialogue = {
                    "type": "conflict_alert",
                    "target_nation": source_nation,
                    "talleyrand_text": conflict["message"],
                    "options": [
                        {
                            "label": "Accept anyway",
                            "description": f"Accept alliance despite conflict with {', '.join(conflict['conflicting_nations'])}.",
                            "action": "accept_ai_proposal",
                        },
                        {
                            "label": "Reject",
                            "description": "Decline the proposal.",
                            "action": "reject_ai_proposal",
                        },
                    ],
                    "context": context,
                    "turn_created": int(world.current_turn),
                    "blocking": True,
                }
                return {
                    "success": True,
                    "message": conflict["message"],
                    "diplomatic_dialogue": world.pending_diplomatic_dialogue,
                }

        # Execute acceptance via WorldState._ratify_treaty (same path as player proposals)
        if "proposer_nation" not in terms:
            terms["proposer_nation"] = source_nation
        if "target_nation" not in terms:
            terms["target_nation"] = world.player_nation
        treaty_event = world._ratify_treaty(terms)
        world.pending_diplomatic_dialogue = None
        # Bug 2 fix: Dismiss stale DIPLOMATIC_PROPOSAL notification
        from backend.notifications import DIPLOMATIC_PROPOSAL
        world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)

        # Apply acceptance cooldown to prevent immediate follow-up proposals
        from backend.game_logic.ai_diplomacy import apply_acceptance_cooldown
        apply_acceptance_cooldown(source_nation, world)

        treaty_msg = ""
        if treaty_event:
            treaty_msg = treaty_event.get("message", "")

        world.log_event({
            "type": "ai_proposal_accepted",
            "source": source_nation,
            "proposal_type": proposal_type,
        })

        return {
            "success": True,
            "message": (
                f"You have accepted {source_nation}'s proposal. {treaty_msg}"
            ),
        }

    def _handle_reject_ai_proposal(self, dialogue: Dict, world) -> Dict:
        """Reject an incoming AI proposal. Applies cooldowns."""
        from backend.game_logic.ai_diplomacy import apply_rejection_cooldowns

        context = dialogue.get("context", {})
        terms = context.get("proposal", {})
        source_nation = context.get("source_nation", "")
        proposal_type = terms.get("type", "unknown")

        if source_nation:
            apply_rejection_cooldowns(source_nation, proposal_type, world)

        world.pending_diplomatic_dialogue = None
        # Bug 2 fix: Dismiss stale DIPLOMATIC_PROPOSAL notification
        from backend.notifications import DIPLOMATIC_PROPOSAL
        world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)

        world.log_event({
            "type": "ai_proposal_rejected",
            "source": source_nation,
            "proposal_type": proposal_type,
        })

        return {
            "success": True,
            "message": (
                f"You have rejected {source_nation}'s proposal. "
                f"Talleyrand will convey your decision."
            ),
        }

    def _handle_counter_ai_proposal(self, dialogue: Dict, world) -> Dict:
        """Generate and present a counter-offer to an AI proposal."""
        from backend.game_logic.ai_diplomacy import (
            generate_counter_offer, apply_rejection_cooldowns,
            _format_proposal_summary,
        )

        context = dialogue.get("context", {})
        terms = context.get("proposal", {})
        source_nation = context.get("source_nation", "")

        if not source_nation or not terms:
            world.pending_diplomatic_dialogue = None
            return {"success": False, "message": "Error: proposal data missing."}

        # Counter-offer costs 1 DP
        if world.diplomatic_points < 1:
            return {
                "success": False,
                "message": "Insufficient Diplomatic Points. Counter-offers cost 1 DP.",
            }
        world.diplomatic_points -= 1

        # Run M3 counter-offer algorithm
        counter_terms = generate_counter_offer(terms, world)

        if counter_terms is None:
            # Counter failed (score < 30) — auto-reject
            apply_rejection_cooldowns(source_nation, terms.get("type", "unknown"), world)
            world.pending_diplomatic_dialogue = None
            # Bug 2 fix: Dismiss stale DIPLOMATIC_PROPOSAL notification
            from backend.notifications import DIPLOMATIC_PROPOSAL
            world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)

            world.log_event({
                "type": "ai_proposal_counter_failed",
                "source": source_nation,
            })

            return {
                "success": True,
                "message": (
                    f"Talleyrand attempted to negotiate, but {source_nation} "
                    f"found our counter-terms unacceptable. The proposal is rejected. "
                    f"(1 DP spent)"
                ),
            }

        # Counter succeeded — present the modified terms
        counter_summary = _format_proposal_summary(counter_terms)

        # Dismiss stale proposal notification (counter replaces original)
        from backend.notifications import DIPLOMATIC_PROPOSAL
        world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)

        # Fix 4: Mark popup as counter-offer so Godot hides Counter button
        if world.incoming_proposal_popup:
            world.incoming_proposal_popup["is_counter_offer"] = True

        world.pending_diplomatic_dialogue = {
            "type": "counter_offer",
            "target_nation": source_nation,
            "talleyrand_text": (
                f"Sire, I have negotiated modified terms with {source_nation}:\n\n"
                f"  {counter_summary}\n\n"
                f"Shall we proceed with these terms?"
            ),
            "options": [
                {
                    "label": "Accept these terms",
                    "description": "Accept the counter-offer.",
                    "action": "accept_ai_proposal",
                },
                {
                    "label": "Reject",
                    "description": "Decline entirely.",
                    "action": "reject_ai_proposal",
                },
            ],
            "context": {
                "proposal": counter_terms,
                "source_nation": source_nation,
                "is_counter": True,
            },
            "turn_created": int(world.current_turn),
            "blocking": True,
        }

        return {
            "success": True,
            "message": world.pending_diplomatic_dialogue["talleyrand_text"],
            "diplomatic_dialogue": world.pending_diplomatic_dialogue,
        }

    def handle_objection_response(self, choice: str, game_state: Dict) -> Dict:
        """
        Handle player's response to a marshal objection.

        Args:
            choice: 'trust', 'insist', or 'compromise'
            game_state: Current game state dict with 'world' key

        Returns:
            Result dict with execution outcome or error
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # ════════════════════════════════════════════════════════════
        # CHECK FOR STRATEGIC OBJECTION (Phase M)
        # Strategic objections are stored in pending_strategic_objection
        # ════════════════════════════════════════════════════════════
        if getattr(world, 'pending_strategic_objection', None) is not None:
            return self._handle_strategic_objection_from_endpoint(choice, game_state)

        # Check if there's a pending tactical objection
        if world.pending_objection is None:
            return {
                "success": False,
                "message": "No objection pending. Issue a command first."
            }

        objection = world.pending_objection
        marshal_name = objection.get("marshal")

        # Get alternative (disobedience.py uses 'suggested_alternative')
        alternative = objection.get("suggested_alternative") or objection.get("alternative")
        compromise = objection.get("compromise")

        # Validate choice
        valid_choices = ["trust", "insist"]
        if alternative or compromise:
            valid_choices.append("compromise")

        if choice not in valid_choices:
            return {
                "success": False,
                "message": f"Invalid choice: '{choice}'. Valid choices: {', '.join(valid_choices)}"
            }

        # Process the choice through disobedience system
        response_result = world.disobedience_system.handle_response(
            objection=objection,
            choice=choice,
            game_state=world,
            vindication_tracker=world.vindication_tracker
        )

        # Clear the pending objection
        world.pending_objection = None

        # Note: record_response() called inside disobedience_system.handle_response()
        # (disobedience.py:1124, V2b enriched with current_turn). Do NOT call again.
        # Capture authority event from the response_result if threshold crossed.
        authority_event = response_result.get("authority_event")

        # Log objection event (MODERATE+ only — MILD concerns are not logged here)
        world.log_event({
            "type": "objection",
            "marshal": marshal_name,
            "concern_level": objection.get("concern_level", ""),
            "action": (objection.get("original_order") or {}).get("action", ""),
            "target": (objection.get("original_order") or {}).get("target", ""),
            "resolution": choice,
        })

        # ════════════════════════════════════════════════════════════
        # V2b DEFIANCE CHECK (Step 17 in bypass hierarchy)
        # After "insist" + STRONG/EXTREME: defiance roll
        # ════════════════════════════════════════════════════════════
        concern_level_str = objection.get("concern_level", "NONE")
        concern_level_val = ConcernLevel[concern_level_str] if concern_level_str in ConcernLevel.__members__ else ConcernLevel.NONE
        marshal = world.get_marshal(marshal_name)

        if choice == "insist" and marshal and concern_level_val >= ConcernLevel.STRONG:
            from backend.commands.defiance import (
                calculate_defiance_chance, get_defiant_action,
                defiance_succeeded, apply_defiance_outcome
            )
            from backend.notifications import (
                create_notification, NotificationPriority, MARSHAL_DEFIED_ORDER
            )

            # N7 fix: No defiance if marshal is broken/retreating (stale objection via save/load)
            if getattr(marshal, 'broken', False) or getattr(marshal, 'retreating', False):
                defiance_chance = 0.0
            else:
                defiance_chance = calculate_defiance_chance(marshal, concern_level_val, world)
            defiance_roll = random.random()

            if defiance_roll < defiance_chance:
                # ═══ DEFIANCE FIRES ═══
                print(f"  [DEFIANCE] {marshal_name} defies order! (roll={defiance_roll:.2f} < chance={defiance_chance:.2f})")

                original_action = (objection.get("original_order") or {}).get("action", "")
                defiant_action = get_defiant_action(marshal, original_action)

                # If preferred action blocked, fallback to wait (sulk)
                if defiant_action is None:
                    defiant_action = "wait"

                # N3 fix: AP follows action taken — charge for defiant action, not original
                defiance_free_actions = ["retreat", "break_square"]
                if defiant_action not in defiance_free_actions:
                    world.use_action(defiant_action)

                # Execute defiant action
                pre_battle_strength = marshal.strength
                defiant_command = {"action": defiant_action, "marshal": marshal_name}

                if defiant_action == "bombardment":
                    # m2 fix: call _execute_bombardment directly with the specific
                    # defiant marshal — auto-assign would pick from ALL artillery.
                    nearest = world.find_nearest_enemy(marshal.location)
                    if nearest and nearest[1] <= 2:
                        defiant_execution = self._execute_bombardment(
                            marshal, nearest[0], world, game_state
                        )
                    else:
                        defiant_action = "wait"
                        defiant_execution = self._execute_wait(marshal, world, game_state)
                elif defiant_action == "attack":
                    nearest = world.find_nearest_enemy(marshal.location)
                    if nearest:
                        defiant_execution = self._execute_attack(marshal, nearest[0].name, world, game_state)
                    else:
                        defiant_action = "wait"
                        defiant_execution = self._execute_wait(marshal, world, game_state)
                    if not defiant_execution.get("success"):
                        defiant_action = "wait"
                        defiant_execution = self._execute_wait(marshal, world, game_state)
                elif defiant_action == "fortify":
                    defiant_execution = self._execute_fortify(
                        {"marshal": marshal_name}, game_state
                    )
                    # C1.2 fix: fortify may fail (AGGRESSIVE stance, engaged, etc.)
                    if not defiant_execution.get("success"):
                        defiant_action = "wait"
                        defiant_execution = self._execute_wait(marshal, world, game_state)
                else:  # wait / sulk
                    defiant_execution = self._execute_wait(marshal, world, game_state)

                # Evaluate outcome
                battle_result = defiant_execution.get("battle_result") or defiant_execution.get("bombardment_result")
                outcome = defiance_succeeded(marshal, defiant_action, battle_result, pre_battle_strength)

                # Apply outcome table
                outcome_result = apply_defiance_outcome(marshal, outcome, world)

                # Redemption check: insist penalty or defiance outcome may push trust <= 20
                _redemption_event = response_result.get("redemption_event")
                if not _redemption_event:
                    _redemption_event = world.disobedience_system.check_redemption_threshold(marshal, world)

                # M3 fix: register defensive vindication for deferred evaluation
                # (fortify defiance can't be assessed immediately — needs enemy attack)
                if defiant_action == "fortify" and defiant_execution.get("success"):
                    world.vindication_tracker.pending_defensive_vindication[marshal_name] = {
                        "turn": world.current_turn,
                        "source": "defiance",
                    }

                # Fire notification
                world.notifications.add(create_notification(
                    MARSHAL_DEFIED_ORDER,
                    NotificationPriority.HIGH,
                    f"{marshal_name} defied your order!",
                    f"{marshal_name} defied your order to {_action_display_name(original_action)} "
                    f"and chose to {_action_display_name(defiant_action)} instead.",
                    world.current_turn,
                ))

                # Log campaign event
                world.log_event({
                    "type": "defiance",
                    "marshal": marshal_name,
                    "original_action": original_action,
                    "defiance_action": defiant_action,
                    "outcome": outcome_result["outcome_type"],
                    "turn": world.current_turn,
                })

                # Build response
                action_desc = _action_display_name(defiant_action)
                defiance_message = (
                    f"Despite your insistence, {marshal_name} {action_desc} instead!\n\n"
                    f"{outcome_result['berthier_text']}"
                )
                if defiant_execution.get("message"):
                    defiance_message += f"\n\n{defiant_execution['message']}"

                result = {
                    "success": True,
                    "message": defiance_message,
                    "objection_resolved": True,
                    "choice": choice,
                    "disobeyed": False,
                    "defiance": True,
                    "defiance_action": defiant_action,
                    "defiance_outcome": outcome_result["outcome_type"],
                    "trust_change": response_result.get("trust_change", 0) + outcome_result["trust_change"],
                    "authority_change": response_result.get("authority_change", 0) + outcome_result["authority_change"],
                    "berthier_text": outcome_result["berthier_text"],
                    "events": defiant_execution.get("events", []),
                    "action_info": defiant_execution.get("action_info", {"remaining": world.actions_remaining}),
                    "action_summary": world.get_action_summary(),
                    "new_state": game_state,
                }
                if defiant_execution.get("battle_report"):
                    result["battle_report"] = defiant_execution["battle_report"]
                if authority_event:
                    result["authority_event"] = authority_event
                if _redemption_event:
                    result["redemption_event"] = _redemption_event
                    result["state"] = "awaiting_redemption_choice"
                return result

            else:
                # ═══ DEFIANCE ROLL FAILS — marshal obeys reluctantly ═══
                print(f"  [DEFIANCE] Roll failed for {marshal_name} (roll={defiance_roll:.2f} >= chance={defiance_chance:.2f})")
                from backend.commands.defiance import apply_defiance_outcome
                outcome_result = apply_defiance_outcome(marshal, "failed_roll", world)

                # Add failed-roll trust/authority changes to response
                response_result["trust_change"] = response_result.get("trust_change", 0) + outcome_result["trust_change"]
                response_result["message"] = (
                    response_result.get("message", "") + "\n\n" + outcome_result["berthier_text"]
                )

        # ════════════════════════════════════════════════════════════
        # BUG FIX #1: Check for DISOBEY - execute ALTERNATIVE instead
        # ════════════════════════════════════════════════════════════
        if response_result.get("disobeyed"):
            print("  [DISOBEY] Marshal executes their alternative instead!")

            # Marshal does what THEY wanted, not what player ordered
            disobey_order = alternative if alternative else None

            if disobey_order:
                # Execute the marshal's preferred action
                parsed_command = {
                    "success": True,
                    "command": disobey_order
                }
                execution_result = self._execute_post_objection(parsed_command, game_state, marshal_name)

                # Build message showing what marshal did instead
                disobey_msg = response_result["message"]
                action_desc = f"{disobey_order.get('action', 'act')} {disobey_order.get('target', '')}"
                final_message = f"{disobey_msg}\n\n{marshal_name} instead chooses to {action_desc}."

                if execution_result.get("success"):
                    final_message += f"\n\n{execution_result.get('message', '')}"

                result = {
                    "success": True,
                    "message": final_message,
                    "objection_resolved": True,
                    "choice": choice,
                    "disobeyed": True,
                    "executed_alternative": True,
                    "trust_change": response_result.get("trust_change", 0),
                    "authority_change": response_result.get("authority_change", 0),
                    "events": execution_result.get("events", []),
                    "action_info": execution_result.get("action_info", {"remaining": world.actions_remaining}),
                    "action_summary": world.get_action_summary(),
                    "new_state": game_state
                }
                if execution_result.get("battle_report"):
                    result["battle_report"] = execution_result["battle_report"]
            else:
                # No alternative available - marshal simply refuses
                print("  [WARN] No alternative available - marshal refuses entirely")
                result = {
                    "success": True,
                    "message": response_result["message"] + f"\n\n{marshal_name} stands firm and takes no action.",
                    "objection_resolved": True,
                    "choice": choice,
                    "disobeyed": True,
                    "executed_alternative": False,
                    "trust_change": response_result.get("trust_change", 0),
                    "authority_change": response_result.get("authority_change", 0),
                    "events": [],
                    "action_info": {"remaining": world.actions_remaining},
                    "action_summary": world.get_action_summary(),
                    "new_state": game_state
                }

            # Check for redemption event even on disobey
            if response_result.get("redemption_event"):
                result["redemption_event"] = response_result["redemption_event"]
                result["state"] = "awaiting_redemption_choice"
                print("  [ALERT] REDEMPTION EVENT attached to disobey response")
            if authority_event:
                result["authority_event"] = authority_event

            return result

        # ════════════════════════════════════════════════════════════
        # V2b: DEFENSIVE VINDICATION CREATION
        # When player trusts + marshal's alternative was defend/fortify/hold
        # ════════════════════════════════════════════════════════════
        if choice == "trust" and alternative:
            alt_action = alternative.get("action", "")
            if alt_action in ("defend", "fortify", "hold") and marshal:
                world.vindication_tracker.pending_defensive_vindication[marshal_name] = {
                    "turn": world.current_turn
                }

        # ════════════════════════════════════════════════════════════
        # BUG FIX #2: Check for REDEMPTION EVENT - return with event
        # ════════════════════════════════════════════════════════════
        if response_result.get("redemption_event"):
            print("  [ALERT] REDEMPTION EVENT - returning before order execution")
            # Still execute the order, but include redemption event in response
            # (Trust dropped to critical AFTER the order would execute)

        # Get the order to execute (original or alternative)
        if choice == "trust" and alternative:
            # Execute the marshal's suggested alternative
            order_to_execute = alternative
            # Ensure marshal name is in the alternative dict (generated alternatives
            # may omit it, but handlers like _execute_fortify need it)
            if "marshal" not in order_to_execute or not order_to_execute["marshal"]:
                order_to_execute["marshal"] = marshal_name
            execute_msg = f"{marshal_name} executes their alternative plan."
        elif choice == "compromise" and compromise:
            # Execute compromise action
            order_to_execute = compromise
            if "marshal" not in order_to_execute or not order_to_execute["marshal"]:
                order_to_execute["marshal"] = marshal_name
            execute_msg = f"{marshal_name} executes the compromise plan."
        else:
            # Execute original order (insist or trust with no alternative)
            order_to_execute = objection["original_order"]
            execute_msg = f"{marshal_name} follows your orders."

        # Build result message
        result_message = f"{response_result['message']}\n\n{execute_msg}"

        # Now execute the order
        # Create a parsed command structure from the order
        parsed_command = {
            "success": True,
            "command": order_to_execute
        }

        # Execute the command (this will bypass objection check since we just resolved it)
        # Temporarily mark this as a post-objection execution
        execution_result = self._execute_post_objection(parsed_command, game_state, marshal_name)

        # Combine messages
        if execution_result.get("success"):
            final_message = f"{result_message}\n\n{execution_result.get('message', '')}"
        else:
            final_message = f"{result_message}\n\nExecution failed: {execution_result.get('message', 'Unknown error')}"

        result = {
            "success": execution_result.get("success", False),
            "message": final_message,
            "objection_resolved": True,
            "choice": choice,
            "disobeyed": False,
            "trust_change": response_result.get("trust_change", 0),
            "authority_change": response_result.get("authority_change", 0),
            "events": execution_result.get("events", []),
            "action_info": execution_result.get("action_info", {}),
            "action_summary": world.get_action_summary(),
            "new_state": game_state
        }
        if execution_result.get("battle_report"):
            result["battle_report"] = execution_result["battle_report"]

        # Add redemption event if triggered (trust dropped to critical after executing)
        if response_result.get("redemption_event"):
            result["redemption_event"] = response_result["redemption_event"]
            result["state"] = "awaiting_redemption_choice"
            print("  [ALERT] REDEMPTION EVENT attached to response")
        if authority_event:
            result["authority_event"] = authority_event

        return result

    def _execute_post_objection(self, parsed_command: Dict, game_state: Dict, marshal_name: str) -> Dict:
        """
        Execute a command after objection has been resolved.
        Bypasses the objection check since we just handled it.

        Args:
            parsed_command: The parsed command to execute
            game_state: Current game state
            marshal_name: Name of the marshal executing

        Returns:
            Execution result dict
        """
        world: WorldState = game_state.get("world")
        command = parsed_command.get("command", {})
        action = command.get("action", "unknown")

        # Check action economy
        # FIX: Added "retreat" - must match main execute() free_actions list
        # R72: Vassal commands are free (DP/gold cost, not military AP)
        free_actions = ["status", "help", "end_turn", "unknown", "retreat", "debug", "economy", "treasury", "finances", "break_square", "diplomatic_proposal", "diplomatic_mission", "diplomatic_feasibility", "diplomatic_advisory", "diplomatic_error", "diplomatic_break", "diplomatic_downgrade", "diplomatic_declare_war", "diplomatic_ultimatum", "invest_vassal", "change_autonomy", "make_vassal", "release_vassal"]
        action_costs_point = action not in free_actions

        if action_costs_point:
            is_admin = action in ADMIN_ACTIONS
            if is_admin:
                if world.admin_actions_remaining <= 0:
                    return {
                        "success": False,
                        "message": "No administrative actions remaining this turn!"
                    }
            elif world.actions_remaining <= 0:
                return {
                    "success": False,
                    "message": "No actions remaining this turn!"
                }

        # Route to appropriate handler based on action type
        command_type = command.get("type", "specific")

        # Strategic commands route through strategic executor
        if command.get("is_strategic") and command.get("strategic_type"):
            parsed_command["is_strategic"] = True
            parsed_command["strategic_type"] = command["strategic_type"]
            parsed_command["marshal"] = marshal_name
            strategic_result = self._execute_strategic_command(parsed_command, command, game_state)
            if strategic_result is not None:
                result = strategic_result
                # Consume action if successful — MUST use variable_action_cost!
                # Strategic commands cost 2 AP (1 for literal). Do NOT call
                # use_action() once — that only deducts 1 AP. This was a bug
                # where post-objection HOLD always cost 1 AP instead of 2.
                #
                # CRITICAL: pending_objection means player hasn't decided yet —
                # AP is consumed when they respond, NOT when objection triggers!
                action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
                if result.get("success", False) and action_costs_point and not result.get("pending_objection"):
                    variable_cost = result.get("variable_action_cost", 1)
                    for _ in range(variable_cost):
                        action_result = world.use_action(action)
                # For pending objections, cost is 0 (not consumed yet)
                # Actual cost depends on player choice (proceed=2, preferred=1, compromise=2)
                if result.get("pending_objection"):
                    result["action_info"] = {
                        "cost": 0,  # No AP consumed yet
                        "remaining": world.actions_remaining,
                        "turn_advanced": False,
                        "new_turn": None
                    }
                else:
                    result["action_info"] = {
                        "cost": result.get("variable_action_cost", 1),
                        "remaining": world.actions_remaining,
                        "turn_advanced": action_result.get("turn_advanced", False),
                        "new_turn": action_result.get("new_turn")
                    }
                return result

        if action == "attack":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_attack(marshal, command.get("target"), world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "defend":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_defend(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "move":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_move(marshal, command.get("target"), world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "scout":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_scout(marshal, command.get("target"), world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "recruit":
            result = self._execute_recruit(command, game_state)
        elif action == "build":
            result = self._execute_build(command, game_state)
        elif action == "repair":
            result = self._execute_repair(command, game_state)
        # ════════════════════════════════════════════════════════════
        # TACTICAL ACTIONS (Phase 2.6) - Must work via objection Insist
        # ════════════════════════════════════════════════════════════
        elif action == "fortify":
            result = self._execute_fortify(command, game_state)
        elif action == "drill":
            result = self._execute_drill(command, game_state)
        elif action == "unfortify":
            result = self._execute_unfortify(command, game_state)
        elif action == "form_square":
            result = self._execute_form_square(command, game_state)
        elif action == "break_square":
            result = self._execute_break_square(command, game_state)
        elif action == "retreat":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_retreat_action(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        # BUG-005 FIX: Handle stance_change in post-objection execution
        elif action == "stance_change":
            result = self._execute_stance_change(command, game_state)
        elif action == "hold":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_hold(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "wait":
            # _execute_wait takes (marshal, world, game_state) — not (command, game_state)
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_wait(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "bombardment":
            # GAP fix: bombardment handler (unreachable today, but prevents silent
            # "Unknown action" if future alternatives/compromises produce it)
            marshal = world.get_marshal(marshal_name)
            if marshal:
                nearest = world.find_nearest_enemy(marshal.location)
                if nearest and nearest[1] <= 2:
                    result = self._execute_bombardment(marshal, nearest[0], world, game_state)
                else:
                    result = {"success": False, "message": f"{marshal_name} has no valid bombardment target in range."}
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "garrison":
            # GAP fix: garrison handler (unreachable today, but prevents silent
            # "Unknown action" if future alternatives/compromises produce it)
            result = self._execute_garrison(command, game_state)
        else:
            result = {"success": False, "message": f"Unknown action: {action}"}

        # Consume action if successful
        # BUG FIX: Must handle variable_action_cost (stance_change costs 0-2 AP).
        # Previously called world.use_action() once which only deducts 1 AP.
        # N2 fix: Admin actions (recruit, build, repair) use admin AP pool.
        is_admin = action in {"recruit", "build", "repair"}
        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
        if result.get("success", False) and action_costs_point:
            if is_admin:
                world.use_admin_action(1)
                action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 1}
            else:
                variable_cost = result.get("variable_action_cost")
                if variable_cost is not None:
                    if variable_cost > 0:
                        if world.actions_remaining < variable_cost:
                            return {
                                "success": False,
                                "message": f"Not enough actions! Need {variable_cost}, have {world.actions_remaining}.",
                                "actions_remaining": int(world.actions_remaining),
                            }
                        for _ in range(variable_cost):
                            action_result = world.use_action(action)
                    else:
                        # Free transition (e.g. returning to neutral)
                        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
                else:
                    action_result = world.use_action(action)

        # Add action info to result
        result["action_info"] = {
            "cost": action_result.get("action_cost", 0),
            "remaining": world.actions_remaining,
            "turn_advanced": action_result.get("turn_advanced", False),
            "new_turn": action_result.get("new_turn")
        }

        # ════════════════════════════════════════════════════════════
        # TACTICAL EVENTS: Add to message when turn advances
        # ════════════════════════════════════════════════════════════
        if action_result.get("turn_advanced", False):
            tactical_events = world.get_last_tactical_events()
            if tactical_events:
                tactical_messages = []
                for event in tactical_events:
                    event_msg = event.get("message", "")
                    if event_msg:
                        tactical_messages.append(event_msg)

                if tactical_messages:
                    result["message"] = result.get("message", "") + "\n\n--- TURN EVENTS ---\n" + "\n".join(tactical_messages)
                    result["tactical_events"] = tactical_events

        return result

    def resolve_battle_vindication(self, marshal_name: str, result: str, game_state: Dict) -> Optional[Dict]:
        """
        Call vindication tracker after a battle to update trust/authority.

        Args:
            marshal_name: Name of marshal who fought
            result: 'victory', 'defeat', or 'draw'
            game_state: Current game state

        Returns:
            Vindication result dict or None if no pending vindication
        """
        world: WorldState = game_state.get("world")

        if not world:
            return None

        return world.vindication_tracker.resolve_battle(
            marshal_name=marshal_name,
            result=result,
            game_state=world
        )

    # ════════════════════════════════════════════════════════════
    # VASSAL COMMANDS (Phase 8 Session 5)
    # ════════════════════════════════════════════════════════════

    def _execute_invest_vassal(self, command: Dict, game_state: Dict) -> Dict:
        """Invest in a vassal: 1 DP + 200g → +10 loyalty."""
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        target = (command.get("target") or "").strip()
        if not target:
            return {"success": False, "message": "Specify which vassal to invest in."}

        from backend.game_logic.vassal import invest_in_vassal
        result = invest_in_vassal(world, target)
        if result.get("success"):
            result["new_state"] = game_state
        return result

    def _execute_change_autonomy(self, command: Dict, game_state: Dict) -> Dict:
        """Change vassal autonomy level."""
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        target = (command.get("target") or "").strip()
        if not target:
            return {"success": False, "message": "Specify which vassal."}

        # Parse autonomy level from command
        from backend.game_logic.vassal import (
            AUTONOMY_PUPPET, AUTONOMY_SATELLITE, AUTONOMY_AUTONOMOUS,
            change_vassal_autonomy
        )
        raw_text = (command.get("raw_input") or command.get("original_command") or "").lower()
        if "puppet" in raw_text:
            new_level = AUTONOMY_PUPPET
        elif "satellite" in raw_text:
            new_level = AUTONOMY_SATELLITE
        elif "autonomous" in raw_text:
            new_level = AUTONOMY_AUTONOMOUS
        elif "increase" in raw_text:
            # Direction-based: increase by one level
            vassals = getattr(world, 'vassals', {})
            v = vassals.get(target, {})
            current = v.get("autonomy", AUTONOMY_SATELLITE)
            if current >= AUTONOMY_AUTONOMOUS:
                return {"success": False, "message": f"{target} is already at maximum autonomy."}
            new_level = current + 1
        elif "decrease" in raw_text:
            # Direction-based: decrease by one level
            vassals = getattr(world, 'vassals', {})
            v = vassals.get(target, {})
            current = v.get("autonomy", AUTONOMY_SATELLITE)
            if current <= AUTONOMY_PUPPET:
                return {"success": False, "message": f"{target} is already at minimum autonomy."}
            new_level = current - 1
        else:
            return {
                "success": False,
                "message": "Specify autonomy level: puppet, satellite, or autonomous."
            }

        result = change_vassal_autonomy(world, target, new_level)
        if result.get("success"):
            result["new_state"] = game_state
        return result

    def _execute_make_vassal(self, command: Dict, game_state: Dict) -> Dict:
        """Create a vassal from treaty or conquest path."""
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        target = (command.get("target") or "").strip()
        if not target:
            return {"success": False, "message": "Specify which nation to vassalize."}

        player = getattr(world, 'player_nation', 'France')

        from backend.game_logic.vassal import (
            create_vassal_treaty, create_vassal_conquest,
            assimilate_vassal_marshals, AUTONOMY_PUPPET, AUTONOMY_SATELLITE
        )

        # Determine path: if at WAR → conquest, if OPEN_BORDERS+ → treaty
        current_state = world.get_diplomatic_state(player, target)
        if current_state == "WAR":
            result = create_vassal_conquest(world, player, target)
        else:
            result = create_vassal_treaty(world, player, target)

        if result.get("success"):
            # Assimilate marshals for PUPPET/SATELLITE
            vassal_state = world.vassals.get(target, {})
            autonomy = vassal_state.get("autonomy", AUTONOMY_SATELLITE)
            if autonomy in (AUTONOMY_PUPPET, AUTONOMY_SATELLITE):
                assimilated = assimilate_vassal_marshals(world, target)
                if assimilated:
                    result["message"] += (
                        f" Marshals assimilated: {', '.join(assimilated)}."
                    )
            result["new_state"] = game_state

            # R23: Marshal trust reactions for vassal creation
            self._apply_diplomatic_trust_reactions(world, "vassal_created", target)

        return result

    def _execute_release_vassal(self, command: Dict, game_state: Dict) -> Dict:
        """Release a vassal nation. Costs 1 DP."""
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        target = (command.get("target") or "").strip()
        if not target:
            return {"success": False, "message": "Specify which vassal to release."}

        vassals = getattr(world, 'vassals', {})
        if target not in vassals:
            return {"success": False, "message": f"{target} is not a vassal."}

        if world.diplomatic_points < 1:
            return {"success": False, "message": "Insufficient Diplomatic Points. Releasing a vassal costs 1 DP."}

        from backend.game_logic.vassal import release_vassal
        result = release_vassal(world, target)
        if result.get("success"):
            world.diplomatic_points -= 1
            result["new_state"] = game_state
        return result

    # ========================================
    # CHEAT COMMANDS (Phase 8 Session 8A)
    # ========================================

    def _execute_cheat(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute cheat commands for diplomatic system testing.

        Gated behind mock/debug mode.

        Supported: set_threat, set_relation, give_dp, trigger_coalition,
        set_war_exhaustion, set_diplo_state, create_vassal,
        set_vassal_loyalty, set_talleyrand_trust, queue_ai_proposal,
        clear_dialogue
        """
        import os
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        # Guard: only available in mock/debug mode
        llm_mode = os.getenv("LLM_MODE", "mock")
        debug_mode = game_state.get("debug_mode", False)
        if llm_mode != "mock" and not debug_mode:
            return {
                "success": False,
                "message": "Cheat commands only available in mock/debug mode.",
            }

        cheat_type = (command.get("cheat_type") or command.get("target") or "").strip()
        cheat_args = command.get("cheat_args", [])

        if not cheat_type:
            return {"success": False, "message": "Usage: cheat <type> <args>"}

        # ── set_threat <value> ──
        if cheat_type == "set_threat":
            if not cheat_args:
                return {"success": False, "message": "Usage: cheat set_threat <value>"}
            value = max(0, min(100, int(cheat_args[0])))
            old = world.threat_level
            world.threat_level = value
            return {"success": True, "message": f"Threat level: {old} → {value}"}

        # ── set_relation <nation> <value> ──
        if cheat_type == "set_relation":
            if len(cheat_args) < 2:
                return {"success": False, "message": "Usage: cheat set_relation <nation> <value>"}
            nation = cheat_args[0]
            value = max(-100, min(100, int(cheat_args[1])))
            player = world.player_nation
            key = world._make_diplo_key(player, nation)
            old = world.nation_relations.get(key, 0)
            world.nation_relations[key] = value
            return {"success": True, "message": f"Relation France↔{nation}: {old} → {value}"}

        # ── give_dp <amount> ──
        if cheat_type == "give_dp":
            if not cheat_args:
                return {"success": False, "message": "Usage: cheat give_dp <amount>"}
            amount = int(cheat_args[0])
            max_dp = int(getattr(world, 'max_diplomatic_points', 5))
            old = getattr(world, 'diplomatic_points', 0)
            world.diplomatic_points = min(old + amount, max_dp)
            return {"success": True, "message": f"DP: {old} → {world.diplomatic_points} (max {max_dp})"}

        # ── trigger_coalition ──
        if cheat_type == "trigger_coalition":
            from backend.game_logic.coalition import get_qualifying_nations, form_coalition
            qualifying = get_qualifying_nations(world)
            if not qualifying:
                return {"success": False, "message": "No qualifying nations for coalition."}
            result = form_coalition(qualifying, world)
            return result

        # ── set_war_exhaustion <nation> <value> ──
        if cheat_type == "set_war_exhaustion":
            if len(cheat_args) < 2:
                return {"success": False, "message": "Usage: cheat set_war_exhaustion <nation> <value>"}
            nation = cheat_args[0]
            value = max(0, min(200, int(cheat_args[1])))
            old = world.war_exhaustion.get(nation, 0)
            world.war_exhaustion[nation] = value
            return {"success": True, "message": f"War exhaustion {nation}: {old} → {value}"}

        # ── set_diplo_state <nation> <state> ──
        if cheat_type == "set_diplo_state":
            if len(cheat_args) < 2:
                return {"success": False, "message": "Usage: cheat set_diplo_state <nation> <state>"}
            nation = cheat_args[0]
            state = cheat_args[1].upper()
            player = world.player_nation
            key = world._make_diplo_key(player, nation)
            old = world.diplomatic_states.get(key, "PEACE")
            world.diplomatic_states[key] = state
            # Track war start turn for war weariness calculation
            if state == "WAR" and key not in world.war_start_turns:
                world.war_start_turns[key] = int(world.current_turn)
            return {"success": True, "message": f"Diplomatic state France↔{nation}: {old} → {state}"}

        # ── create_vassal <nation> ──
        if cheat_type == "create_vassal":
            if not cheat_args:
                return {"success": False, "message": "Usage: cheat create_vassal <nation>"}
            nation = cheat_args[0]
            from backend.game_logic.vassal import create_vassal_treaty
            result = create_vassal_treaty(world, "France", nation, 0)
            return result

        # ── set_vassal_loyalty <nation> <value> ──
        if cheat_type == "set_vassal_loyalty":
            if len(cheat_args) < 2:
                return {"success": False, "message": "Usage: cheat set_vassal_loyalty <nation> <value>"}
            nation = cheat_args[0]
            if nation not in world.vassals:
                return {"success": False, "message": f"{nation} is not a vassal."}
            value = max(0, min(100, int(cheat_args[1])))
            old = world.vassals[nation]["loyalty"]
            world.vassals[nation]["loyalty"] = value
            return {"success": True, "message": f"Vassal loyalty {nation}: {old} → {value}"}

        # ── set_talleyrand_trust <value> ──
        if cheat_type == "set_talleyrand_trust":
            if not cheat_args:
                return {"success": False, "message": "Usage: cheat set_talleyrand_trust <value>"}
            diplomats = getattr(world, 'diplomats', {})
            talleyrand = diplomats.get("France")
            if not talleyrand:
                return {"success": False, "message": "No Talleyrand found."}
            old = talleyrand.trust
            talleyrand.trust = int(cheat_args[0])
            return {"success": True, "message": f"Talleyrand trust: {old} → {talleyrand.trust}"}

        # ── queue_ai_proposal <nation> <type> ──
        if cheat_type == "queue_ai_proposal":
            if len(cheat_args) < 2:
                return {"success": False, "message": "Usage: cheat queue_ai_proposal <nation> <type>"}
            nation = cheat_args[0]
            proposal_type = cheat_args[1]
            player = world.player_nation
            proposal = {
                "source": nation,
                "proposal_type": proposal_type,
                "priority": 1,
                "terms": {
                    "type": proposal_type,
                    "proposer_nation": nation,
                    "target_nation": player,
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                },
                "talleyrand_assessment": f"A {proposal_type} proposal from {nation} (debug-generated).",
                "turn_generated": int(world.current_turn),
            }
            if not hasattr(world, 'diplomatic_queue'):
                world.diplomatic_queue = []
            world.diplomatic_queue.append(proposal)
            return {
                "success": True,
                "message": f"Queued {_proposal_display_name(proposal_type)} proposal from {nation} to France.",
            }

        # ── clear_dialogue (Audit fix C-2) ──
        if cheat_type == "clear_dialogue":
            had_dialogue = world.pending_diplomatic_dialogue is not None
            world.pending_diplomatic_dialogue = None
            world.incoming_proposal_popup = None
            if had_dialogue:
                return {"success": True, "message": "Cleared stuck diplomatic dialogue."}
            return {"success": True, "message": "No dialogue was pending."}

        return {"success": False, "message": f"Unknown cheat type: {cheat_type}"}