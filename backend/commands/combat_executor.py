"""
Combat Executor for Project Sovereign
Handles all combat-related execution: attack, charge, bombardment, garrison.

Extracted from executor.py in R10A (Architecture Refactoring Session 10A).
"""
from typing import Dict, Optional
from backend.models.world_state import WorldState
from backend.models.region import CHARGE_BLOCKED_TERRAIN, TERRAIN_DEFENSE_BONUS
from backend.game_logic.combat import FORCED_RETREAT_THRESHOLD


def friendly_fire_refusal(world, marshal, target_nation: str) -> Optional[Dict]:
    """A blocked-attack result when the target is our OWN nation, an ally, or a
    vassal — else None (the target is a valid enemy / attackable neutral, so the
    caller proceeds, declaring war on a neutral as before).

    Closes the friendly-fire hole (playtest finding): ordering an attack on an
    allied marshal used to reach the war-declaration seam and stage a war
    against our own ally. Shared by the executor pre-validation (before the
    marshal's objection can fire) and the combat war-declaration backstop.
    """
    if world.can_attack_nation(marshal.nation, target_nation):
        return None
    if marshal.nation == target_nation:
        message = f"{marshal.name} cannot attack our own forces, Sire."
    else:
        relation = ("vassal"
                    if world.get_diplomatic_state(marshal.nation, target_nation) == "VASSAL"
                    else "ally")
        message = (f"{marshal.name} cannot attack {target_nation} — they are our "
                   f"{relation}, Sire, and we are not at war with them.")
    return {"success": False, "message": message}


class CombatExecutor:
    """Handles all combat-related execution: attack, charge, bombardment, garrison."""

    def __init__(self, parent_executor):
        """Initialize with reference to parent CommandExecutor for shared state access."""
        self._executor = parent_executor
        self.combat_resolver = parent_executor.combat_resolver

    # ════════════════════════════════════════════════════════════════════════════════
    # MULTI-MARSHAL COORDINATION (Phase 7, Session 57+)
    # Combined arms detection, coordination bonuses, dedicated support, adjacent support.
    # Extracted from executor.py in R10B (Architecture Refactoring Session 10B).
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
            and world.is_at_war(nation, m.nation)
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

    def _calculate_overwatch(self, attacker, atk_participants, defender_region_name: str,
                             world: WorldState, defender_name: str = None) -> int:
        """Count enemy artillery in defender's region, apply overwatch penalty to all attackers.

        Session 68: Artillery Overwatch — enemy artillery passively debuffs attackers
        by -3% per gun (capped at 3 guns = -9% max).

        V2-24: defender_name excludes the defending marshal from counting as its own
        overwatch (a marshal can't provide overwatch to itself when it IS the target).

        Sets transient `overwatch_penalty` on each attacking participant.
        Returns the count of eligible overwatch artillery (for reporting).
        """
        enemy_artillery_count = 0
        overwatch_artillery_names = []
        for m in world.marshals.values():
            if (m.location == defender_region_name
                    and m.nation != attacker.nation
                    and world.is_at_war(attacker.nation, m.nation)
                    and getattr(m, 'artillery', False)
                    and m.strength > 0
                    and not getattr(m, 'broken', False)
                    and not getattr(m, 'retreated_this_turn', False)
                    and getattr(m, 'retreat_recovery', 0) == 0
                    and not getattr(m, 'moved_this_turn', False)
                    and (defender_name is None or m.name != defender_name)):
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

    @staticmethod
    def _rewrite_primary_casualties(description, atk_name, atk_raw, atk_share,
                                    def_name, def_raw, def_share):
        """Rewrite a coordinated-battle description's casualty numbers from the
        whole-corps raw total to each primary marshal's actual distributed share.

        resolve_battle formats the casualty line before the caller distributes
        casualties across participants, so it names the primary marshal with the
        entire corps' losses. This corrects the printed line for both the
        "Casualties: <name> <n>" (tactical/stalemate) and "suffered <n> casualties"
        (decisive-victory) templates. Reinforcers' losses are surfaced separately
        via reinforcement_messages, so no figure is double-counted.
        """
        if not description:
            return description
        for name, raw, share in ((atk_name, atk_raw, atk_share),
                                 (def_name, def_raw, def_share)):
            if raw == share:
                continue
            description = description.replace(
                f"{name} {raw:,}", f"{name} {share:,}")
            description = description.replace(
                f"suffered {raw:,} casualties", f"suffered {share:,} casualties")
        return description

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
        # PL-2: Dedup across turns — only one counter-punch notification per marshal at a time
        if battle_result.get("counter_punch_earned"):
            if getattr(defender, 'nation', '') == player_nation:
                already_has = any(
                    n.get("type") == COUNTER_PUNCH_EARNED
                    and n.get("details", {}).get("marshal") == defender.name
                    for n in world.notifications.get_pending()
                )
                if not already_has:
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

    def _post_combat_pipeline(self, ctx: dict, world: 'WorldState') -> dict:
        """
        Centralized post-combat state recording and tracking.

        Called by all 5 combat paths after path-specific resolution.
        Ensures every combat path runs every recording step, preventing
        the "path X missing step Y" bugs found in every audit.

        Args:
            ctx: Combat context with keys:
                attacker (Marshal): attacking marshal
                defender (Marshal or None): defending marshal (None for garrison)
                defender_nation (str): nation of the defender
                battle_region (str): region name where battle occurred
                outcome (str): e.g. 'attacker_victory', 'defender_victory'
                attacker_won (bool)
                defender_won (bool)
                attacker_casualties (int)
                defender_casualties (int)
                pre_battle_attacker_strength (int)
                pre_battle_defender_strength (int)
                battle_result (dict or None): from resolve_battle()
                conquered (bool): whether territory was captured

                # Path flags
                is_bombardment (bool): ranged bombardment (limited recording)
                is_garrison (bool): garrison assault (custom authority)
                is_glorious_charge (bool): cavalry charge
                is_auto_bombardment_kill (bool): defender killed by prep fire

                # Optional
                attacker_artillery (list): for relationship processing
                defender_artillery (list): for relationship processing
                skip_log_battle_event (bool): caller handles its own event log
                skip_idle_reset (bool): caller already reset idle
                skip_exhaustion (bool): caller handles exhaustion
                skip_cannon_fire_record (bool): caller already recorded
                skip_war_damage (bool): caller already applied war damage
                skip_intel_update (bool): caller already updated intel
                skip_coordination_clear (bool): caller already cleared

        Returns:
            dict with:
                vindication_msg (str): vindication message for display
                relationship_changes (list): relationship change records
        """
        attacker = ctx['attacker']
        defender = ctx.get('defender')
        defender_nation = ctx.get('defender_nation', defender.nation if defender else '')
        battle_region = ctx['battle_region']
        outcome = ctx.get('outcome', '')
        attacker_won = ctx.get('attacker_won', False)
        defender_won = ctx.get('defender_won', False)
        atk_casualties = ctx.get('attacker_casualties', 0)
        def_casualties = ctx.get('defender_casualties', 0)
        pre_atk = ctx.get('pre_battle_attacker_strength', 0)
        pre_def = ctx.get('pre_battle_defender_strength', 0)
        battle_result = ctx.get('battle_result')
        conquered = ctx.get('conquered', False)

        is_bombardment = ctx.get('is_bombardment', False)
        is_garrison = ctx.get('is_garrison', False)
        is_auto_kill = ctx.get('is_auto_bombardment_kill', False)

        pipeline_out = {
            'vindication_msg': '',
            'relationship_changes': [],
        }

        # ── 1. Clear coordination fields ──
        if not ctx.get('skip_coordination_clear'):
            involved = {attacker.location, battle_region}
            if defender and getattr(defender, 'strength', 0) > 0:
                involved.add(defender.location)
            self._clear_coordination_fields(involved, world)

        # ── 2. Log battle event ──
        if (battle_result and not is_bombardment and not is_garrison
                and not is_auto_kill and not ctx.get('skip_log_battle_event')):
            self._log_battle_event(battle_result, battle_region, world)

        # ── 3. Combat notifications ──
        if (battle_result and not is_bombardment and not is_garrison
                and not is_auto_kill and not ctx.get('skip_combat_notifications')):
            if defender:
                self._process_combat_notifications(battle_result, attacker, defender, world)

        # ── 4. Fog of War intel update ──
        if not ctx.get('skip_intel_update'):
            world.update_intel_from_battle(battle_region, world.current_turn)

        # ── 5. War damage to region ──
        if not is_bombardment and not ctx.get('skip_war_damage'):
            self._apply_battle_effects_to_region(
                battle_region, pre_atk, pre_def, world)

        # ── 6. Idle reset ──
        if not ctx.get('skip_idle_reset'):
            attacker.idle_turns = 0
            attacker._acted_this_turn = True

        # ── 7. Record battle for cannon fire detection ──
        if not ctx.get('skip_cannon_fire_record'):
            def_name = defender.name if defender else f"{battle_region}_garrison"
            world.record_battle(battle_region, attacker.name, def_name, outcome)

        # ── 8. Record battle for diplomacy war score ──
        if not ctx.get('skip_diplo_record'):
            from backend.game_logic.diplomacy import record_battle as record_diplo_battle
            from backend.game_logic.war_contribution import detect_battle_theater
            diplo_winner = None
            if attacker_won:
                diplo_winner = attacker.nation
            elif defender_won:
                diplo_winner = defender_nation
            if diplo_winner:
                # Imperial Settlement B2: theater-aware emitter — pass one-hop
                # adjacency participants + theater strength so allies near the
                # battle receive battle-bucket credit (spec §9.4 line 717).
                theater = detect_battle_theater(
                    world,
                    battle_region=battle_region,
                    attacker_nation=attacker.nation,
                    defender_nation=defender_nation,
                    attacker_marshal_name=getattr(attacker, "name", None),
                    defender_marshal_name=getattr(defender, "name", None),
                    attacker_pre_battle_strength=int(pre_atk),
                    defender_pre_battle_strength=int(pre_def),
                )
                record_diplo_battle(
                    world,
                    attacker_nation=attacker.nation,
                    defender_nation=defender_nation,
                    winner_nation=diplo_winner,
                    attacker_casualties=int(atk_casualties),
                    defender_casualties=int(def_casualties),
                    location=battle_region,
                    war_id=(theater or {}).get("war_id"),
                    attacker_participants=(theater or {}).get("attacker_participants"),
                    defender_participants=(theater or {}).get("defender_participants"),
                    nation_theater_strength=(theater or {}).get("nation_theater_strength"),
                )

        # ── 9. Set last_combat_result ──
        if not is_bombardment and not ctx.get('skip_last_combat_result'):
            if attacker_won:
                attacker.last_combat_result = "victory"
                if defender and defender.name in world.marshals:
                    defender.last_combat_result = "defeat"
            elif defender_won:
                attacker.last_combat_result = "defeat"
                if defender and defender.name in world.marshals:
                    defender.last_combat_result = "victory"
            elif 'mutual_destruction' in outcome:
                attacker.last_combat_result = "defeat"
                if defender and defender.name in world.marshals:
                    defender.last_combat_result = "defeat"
            else:
                attacker.last_combat_result = "stalemate"
                if defender and defender.name in world.marshals:
                    defender.last_combat_result = "stalemate"

        # ── 10. Win/Loss Relationships ──
        if (not is_bombardment and not is_garrison and battle_result
                and defender and not ctx.get('skip_relationships')):
            from backend.game_logic.relationship import process_battle_relationships
            kwargs = {}
            if ctx.get('attacker_artillery'):
                kwargs['attacker_artillery'] = ctx['attacker_artillery']
            if ctx.get('defender_artillery'):
                kwargs['defender_artillery'] = ctx['defender_artillery']
            relationship_changes = process_battle_relationships(
                attacker, defender, battle_result, battle_region, world, **kwargs
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
                    "location": battle_region,
                })
            pipeline_out['relationship_changes'] = relationship_changes

        # ── 11. Vindication ──
        if not is_bombardment:
            if world.vindication_tracker.has_pending(attacker.name):
                if attacker_won:
                    vind_outcome = "victory"
                elif defender_won:
                    vind_outcome = "defeat"
                else:
                    vind_outcome = "draw"
                vindication_result = world.vindication_tracker.resolve_battle(
                    marshal_name=attacker.name,
                    result=vind_outcome,
                    game_state=world
                )
                if vindication_result:
                    pipeline_out['vindication_msg'] = f"\n\n[Vindication] {vindication_result['message']}"
                    pipeline_out['vindication_result'] = vindication_result

        # ── 12. Authority: major victory / defeat ──
        if not is_bombardment and not is_garrison:
            player_nation = world.player_nation
            player_is_attacker = attacker.nation == player_nation
            player_is_defender = defender_nation == player_nation

            if player_is_attacker or player_is_defender:
                atk_won_auth = attacker_won
                def_won_auth = defender_won
                player_won = (player_is_attacker and atk_won_auth) or (player_is_defender and def_won_auth)
                player_lost = (player_is_attacker and def_won_auth) or (player_is_defender and atk_won_auth)

                if player_won:
                    outnumbered = pre_atk < pre_def
                    if player_is_defender:
                        outnumbered = pre_def < pre_atk
                    capital_captured = False
                    if conquered:
                        cap_reg = world.get_region(battle_region)
                        if cap_reg and getattr(cap_reg, 'is_capital', False):
                            capital_captured = True
                    if outnumbered or capital_captured:
                        world.authority_tracker.modify_authority(+5)
                elif player_lost:
                    outnumbering = pre_atk > pre_def
                    if player_is_defender:
                        outnumbering = pre_def > pre_atk
                    capital_lost = False
                    cap_reg = world.get_region(battle_region)
                    if cap_reg and getattr(cap_reg, 'is_capital', False):
                        if cap_reg.controller != player_nation:
                            capital_lost = True
                    if outnumbering or capital_lost:
                        world.authority_tracker.modify_authority(-5)

        # ── 13. Coalition: threat + war exhaustion ──
        if not is_bombardment:
            from backend.game_logic.coalition import (
                add_threat, add_war_exhaustion_from_battle, add_coalition_shock
            )
            france = world.player_nation
            total_cas = int(atk_casualties) + int(def_casualties)

            if attacker_won and attacker.nation == france:
                # France won as attacker
                add_threat(world, 3, "battle_win")
                # Decisive: ratio > 2:1 AND total > 10,000
                if int(def_casualties) > 0 and int(atk_casualties) > 0:
                    ratio = int(def_casualties) / int(atk_casualties)
                elif int(def_casualties) > 0:
                    ratio = 999
                else:
                    ratio = 0
                if ratio > 2 and total_cas > 10000:
                    add_threat(world, 5, "decisive_victory")
                    if defender:
                        add_coalition_shock(defender_nation, world)
                if conquered:
                    cap_reg = world.get_region(battle_region)
                    if cap_reg and getattr(cap_reg, 'is_capital', False):
                        add_threat(world, 15, "capital_capture")
                add_war_exhaustion_from_battle(defender_nation, int(def_casualties), world)

            elif defender_won:
                if attacker.nation == france:
                    add_war_exhaustion_from_battle(attacker.nation, int(atk_casualties), world)
                if defender_nation == france:
                    add_threat(world, 3, "battle_win")
                    if int(atk_casualties) > 0 and int(def_casualties) > 0:
                        ratio = int(atk_casualties) / int(def_casualties)
                    elif int(atk_casualties) > 0:
                        ratio = 999
                    else:
                        ratio = 0
                    if ratio > 2 and total_cas > 10000:
                        add_threat(world, 5, "decisive_victory")
                        add_coalition_shock(attacker.nation, world)
                    add_war_exhaustion_from_battle(
                        attacker.nation, int(atk_casualties), world)

            elif not attacker_won and not defender_won and is_garrison:
                # Garrison hold — war exhaustion for attacking nation
                from backend.game_logic.coalition import add_war_exhaustion_from_battle as add_we
                add_we(attacker.nation, int(atk_casualties), world)

        # ── 14. Exhaustion tracking ──
        if not ctx.get('skip_exhaustion'):
            attacker.increment_attacks_this_turn()

        return pipeline_out

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

        # Recompute coordination for the attacker's current region before reading
        # the modifier — unlike the marshal-vs-marshal paths, garrison assault has
        # no coordination recompute, so a stale bonus left on an ally (e.g. by a
        # glorious charge out of a shared region) would otherwise be applied here.
        self._calculate_coordination_context(marshal, world)
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

        # [5C-11] War damage to battle region (pre-battle strengths)
        pre_battle_atk_strength = marshal.strength + attacker_losses
        self._apply_battle_effects_to_region(
            target_region.name, pre_battle_atk_strength, old_garrison, world)

        # [5C-6] Fog/intel update after garrison battle
        world.update_intel_from_battle(target_region.name, world.current_turn)

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
            # R1 Pipeline: centralized post-combat recording
            self._post_combat_pipeline({
                'attacker': marshal,
                'defender': None,
                'defender_nation': old_controller,
                'battle_region': target_region.name,
                'outcome': 'attacker_victory',
                'attacker_won': True,
                'defender_won': False,
                'attacker_casualties': int(attacker_losses),
                'defender_casualties': int(garrison_losses),
                'pre_battle_attacker_strength': pre_battle_atk_strength,
                'pre_battle_defender_strength': old_garrison,
                'battle_result': None,
                'conquered': True,
                'is_garrison': True,
                'skip_coordination_clear': True,
                'skip_log_battle_event': True,
                'skip_intel_update': True,
                'skip_war_damage': True,
                'skip_exhaustion': True,
            }, world)

            # Custom garrison authority (uses garrison_effective, not standard outnumbered check)
            if marshal.nation == world.player_nation:
                garrison_effective = int(old_garrison * (1.0 + TERRAIN_DEFENSE_BONUS.get(target_region.terrain, 0.0))
                                         * (1.0 + (0.25 if target_region.has_building("fortification") else 0.0)))
                if pre_battle_atk_strength < garrison_effective:
                    world.authority_tracker.modify_authority(+5)
                if getattr(target_region, 'is_capital', False):
                    world.authority_tracker.modify_authority(+5)

            # Move attacker into region
            marshal.move_to(target_region.name)

            # Movement attrition
            attrition_info = self._executor._calculate_movement_attrition(marshal, target_region.name, world)

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

            # R1 Pipeline: centralized post-combat recording
            self._post_combat_pipeline({
                'attacker': marshal,
                'defender': None,
                'defender_nation': target_region.controller,
                'battle_region': target_region.name,
                'outcome': 'defender_victory',
                'attacker_won': False,
                'defender_won': True,
                'attacker_casualties': int(attacker_losses),
                'defender_casualties': int(garrison_losses),
                'pre_battle_attacker_strength': pre_battle_atk_strength,
                'pre_battle_defender_strength': old_garrison,
                'battle_result': None,
                'conquered': False,
                'is_garrison': True,
                'skip_coordination_clear': True,
                'skip_log_battle_event': True,
                'skip_intel_update': True,
                'skip_war_damage': True,
                'skip_exhaustion': True,
            }, world)

            # Custom garrison authority (uses garrison_effective)
            if marshal.nation == world.player_nation:
                garrison_effective = int(old_garrison * (1.0 + TERRAIN_DEFENSE_BONUS.get(target_region.terrain, 0.0))
                                         * (1.0 + (0.25 if target_region.has_building("fortification") else 0.0)))
                if pre_battle_atk_strength > garrison_effective:
                    world.authority_tracker.modify_authority(-5)

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
            # Movement attrition on forced retreat (Phase 6.2.F) — halved rate
            forced_retreat_attrition = self._executor._calculate_movement_attrition(marshal, retreat_to, world, is_retreat=True)
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
            return f"[!] {marshal.name}'s broken army flees to {retreat_to}!{strategic_msg}{attrition_note} (recovering for 3 turns)"
        else:
            # ════════════════════════════════════════════════════════════
            # SURROUNDED - ARMY BROKEN: No safe retreat possible
            # Army shatters, survivors flee to capital with 3-10% strength
            # ════════════════════════════════════════════════════════════
            old_loc = marshal.location
            old_strength = marshal.strength

            # Calculate survivors (3-10% of current strength)
            survival_rate = random.uniform(0.03, 0.10)
            # Minimum 1000 survivors, but a rout can never leave MORE troops than
            # the army had when it broke: for a sub-1000 army the flat floor would
            # otherwise be a net gain (an 800-man corps "shatters" to 1000).
            survivors = min(old_strength, max(1000, int(old_strength * survival_rate)))

            # V2-65: Find safe spawn (capital may be enemy-occupied)
            # V2-93: Exclude battle location so broken marshal doesn't stay in place
            spawn_loc = world.find_safe_spawn(marshal, exclude=marshal.location)

            # Apply broken state
            # NOTE: Broken armies do NOT set retreated_this_turn because:
            # 1. They flee to capital (not adjacent region) - no ally cover possible
            # 2. They're in BROKEN state with 3-10% strength - not a normal retreat
            marshal.move_to(spawn_loc)  # Use move_to() for proper state clearing
            marshal.strength = survivors
            marshal.morale = 20  # Shattered morale
            marshal.broken = True
            marshal.broken_recovery = 0  # Start at stage 0 (4 turns to recover)

            # Clear all combat transient state (single source of truth)
            marshal.retreating = False
            marshal.retreat_recovery = 0
            marshal.clear_combat_transient_state()

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
                f"[BROKEN] {marshal.name}'s army is SURROUNDED and SHATTERED at {old_loc}! "
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
        attacker_casualties = max(1, int(marshal.strength * return_rate * return_variance))

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
        # m3: Floor morale at forced-retreat threshold — bombardment alone shouldn't collapse armies
        if defender.morale < FORCED_RETREAT_THRESHOLD:
            defender.morale = FORCED_RETREAT_THRESHOLD

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
                    # m3: Floor morale at forced-retreat threshold for collateral too
                    if force.morale < FORCED_RETREAT_THRESHOLD:
                        force.morale = FORCED_RETREAT_THRESHOLD

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

        # R1 Pipeline: centralized diplo recording (Bug 5 fix — bombardment was missing this)
        self._post_combat_pipeline({
            'attacker': marshal,
            'defender': defender,
            'battle_region': target_location,
            'outcome': 'bombardment',
            'attacker_won': True,
            'defender_won': False,
            'attacker_casualties': int(attacker_casualties),
            'defender_casualties': int(defender_casualties),
            'pre_battle_attacker_strength': int(marshal.strength + attacker_casualties),
            'pre_battle_defender_strength': int(pre_defender_strength),
            'battle_result': None,
            'conquered': False,
            'is_bombardment': True,
            'skip_coordination_clear': True,
            'skip_log_battle_event': True,
            'skip_intel_update': True,
            'skip_idle_reset': True,
            'skip_exhaustion': True,
            'skip_cannon_fire_record': True,
            'skip_war_damage': True,
        }, world)

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
            "terrain_modifier": int(terrain_mod * 100),
            "fort_degraded": fortification_degraded,
            "fort_old": int(fortification_old * 100),
            "fort_new": int(fortification_new * 100),
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
                "terrain_modifier": int(terrain_mod * 100),
                "fort_degraded": fortification_degraded,
                "fort_old": int(fortification_old * 100),
                "fort_new": int(fortification_new * 100),
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

    def _build_opening_attack_guidance(self, world: WorldState) -> Dict:
        """Build first-hour guidance for the naive Ney-vs-Wellington opener."""
        drouot = world.get_marshal("Drouot")
        davout = world.get_marshal("Davout")

        preparation_steps = []
        if drouot and drouot.nation == world.player_nation and drouot.strength > 0:
            preparation_steps.append(
                "Move Drouot to Belgium first so he can bombard Waterloo before Ney commits."
            )
        if davout and davout.nation == world.player_nation and davout.strength > 0:
            preparation_steps.append(
                "Bring Davout forward before committing Ney alone so Wellington does not meet a single unsupported thrust."
            )
        if not preparation_steps:
            preparation_steps.append(
                "Bring another French marshal forward before committing Ney alone."
            )

        return {
            "title": "BERTHIER'S WARNING",
            "message": (
                '"Sire, a lone rush at Wellington from Belgium teaches the wrong lesson. '
                'Waterloo is ready for him, and Ney will spend men before you have shown the counterplay."'
            ),
            "tip": "Better line: " + " ".join(preparation_steps),
            "warning": (
                "The direct unsupported assault is still risky. "
                "Soften Waterloo or add support before asking Ney to force the issue."
            ),
            "summary": (
                "Berthier halts the direct Ney assault long enough to point out a better opening."
            ),
        }

    def _should_surface_opening_attack_guidance(
        self,
        marshal,
        enemy_marshal,
        world: WorldState,
    ) -> bool:
        """Intercept the common first-hour bad opener once per campaign."""
        if world.current_turn != 1:
            return False
        if getattr(world, "opening_attack_guidance_shown", False):
            return False
        if marshal.nation != world.player_nation:
            return False
        if marshal.name != "Ney" or enemy_marshal.name != "Wellington":
            return False
        if marshal.location != "Belgium" or enemy_marshal.location != "Waterloo":
            return False

        # If the player has already staged support into Belgium, let the attack proceed.
        has_setup_support = any(
            ally.nation == marshal.nation
            and ally.name != marshal.name
            and ally.location == marshal.location
            and ally.strength > 0
            for ally in world.marshals.values()
        )
        return not has_setup_support

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
        self._executor._auto_break_square(marshal, "attack")

        def _stage_war_purpose_for_attack(target_nation: str) -> Dict:
            """Stage WPS-A purpose selection instead of auto-declaring by attack."""
            from backend.game_logic.diplomacy import get_available_war_objectives

            objectives = get_available_war_objectives(world, marshal.nation, target_nation)
            options = []
            for obj in objectives:
                if obj.get("available"):
                    options.append({
                        "label": obj.get("label", obj.get("type", "Objective")),
                        "action": "select_war_objective",
                        "objective_type": obj.get("type"),
                        "target_nation": target_nation,
                    })
            options.append({"label": "Back Out", "action": "reconsider"})
            world.dialogue_manager.replace({
                "type": "war_purpose_selection",
                "target_nation": target_nation,
                "message": f"Choose your war purpose against {target_nation}.",
                "objectives": objectives,
                "options": options,
                "blocking": True,
                "turn_created": int(world.current_turn),
            })
            return {
                "success": True,
                "message": (
                    f"Choose your war purpose against {target_nation}. "
                    "Issue the attack again after the declaration is settled."
                ),
                "war_purpose_popup": {
                    "target_nation": target_nation,
                    "objectives": objectives,
                },
                "diplomatic_dialogue": world.pending_diplomatic_dialogue,
                "awaiting_diplomatic_response": True,
            }

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
                drill_cancelled_message = f"[!] DRILL CANCELLED: {marshal.name}'s drill was interrupted - troops dispersed before training completed.\n\n"

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
                        if (m.name.lower() == resolved_target.lower()
                                and m.nation != marshal.nation
                                and world.is_at_war(marshal.nation, m.nation)):
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
                            if not world.is_at_war(marshal.nation, m.nation):
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
                                    f"[Cavalry][Blocked] {marshal.name}'s blood is up (Recklessness: {recklessness}) "
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
                                "message": f"[Cavalry] {marshal.name}'s blood is up! (Recklessness: {recklessness})\n\n"
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
                # C2 fix: Use nation-aware lookup for AI marshals to prevent same-nation targeting
                result = world._find_nearest_enemy_for_nation(marshal.location, marshal.nation)

            if result:
                nearest_enemy, distance = result
                # Check if in range (distance already returned by find_nearest_enemy)
                if distance <= marshal.movement_range:
                    # Auto-target the nearest enemy
                    target = nearest_enemy.name
                else:
                    # Out of range — literal marshals ask for clarification instead of guessing
                    if getattr(marshal, 'personality', '') == 'literal':
                        # R5: Fog-filtered for player, omniscient for AI
                        if marshal.nation == world.player_nation:
                            enemies = [e for e in world.get_visible_enemies(marshal.nation) if e.strength > 0]
                        else:
                            enemies = [e for e in world.get_enemies_of_nation(marshal.nation) if e.strength > 0]
                        # CR-2: options carry the full reissue command so the
                        # popup and typed answers resolve identically.
                        # Adversarial-review fix: sort by distance so the
                        # FIRST option is the nearest enemy the question
                        # names — dict-insertion order let a typed "yes"
                        # pursue a different enemy than the one asked about.
                        from backend.commands.clarification import strategic_reissue_command

                        enemies.sort(
                            key=lambda e: world.get_distance(marshal.location, e.location))
                        options = []
                        for e in enemies[:3]:
                            e_dist = world.get_distance(marshal.location, e.location)
                            options.append({
                                "label": f"Pursue {e.name} ({e.location}, {e_dist} away)",
                                "value": "specify",
                                "target": e.name,
                                "command": strategic_reissue_command(
                                    marshal.name, "PURSUE", e.name),
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
                        # [4A-1] Break square formation before auto-move
                        self._executor._auto_break_square(marshal, "attack")

                        # [4A-1] Diplomatic territory check
                        from backend.game_logic.diplomacy import can_enter_territory
                        best_region = world.get_region(best_next)
                        if best_region and best_region.controller and best_region.controller != marshal.nation:
                            if not can_enter_territory(world, marshal.nation, best_region.controller):
                                return {
                                    "success": False,
                                    "message": f"{marshal.name} cannot enter {best_next} — diplomatic restrictions."
                                }

                        old_location = marshal.location
                        marshal.move_to(best_next)

                        # [4A-1] Artillery: mark as moved (blocks attacking this turn)
                        if getattr(marshal, 'artillery', False):
                            marshal.moved_this_turn = True

                        # [4A-1] Reset idle tracking
                        marshal.idle_turns = 0
                        marshal._acted_this_turn = True

                        # [4A-1] Refresh fog of war
                        if marshal.nation == world.player_nation:
                            world.calculate_visibility()

                        # [4A-1] Movement attrition
                        attrition_info = self._executor._calculate_movement_attrition(marshal, best_next, world)
                        attrition_msg = f" ({attrition_info['total_losses']:,} lost to march)" if attrition_info["total_losses"] > 0 else ""

                        return {
                            "success": True,
                            "message": f"{marshal.name} advances from {old_location} to {best_next}, moving toward {nearest_enemy.name} at {nearest_enemy.location}! (Now {best_distance} region{'s' if best_distance != 1 else ''} away){attrition_msg}"
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
        enemy_by_name, enemy_error = self._executor._fuzzy_match_enemy(target, world, marshal.nation)
        resolved_target = target

        if not enemy_by_name:
            # PT-4 FIX: If fuzzy match returned a diplomatic block (armistice/etc),
            # return it immediately instead of falling through to "Unknown target"
            if enemy_error and enemy_error.get("diplomatic_block"):
                return enemy_error

            # 4D-4: Check if target is a friendly marshal name
            friendly_match = None
            target_lower = target.lower()
            for m in world.marshals.values():
                if m.nation == marshal.nation and m.name.lower() == target_lower:
                    friendly_match = m
                    break
            if friendly_match:
                return {
                    "success": False,
                    "message": f"Cannot attack friendly marshal {friendly_match.name}!"
                }

            # Not an enemy - try fuzzy matching for region names
            target_region_fuzzy, region_error = self._executor._fuzzy_match_region(target, world)

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
                    return self._executor._execute_strategic_command(pursue_parsed, pursue_parsed["command"], game_state)

                # Non-enemy or AI marshal — provide helpful error
                # Find closer targets within range
                # R5: Fog-filtered for player, omniscient for AI
                nearby_targets = []
                if marshal.nation == world.player_nation:
                    candidate_enemies = world.get_visible_enemies(marshal.nation)
                else:
                    candidate_enemies = world.get_enemies_of_nation(marshal.nation)
                for enemy in candidate_enemies:
                    if enemy.strength > 0:
                        enemy_distance = world.get_distance(marshal.location, enemy.location)
                        if enemy_distance <= marshal.movement_range:
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
        enemies_here = [m for m in marshals_here if m.nation != marshal.nation and m.strength > 0 and world.is_at_war(marshal.nation, m.nation)]

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
        if not enemy_marshal and enemy_by_name and enemy_by_name.nation != marshal.nation:
            enemy_marshal = enemy_by_name

        if not enemy_marshal:
            # Check if target is a region with enemies (use resolved_target for regions)
            enemy_marshal = world.get_enemy_at_location_for_nation(resolved_target, marshal.nation)

        # ════════════════════════════════════════════════════════════
        # AUTO WAR DECLARATION (Phase 8 Session 2)
        # If attacking a nation we're not at WAR with, auto-declare war
        # before proceeding. Costs 1 DP, applies relation penalties.
        # ════════════════════════════════════════════════════════════
        if enemy_marshal and not world.is_at_war(marshal.nation, enemy_marshal.nation):
            # Never turn an attack into a war declaration against our own ally
            # or vassal (friendly-fire backstop).
            _refusal = friendly_fire_refusal(world, marshal, enemy_marshal.nation)
            if _refusal is not None:
                return _refusal
            if marshal.nation == world.player_nation:
                return _stage_war_purpose_for_attack(enemy_marshal.nation)
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
                and world.is_at_war(marshal.nation, m.nation)
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
                    # Don't declare war on our own ally/vassal to seize their land.
                    _refusal = friendly_fire_refusal(world, marshal, target_region.controller)
                    if _refusal is not None:
                        return _refusal
                    from backend.game_logic.diplomacy import declare_war, can_enter_territory
                    if not can_enter_territory(world, marshal.nation, target_region.controller):
                        if marshal.nation == world.player_nation:
                            return _stage_war_purpose_for_attack(target_region.controller)
                        war_result = declare_war(world, marshal.nation, target_region.controller)
                        if war_result.get("success") and marshal.nation == world.player_nation:
                            dp = getattr(world, 'diplomatic_points', 0)
                            world.diplomatic_points = max(0, dp - war_result.get("dp_cost", 1))

                # Check for any defenders (marshals from nations other than attacker)
                defenders = [m for m in world.marshals.values()
                            if m.location == resolved_target and m.strength > 0 and m.nation != marshal.nation
                            and world.is_at_war(marshal.nation, m.nation)]

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
                    attrition_info = self._executor._calculate_movement_attrition(marshal, resolved_target, world)

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
        if self._should_surface_opening_attack_guidance(marshal, enemy_marshal, world):
            world.opening_attack_guidance_shown = True
            guidance = self._build_opening_attack_guidance(world)
            return {
                "success": True,
                "message": guidance["summary"],
                "opening_attack_guidance": guidance,
                "free_action": True,
                "action_summary": world.get_action_summary(),
                "game_state": world.get_filtered_game_state_summary(),
            }

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
                    f"[Shield] {covering_ally.name} steps forward to cover {original_target.name}'s retreat! "
                    f"\"{original_target.name} is in no condition to fight - I'll handle this!\"\n\n"
                )
                print(f"  [ALLY COVER] {covering_ally.name} covers for retreating {original_target.name}")
            else:
                # No covering ally - target is EXPOSED
                covering_message = (
                    f"[!] {enemy_marshal.name} is EXPOSED! (Just retreated, no ally to cover)\n\n"
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
                        and world.is_at_war(marshal.nation, m.nation)
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
                cavalry_charge_message = f"[Cavalry] {marshal.name}'s cavalry thunders across {middle} to strike! (Cavalry Charge: 2-region attack)\n"
            else:
                cavalry_charge_message = f"[Cavalry] {marshal.name}'s cavalry charges across the battlefield! (Cavalry Charge: 2-region attack)\n"

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

        # W6-2 Dynamic Battle Naming: total engaged for the Great tier —
        # both primaries + every arrived reinforcer, PRE-battle strengths
        # (captured here, before combat consumes anyone).
        total_engaged_strength = int(pre_battle_attacker_strength) + int(pre_battle_defender_strength)
        for _side_results in (attacker_reinforcements, defender_reinforcements):
            for _r in _side_results:
                if _r.get("arrived"):
                    _arr = world.marshals.get(_r.get("marshal", ""))
                    if _arr:
                        total_engaged_strength += int(_arr.strength)

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
        defender_coord = self._calculate_coordination_context(
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
            marshal, atk_participants, battle_region_name, world,
            defender_name=enemy_marshal.name)

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
                    and world.is_at_war(marshal.nation, m.nation)
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

            # R1 Pipeline: centralized post-combat recording
            # Actual bombardment damage is the defender's pre-battle strength
            # (they were destroyed), but we use support_bombardment_total_damage
            # as the actual casualties for correct war score (Bug 2 fix).
            auto_kill_battle_result = {
                "outcome": "attacker_wins",
                "victor": marshal.name,
                "attacker_casualties": 0,
                "defender_casualties": int(support_bombardment_total_damage),
            }
            pipeline_out = self._post_combat_pipeline({
                'attacker': marshal,
                'defender': enemy_marshal,
                'defender_nation': enemy_marshal.nation,
                'battle_region': battle_region_name,
                'outcome': 'attacker_victory',
                'attacker_won': True,
                'defender_won': False,
                'attacker_casualties': 0,
                'defender_casualties': int(support_bombardment_total_damage),
                'pre_battle_attacker_strength': pre_battle_attacker_strength,
                'pre_battle_defender_strength': pre_battle_defender_strength,
                'battle_result': auto_kill_battle_result,
                'conquered': bool(conquest_msg),
                'is_auto_bombardment_kill': True,
            }, world)

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

            # F1a fix: resolve_battle builds the outcome description BEFORE the
            # caller distributes casualties, so it bakes the WHOLE-CORPS raw total
            # in under the primary marshal's name ("Casualties: Ney 8,141" when Ney
            # personally lost 2,171 and reinforcers took the rest). Rewrite the line
            # to the primary's ACTUAL distributed share; the reinforcers' share is
            # reported separately via reinforcement_messages ("supporting allies lost
            # N combined") so there is no double-count.
            battle_result["description"] = self._rewrite_primary_casualties(
                battle_result.get("description", ""),
                marshal.name, battle_result["attacker_raw_casualties"],
                atk_distribution.get(marshal.name, battle_result["attacker_raw_casualties"]),
                enemy_marshal.name, battle_result["defender_raw_casualties"],
                def_distribution.get(enemy_marshal.name, battle_result["defender_raw_casualties"]),
            )

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
            # Uses module-level FORCED_RETREAT_THRESHOLD from combat.py (Bug 7 fix)
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
                        f"[Cavalry] {marshal.name}'s '{marshal.ability['name']}' — "
                        f"cavalry runs down the retreating enemy! (+{pursuit_damage:,} pursuit casualties)"
                    )
                elif attacker_ability_name == "Vorwärts!":
                    pursuit_damage = 3000
                    pursuit_message = (
                        f"[Combat] {marshal.name}'s '{marshal.ability['name']}' — "
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
            # Legacy keys carry the ATTACKER side (existing readers + test
            # fixtures depend on this shape).
            "type_count": attacker_coord.get("type_count", 0),
            "hostile_forced_participants": [],
            "hostile_refused": [],
            "devoted_allies": [],
            # Side-tagged copies so _pick_observation can read the PLAYER'S
            # side when the player is the defender — the legacy attacker-only
            # data credited an enemy combined-arms triangle to "our side"
            # (audit 2026-07-09 fix 2.2).
            "attacker_type_count": attacker_coord.get("type_count", 0),
            "defender_type_count": defender_coord.get("type_count", 0),
            "defender_hostile_forced_participants": [],
            "defender_hostile_refused": [],
            "defender_devoted_allies": [],
        }
        # Classify each side's participants by relationship toward that
        # side's primary combatant.
        if is_coordinated_battle:
            for side_primary, participants, forced_key, refused_key, devoted_key in (
                (marshal, atk_participants,
                 "hostile_forced_participants", "hostile_refused", "devoted_allies"),
                (enemy_marshal, def_participants,
                 "defender_hostile_forced_participants", "defender_hostile_refused",
                 "defender_devoted_allies"),
            ):
                for p in participants:
                    if p.name == side_primary.name:
                        continue
                    rel = p.get_relationship(side_primary.name)
                    if rel == -2:
                        # Hostile — check for SUPPORT order
                        order = getattr(p, 'strategic_order', None)
                        has_support = (
                            order is not None
                            and order.command_type == "SUPPORT"
                            and order.target == side_primary.name
                        )
                        if has_support:
                            coord_context[forced_key].append(p.name)
                        else:
                            coord_context[refused_key].append(p.name)
                    elif rel == 2:
                        coord_context[devoted_key].append(p.name)
        battle_result["coordination_context"] = coord_context
        battle_result["reinforcement_results_for_report"] = {
            "attacker": attacker_reinforcements,
            "defender": defender_reinforcements,
        }
        # Session 68: Inject auto-bombardment and overwatch data for observation re-pick
        battle_result["support_bombardment_total_damage"] = support_bombardment_total_damage
        battle_result["overwatch_count"] = overwatch_count

        # ════════════════════════════════════════════════════════════
        # W6-1 (BUG-CA-9): PARTICIPATION COUNTS. Every ARRIVED
        # reinforcement participant records the battle like the primary
        # pair does (the blessed ES-7 model already assumes "every
        # coordination participant increments battles_won"); anyone who
        # fought is no longer idle; last_battle_turn feeds W6-3 arc memory.
        # Stalemates count for no one — mirroring the primary pair.
        # ════════════════════════════════════════════════════════════
        _w6_outcome = battle_result.get("outcome", "")
        _atk_won = _w6_outcome in ("attacker_victory", "attacker_tactical_victory")
        _def_won = _w6_outcome in ("defender_victory", "defender_tactical_victory")
        _w6_turn = int(world.current_turn)
        marshal.last_battle_turn = _w6_turn
        marshal.idle_turns = 0
        enemy_marshal.last_battle_turn = _w6_turn
        enemy_marshal.idle_turns = 0
        for _side_results, _side_won, _side_lost in (
            (attacker_reinforcements, _atk_won,
             _def_won or _w6_outcome == "mutual_destruction"),
            (defender_reinforcements, _def_won,
             _atk_won or _w6_outcome == "mutual_destruction"),
        ):
            for _r in _side_results:
                if not _r.get("arrived"):
                    continue
                _fighter = world.get_marshal(_r.get("marshal", ""))
                if _fighter is None:
                    continue
                if _side_won:
                    _fighter.battles_won += 1
                elif _side_lost:
                    _fighter.battles_lost += 1
                _fighter.idle_turns = 0
                _fighter.last_battle_turn = _w6_turn

        # ════════════════════════════════════════════════════════════
        # W6-2 DYNAMIC BATTLE NAMING: composed ONCE per battle (this
        # increments the region's named-battle count) and stamped BEFORE
        # the event-log write so the campaign log, the diplo record, the
        # war HUD, and the result/report all carry the same name.
        # ════════════════════════════════════════════════════════════
        battle_name = world.compose_battle_name(
            target_location, total_engaged_strength)
        battle_result["battle_name"] = battle_name
        if isinstance(battle_result.get("log_battle_event"), dict):
            battle_result["log_battle_event"]["battle_name"] = battle_name

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
        # [7B-1] Split artillery reinforcements by nation for relationship processing
        atk_artillery = [a for a in artillery_reinforced_adjacent if a.nation == marshal.nation]
        def_artillery = [a for a in artillery_reinforced_adjacent if a.nation == enemy_marshal.nation]
        relationship_changes = process_battle_relationships(
            marshal, enemy_marshal, battle_result, battle_region_name, world,
            attacker_artillery=atk_artillery, defender_artillery=def_artillery
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
                or coord_context.get("defender_type_count", 0) >= 3
                or coord_context.get("hostile_forced_participants")
                or coord_context.get("hostile_refused")
                or coord_context.get("devoted_allies")
                or coord_context.get("defender_hostile_forced_participants")
                or coord_context.get("defender_hostile_refused")
                or coord_context.get("defender_devoted_allies")
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
        from backend.game_logic.war_contribution import detect_battle_theater
        outcome = battle_result.get("outcome", "")
        atk_won = "attacker" in outcome and "victory" in outcome
        def_won = "defender" in outcome and "victory" in outcome
        diplo_winner = marshal.nation if atk_won else (enemy_marshal.nation if def_won else None)
        if diplo_winner:
            # Imperial Settlement B2: theater-aware emitter — pass one-hop
            # adjacency participants + theater strength so allies near the
            # battle receive battle-bucket credit (spec §9.4 line 717).
            theater = detect_battle_theater(
                world,
                battle_region=target_location,
                attacker_nation=marshal.nation,
                defender_nation=enemy_marshal.nation,
                attacker_marshal_name=getattr(marshal, "name", None),
                defender_marshal_name=getattr(enemy_marshal, "name", None),
                attacker_pre_battle_strength=int(pre_battle_attacker_strength),
                defender_pre_battle_strength=int(pre_battle_defender_strength),
            )
            record_diplo_battle(
                world,
                attacker_nation=marshal.nation,
                defender_nation=enemy_marshal.nation,
                winner_nation=diplo_winner,
                attacker_casualties=int(battle_result.get("attacker", {}).get("casualties", 0)),
                defender_casualties=int(battle_result.get("defender", {}).get("casualties", 0)),
                location=target_location,
                war_id=(theater or {}).get("war_id"),
                attacker_participants=(theater or {}).get("attacker_participants"),
                defender_participants=(theater or {}).get("defender_participants"),
                nation_theater_strength=(theater or {}).get("nation_theater_strength"),
                battle_name=battle_name,
            )

        # [7A-3] Set last_combat_result for strategic condition checking (until_battle_won)
        if atk_won:
            marshal.last_combat_result = "victory"
            enemy_marshal.last_combat_result = "defeat"
        elif def_won:
            marshal.last_combat_result = "defeat"
            enemy_marshal.last_combat_result = "victory"
        elif "mutual_destruction" in outcome:
            marshal.last_combat_result = "defeat"
            enemy_marshal.last_combat_result = "defeat"
        else:
            marshal.last_combat_result = "stalemate"
            enemy_marshal.last_combat_result = "stalemate"

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
        elif can_advance and marshal.strength > 0 and not getattr(self._executor, '_current_sortie', False):
            if marshal.location != target_location:
                print(f"[ATTACK MOVEMENT] MOVING {marshal.name}: {marshal.location} -> {target_location}")
                marshal.move_to(target_location)
                # Movement attrition on post-battle advance (Phase 6.2.F)
                attrition_info = self._executor._calculate_movement_attrition(marshal, target_location, world)
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
                and world.is_at_war(marshal.nation, m.nation)
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

        # R1 Pipeline: centralized vindication + authority + coalition
        atk_pip_outcome = battle_result.get("outcome", "")
        atk_pip_won = "attacker" in atk_pip_outcome and "victory" in atk_pip_outcome
        def_pip_won = "defender" in atk_pip_outcome and "victory" in atk_pip_outcome
        atk_pip_cas = int(battle_result.get("attacker", {}).get("casualties", 0))
        def_pip_cas = int(battle_result.get("defender", {}).get("casualties", 0))

        pipeline_out = self._post_combat_pipeline({
            'attacker': marshal,
            'defender': enemy_marshal,
            'defender_nation': enemy_marshal.nation,
            'battle_region': target_location,
            'outcome': atk_pip_outcome,
            'attacker_won': atk_pip_won,
            'defender_won': def_pip_won,
            'attacker_casualties': atk_pip_cas,
            'defender_casualties': def_pip_cas,
            'pre_battle_attacker_strength': pre_battle_attacker_strength,
            'pre_battle_defender_strength': pre_battle_defender_strength,
            'battle_result': battle_result,
            'conquered': conquered,
            # Skip steps already handled inline by _execute_attack
            'skip_coordination_clear': True,
            'skip_log_battle_event': True,
            'skip_combat_notifications': True,
            'skip_intel_update': True,
            'skip_war_damage': True,
            'skip_idle_reset': True,
            'skip_cannon_fire_record': True,
            'skip_diplo_record': True,
            'skip_last_combat_result': True,
            'skip_relationships': True,
            'skip_exhaustion': True,
        }, world)

        vindication_msg = pipeline_out.get('vindication_msg', '')
        vindication_result = pipeline_out.get('vindication_result')

        # Build auto-bombardment preamble (Session 68) — prepended before combat description
        auto_bombard_preamble = ""
        if auto_bombardment_messages:
            auto_bombard_preamble = "\n".join(auto_bombardment_messages) + "\n\n"

        # Build final message with optional drill cancellation prefix, counter-punch, cavalry charge, and covering
        battle_message = counter_punch_message + cavalry_charge_message + covering_message + flanking_prefix + auto_bombard_preamble + battle_result["description"] + destroyed_msg + movement_msg + conquest_msg + vindication_msg + forced_retreat_msg
        if drill_cancelled_message:
            battle_message = drill_cancelled_message + battle_message

        # W6-2 Dynamic Battle Naming: battle_name was composed once above
        # (right before the diplo record) — reused here for the result/event.

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

        marshal, error = self._executor._fuzzy_match_marshal(marshal_name, world)
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
        if getattr(marshal, 'retreat_recovery', 0) > 0:
            return {
                "success": False,
                "message": f"{marshal.name} is recovering from retreat and cannot form square."
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

        marshal, error = self._executor._fuzzy_match_marshal(marshal_name, world)
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
            return {"success": False, "message": "Game state error in _execute_charge: world state unavailable"}

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
        self._executor._auto_break_square(marshal, "attack")

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
            if m.name.lower() == target.lower() and m.nation != marshal.nation and world.is_at_war(marshal.nation, m.nation):
                target_marshal = m
                break

        # Try fuzzy match
        if not target_marshal:
            target_region = world.get_region(target)
            if target_region:
                # Find enemy in that region
                for m in world.marshals.values():
                    if m.location == target_region.name and m.nation != marshal.nation and world.is_at_war(marshal.nation, m.nation):
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
            print(f"  [CHARGE BLOCKED] {terrain_name} terrain blocks charge -- falling through to normal attack")
            result = self._execute_attack(marshal, target, world, game_state, skip_reckless_popup=True)
            result["charge_blocked_by_terrain"] = True
            result["terrain"] = charge_region.terrain
            if result.get("success"):
                result["message"] = (
                    f"[Cavalry][Blocked] {marshal.name}'s cavalry cannot charge in {terrain_name} terrain! "
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
                    and world.is_at_war(marshal.nation, m.nation)
                ]
                if enemies_in_middle:
                    blocking_enemy = enemies_in_middle[0]
                    return {
                        "success": False,
                        "message": f"Cannot charge through {middle} - {blocking_enemy.name} blocks the path!",
                        "blocked_by": blocking_enemy.name
                    }

        # V2-2: Engagement check — skip if already fought this pair this turn
        for battle in world.battles_this_turn:
            pair = {battle.get("attacker"), battle.get("defender")}
            if marshal.name in pair and target_marshal.name in pair:
                return {
                    "success": False,
                    "message": f"{marshal.name} has already engaged {target_marshal.name} this turn!"
                }

        # V2-51: Record attack direction for flanking bonus
        world.record_attack(marshal.name, marshal.location, target_marshal.location)

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
        # Origin region BEFORE the charge advances — see coordination-clear below.
        charge_origin_region = marshal.location

        # [5D-3] Calculate coordination bonuses for both sides (fairness per spec)
        self._calculate_coordination_context(marshal, world)
        self._calculate_coordination_context(target_marshal, world)

        # Get combat result with glorious charge flag
        combat_result = self.combat_resolver.resolve_battle(
            attacker=marshal,
            defender=target_marshal,
            terrain=charge_terrain,
            glorious_charge=True,  # 2x damage multiplier
            fortification_bonus=charge_fort_bonus
        )

        # ALWAYS reset recklessness after Glorious Charge
        marshal.reset_recklessness()
        marshal.in_combat_this_turn = True

        # ════════════════════════════════════════════════════════════
        # FORCED RETREAT: Handle broken armies (morale <= 25%)
        # Must happen BEFORE movement so retreating defenders clear
        # the territory for capture.
        # ════════════════════════════════════════════════════════════
        forced_retreat_msg = self._handle_forced_retreat(
            combat_result, marshal, target_marshal, world
        )

        # Move attacker if victorious and still alive
        attacker_won = combat_result.get("attacker_won", False)
        movement_msg = ""
        if attacker_won and marshal.strength > 0:
            if marshal.location != charge_battle_region:
                marshal.move_to(charge_battle_region)
                charge_attrition = self._executor._calculate_movement_attrition(marshal, charge_battle_region, world)
                combat_result["attacker_moved"] = True
                combat_result["attacker_new_location"] = charge_battle_region
                movement_msg = f" {marshal.name} advances into {charge_battle_region}."
                if charge_attrition["total_losses"] > 0:
                    charge_march_note = f" ({charge_attrition['total_losses']:,} lost to march"
                    if charge_attrition.get("depot_bonus"):
                        charge_march_note += " — forward supply lines reduce losses"
                    charge_march_note += ")"
                    movement_msg += charge_march_note

        # Check if enemy was destroyed - remove from world
        enemy_destroyed_msg = ""
        if target_marshal.strength <= 0:
            enemy_destroyed_msg = f" {target_marshal.name}'s army is destroyed!"
            world.marshals.pop(target_marshal.name, None)

        # Check if attacker was destroyed
        if marshal.strength <= 0:
            world.marshals.pop(marshal.name, None)

        # ════════════════════════════════════════════════════════════
        # TERRITORY CAPTURE: Check if charge won empty territory
        # ════════════════════════════════════════════════════════════
        conquered = False
        conquest_msg = ""
        if attacker_won and marshal.strength > 0 and marshal.location == charge_battle_region:
            target_region = world.get_region(charge_battle_region)
            if target_region and target_region.controller != marshal.nation:
                remaining_defenders = [
                    m for m in world.marshals.values()
                    if m.location == charge_battle_region and m.strength > 0 and m.nation != marshal.nation
                    and world.is_at_war(marshal.nation, m.nation)
                ]
                if not remaining_defenders:
                    capture_result = self._attempt_region_capture(
                        marshal, charge_battle_region, world, game_state, had_garrison=True
                    )
                    if capture_result["captured"]:
                        conquered = True
                        conquest_msg = f" {charge_battle_region} has been captured by {marshal.nation}!"
                    elif capture_result.get("occupation_started"):
                        conquest_msg = f" {capture_result['message']}"

        # R1 Pipeline: centralized post-combat recording
        charge_outcome = combat_result.get("outcome", "")
        charge_atk_won = "attacker" in charge_outcome and "victory" in charge_outcome
        charge_def_won = "defender" in charge_outcome and "victory" in charge_outcome
        charge_atk_cas = int(combat_result.get("attacker", {}).get("casualties", 0))
        charge_def_cas = int(combat_result.get("defender", {}).get("casualties", 0))

        pipeline_out = self._post_combat_pipeline({
            'attacker': marshal,
            'defender': target_marshal,
            'battle_region': charge_battle_region,
            'outcome': charge_outcome,
            'attacker_won': charge_atk_won,
            'defender_won': charge_def_won,
            'attacker_casualties': charge_atk_cas,
            'defender_casualties': charge_def_cas,
            'pre_battle_attacker_strength': pre_battle_atk,
            'pre_battle_defender_strength': pre_battle_def,
            'battle_result': combat_result,
            'conquered': conquered,
            'is_glorious_charge': True,
        }, world)

        # Clear the CHARGE ORIGIN's coordination too. The charge computed
        # coordination while the marshal was still in origin (stamping transient
        # bonuses on co-located allies), then advanced away — so the pipeline's
        # {attacker.location, battle_region} clear (attacker.location is now the
        # destination) would leave origin allies holding a stale bonus that a later
        # garrison assault reads without recomputing.
        if charge_origin_region not in (charge_battle_region, target_marshal.location):
            self._clear_coordination_fields({charge_origin_region}, world)

        vindication_msg = pipeline_out.get('vindication_msg', '')

        # Build charge message - use "description" key from combat resolver
        charge_message = f"[Cavalry][Combat] GLORIOUS CHARGE! {marshal.name} leads a devastating cavalry assault!\n\n"
        charge_message += combat_result.get("description", "")
        charge_message += enemy_destroyed_msg + movement_msg
        if forced_retreat_msg:
            charge_message += forced_retreat_msg
        if conquest_msg:
            charge_message += conquest_msg
        if vindication_msg:
            charge_message += vindication_msg
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
        # Flag pending capture choice for popup
        if world.pending_capture_choice:
            charge_result["pending_capture_choice"] = True
            charge_result["capture_data"] = world.pending_capture_choice
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
                if m.location == target and m.nation != pending_marshal.nation and world.is_at_war(pending_marshal.nation, m.nation):
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

    # ════════════════════════════════════════════════════════════════════════════════
    # AUTO-DISPATCH COMBAT METHODS (R10B)
    # General attack, auto-assign attack/bombardment, general retreat/defensive.
    # Extracted from executor.py in R10B (Architecture Refactoring Session 10B).
    # ════════════════════════════════════════════════════════════════════════════════

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
                closest_marshal.move_to(next_region)

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
        target_region, error = self._executor._fuzzy_match_region(target, world)

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
            target_region, error = self._executor._fuzzy_match_region(target, world)
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
        return self._executor._execute_specific(routed_command, game_state)

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
            result = self._executor._execute_retreat_action(marshal, world, game_state)
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

