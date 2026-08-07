"""
Combat Executor for Project Sovereign
Handles all combat-related execution: attack, charge, bombardment, garrison.

Extracted from executor.py in R10A (Architecture Refactoring Session 10A).
"""
import re
from typing import Dict, Optional
from backend.models.world_state import (
    PLUNDER_INCOME_MULTIPLIER as WS_PLUNDER_INCOME_MULTIPLIER,
    WorldState,
)
from backend.models.marshal import Marshal
from backend.models.region import CHARGE_BLOCKED_TERRAIN, TERRAIN_DEFENSE_BONUS
from backend.game_logic.combat import FORCED_RETREAT_THRESHOLD
from backend.game_logic.formations import formed_display_name


# ════════════════════════════════════════════════════════════════════════════
# ESP-EV-4 guessed-target guard (July 11, 2026; hoisted + re-surfaced July 18,
# 2026)
#
# A LETHAL order never fires at a parser-GUESSED target. Live-LLM parses can
# substitute a real enemy or region for a name the player wrote that our maps
# do not know ("attack Venetia" -> Archduke John at Tyrol, live). When the raw
# text is available (direct typed player attacks only — AI, strategic execution
# and muster re-issues carry no raw text) and it names NEITHER the parsed target
# NOR anything the resolution produced, the target is a guess: ask, never
# default-scan (the BUG-CA-3 / W6-1 rule, applied to the attack path).
#
# July 18, 2026 — WHY THIS IS A FUNCTION NOW. It used to be an inline block
# sitting AFTER the range-check / PURSUE-upgrade block, which returns early. So
# a guessed target that happened to be out of range was silently converted into
# a strategic PURSUE and marched off before the guard ever ran — the playtest
# report ("Ney, give Charles hell" opened a bad-odds popup over Mack, an enemy
# the player never named") is exactly that hole. Extracting it lets the SAME
# implementation run at both lethal seams (the cavalry-recklessness early
# return and the main resolution path) without a second copy drifting.
# ════════════════════════════════════════════════════════════════════════════

_GUARD_FILLER_WORDS = frozenset({
    "the", "a", "an", "at", "on", "to", "of", "and", "with", "his",
    "her", "their", "them", "him", "near", "nearest", "closest",
    "nearby", "enemy", "enemies", "foe", "foes", "force", "forces",
    "army", "armies", "troops", "whoever", "whatever", "that",
    "is", "in", "range", "guns", "sound", "adjacent", "position",
    "garrison", "defenders", "defender", "corps", "sire", "please",
    "go", "now", "immediately", "there", "yonder",
    # Quantifiers / collectives: these name no FOE, so an order carrying only
    # these is still a delegation ("attack them all" — pinned by CR-6).
    #
    # Kept deliberately SHORT. Words like "any"/"both"/"each"/"one"/"rest"/
    # "else" were tried and removed: the parser fuzzy-matches several of them
    # into real map entities, so listing them here disarms the guard on exactly
    # the inputs where a province was fabricated from them.
    "all", "every", "everyone", "them", "anything", "everything",
})


def guessed_target_refusal(world, marshal, command, target,
                           resolved_target=None, enemy_candidates=(),
                           auto_resolved: bool = False) -> Optional[Dict]:
    """Decide what to do when the player's own words ground NOTHING the
    resolution produced.

    Returns a clarification/refusal response to return instead of attacking,
    or None to proceed. When it proceeds after an ungrounded ENGINE pick it
    stamps ``command["_target_disclosure"]`` so the caller can tell the player
    which foe was chosen.

    ``enemy_candidates`` are the marshals resolution produced (any may be
    None); their name/location/nation all count as grounding.

    ``auto_resolved`` is the load-bearing distinction, and the July 18, 2026
    adversarial review is why it is back after a first cut deleted it:

      auto_resolved=False — the PARSER produced a concrete target and the
        player's words ground none of it ("attack Venetia" -> Archduke John).
        A silent substitution of one real foe for another. ASK. This is the
        original ESP-EV-4 case and it is unchanged.

      auto_resolved=True — the parse handed down target=None and the ENGINE
        picked the nearest visible enemy. Refusing here was a REGRESSION the
        review caught before it shipped: "Ney, attack the weakest enemy",
        "attack the enemy vanguard" and "attack the British army" are ordinary
        delegations whose descriptive words happen not to be on any filler
        list, and they would all have been bounced to a popup. The set of
        words a player might use to describe a foe is not enumerable, so the
        guard must not depend on enumerating it. Instead the order PROCEEDS
        and the choice is DISCLOSED — which also covers the live-probe case
        that prompted the change ("give Charles hell" mustering against Mack):
        the attack is no longer silent, so the player is never misled, and no
        legitimate order is ever blocked.
    """
    raw = str((command or {}).get("_raw_input") or "").lower()
    if not raw or not target:
        return None
    if (command or {}).get("_auto_assigned"):
        return None

    from backend.display_names import humanize_entity_name
    from backend.ai.attack_vocabulary import (
        guard_attack_verbs, IDIOM_FILLER_WORDS)

    # The player's OWN target words: the raw order stripped of the marshal's
    # name, attack verbs and generic filler. If nothing specific remains
    # ("Ney, attack the nearest enemy"), the player DELEGATED the choice —
    # never a guess. The guard only defends against a SPECIFIC name the player
    # typed that resolution silently overrode.
    #
    # IDIOM_FILLER_WORDS is included so the colloquial attack idioms landed
    # July 18, 2026 read as delegation rather than as a named target: in
    # "Ney, give them hell" the words "give"/"hell" name no foe, so the order
    # is a delegated attack, not a guess at a province called Hell.
    skip = (guard_attack_verbs() | _GUARD_FILLER_WORDS | IDIOM_FILLER_WORDS
            | {marshal.name.lower()})
    raw_target_words = [
        w for w in re.findall(r"[a-z']+", raw)
        if w not in skip and len(w) >= 3
    ]

    def _named_in_raw(token) -> bool:
        token = str(token or "")
        if not token:
            return False
        tl = token.lower()
        hum = humanize_entity_name(token).lower()
        if tl in raw or hum in raw:
            return True
        # Word-level grounding: a partial name or title the player DID type
        # stands in for the resolved token ("John" / "the Archduke" ground
        # "Archduke John") — but a full substitution ("Venetia") grounds none
        # of Archduke John / Tyrol / Austria.
        for w in raw_target_words:
            if len(w) >= 4 and (w in tl or w in hum):
                return True
        return False

    # No specific words at all => a plain delegation ("Ney, attack", "attack
    # them all", "give them hell") => let it fly, silently. CR-6 / S5-D1.
    if not raw_target_words or _named_in_raw(target):
        return None

    resolved_tokens = []
    if resolved_target and resolved_target != target:
        resolved_tokens.append(resolved_target)
    for enemy in enemy_candidates:
        if enemy is not None:
            resolved_tokens += [enemy.name, enemy.location, enemy.nation]
    if any(_named_in_raw(t) for t in resolved_tokens):
        return None

    # The player said something specific and it grounds nothing.
    if auto_resolved:
        # The ENGINE picked. Proceed, but say so — see the docstring for why
        # refusing here is wrong. Disclosure is stamped on the command so the
        # attack path can prepend it to whatever it produces (muster preview,
        # battle report, block message), rather than manufacturing a second
        # response shape here.
        chosen = None
        for enemy in enemy_candidates:
            if enemy is not None:
                chosen = enemy
                break
        if command is not None and chosen is not None:
            command["_target_disclosure"] = (
                f"Your words named no foe our maps know, Sire — "
                f"{marshal.name} marches on "
                f"{humanize_entity_name(chosen.name)} at "
                f"{humanize_entity_name(chosen.location)}, the nearest in "
                f"sight. Name another and he will turn."
            )
        return None

    # The PARSER substituted one real foe for the name the player typed. Ask.
    visible = world.get_visible_enemies(marshal.nation)
    # Prefer the answerable clarification (options the player can click OR type
    # back). It reissues a fully-formed named attack, so the answer runs the
    # ordinary pipeline instead of re-entering the guess just refused.
    from backend.commands.clarification import build_attack_target_clarification
    ask = build_attack_target_clarification(world, marshal, visible,
                                            (command or {}).get("_raw_input") or "")
    if ask is not None:
        return ask

    # Nothing visible to offer (or the answer is unaffordable) — keep the
    # honest refusal rather than an empty question.
    # R7: humanized for player copy — no raw camelCase key reaches the terminal.
    seen = ", ".join(
        f"{humanize_entity_name(e.name)} at {humanize_entity_name(e.location)}"
        for e in visible[:6]) or "none in sight"
    return {
        "success": False,
        "message": (
            f"Your order names no foe or province our maps know, Sire — "
            f"{marshal.name} will not charge at a guess. "
            f"Visible enemies: {seen}."
        ),
    }


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

    # CO-1 (Combat Overhaul Phase 1, spec §0.3 G-1): committed reinforcing
    # corps add STRENGTH to the clash, not just a capped coordination %.
    # Each reinforcer's contribution is α · strength · effectiveness ·
    # attack_modifier · relationship_factor (CO-1b). α is the sweep-tuned
    # discount (Sweep 1a; a reinforcer is worth ~α·attack_mult of its raw
    # strength relative to leading its own corps). Single source, read by
    # both the resolution path and the muster odds band (CO-2).
    COMMITTED_ALPHA = 0.6

    def _committed_reinforcement_strength(self, lead, participants, world) -> float:
        """CO-1/CO-1b: additive committed strength a lead's reinforcers bring
        to the clash (everyone in `participants` except the lead).

        Each reinforcer's contribution (spec §0.3 G-1b):

            α · r.strength · r.get_combat_effectiveness()
              · r.get_attack_modifier(1.0, consume=False) · rel_factor

        where get_attack_modifier is READ (consume=False — no one-time bonus is
        spent; GR1 single source, never recomputed here) and rel_factor is the
        MC-3 relationship scale toward the lead (_RELATIONSHIP_SCALING: ×0.0
        hostile … ×1.5 devoted), matching the live-grievance withholding the
        coordination path uses (_calculate_per_ally_coordination): an aggressive
        grievance is a hard 0.0, a non-aggressive one reads the worse direction.

        An aggressive/high-shock reinforcer pushes harder than a cautious one of
        equal size; a marshal who resents the lead contributes ≈0. Returns a
        float (0.0 when the lead fights alone).
        """
        total = 0.0
        for r in participants:
            if r is lead or r.name == lead.name:
                continue
            if getattr(r, "strength", 0) <= 0:
                continue

            rel = lead.get_relationship(r.name)
            scale = self._RELATIONSHIP_SCALING.get(rel, 1.0)

            # Jealousy v3.2 withholding — mirror _calculate_per_ally_coordination
            # so committed mass and coordination read the same grievance.
            lead_jealous = getattr(lead, "jealous_of", None) == r.name
            r_jealous = getattr(r, "jealous_of", None) == lead.name
            if lead_jealous or r_jealous:
                jealous_one = lead if lead_jealous else r
                if jealous_one.personality == "aggressive":
                    scale = 0.0
                else:
                    pair_rel = min(lead.get_relationship(r.name),
                                   r.get_relationship(lead.name))
                    scale = self._RELATIONSHIP_SCALING.get(pair_rel, 1.0)

            if scale <= 0.0:
                continue

            eff = r.get_combat_effectiveness()
            atk_mult = r.get_attack_modifier(1.0, consume=False)
            total += self.COMMITTED_ALPHA * r.strength * eff * atk_mult * scale

        return total

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

            # Jealousy v3.2 (spec §0.2 item 3): while either marshal of the
            # pair is jealous of the other, the pair's coordination reads
            # through the WORSE direction (the jealous one withholds his
            # commitment) — and an AGGRESSIVE grievance is a hard 0.0
            # ("refuses to cooperate", spec §3). Authored MC-3 values are
            # symmetric, so nothing changes outside a live grievance.
            marshal_jealous = getattr(marshal, 'jealous_of', None) == ally.name
            ally_jealous = getattr(ally, 'jealous_of', None) == marshal.name
            if marshal_jealous or ally_jealous:
                jealous_one = marshal if marshal_jealous else ally
                if jealous_one.personality == "aggressive":
                    scale = 0.0
                else:
                    pair_rel = min(marshal.get_relationship(ally.name),
                                   ally.get_relationship(marshal.name))
                    scale = self._RELATIONSHIP_SCALING.get(pair_rel, 1.0)

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
        # Rule 1b (VS-4, VASSAL_DEEPENING_SPEC §5): an assimilated ex-vassal
        # contingent whose homeland wavers (loyalty < 60) is withheld from
        # AUTO-reinforcement — loyalty has military teeth. Mirrors the A-D4
        # hostile pattern: an explicit SUPPORT order for the primary (a
        # direct player order) still brings him — refusal is about the
        # call-to-arms, never command defiance.
        origin = getattr(marshal, 'original_nation', None)
        if origin:
            vassals = getattr(world, 'vassals', {})
            if origin in vassals and vassals[origin].get("lord") == nation:
                from backend.game_logic.vassal import vassal_military_contribution
                if vassal_military_contribution(world, origin) != "loyal":
                    # Post-build review C4: "the written word" is EITHER an
                    # explicit SUPPORT for the primary OR a PURSUE whose
                    # quarry stands in the battle region — byte-mirroring
                    # the Grouchy-rule predicate the muster preview uses,
                    # so shown always equals applied (refusal is about the
                    # call-to-arms, never command defiance).
                    order = getattr(marshal, 'strategic_order', None)
                    has_written_word = False
                    if order is not None:
                        if (order.command_type == "SUPPORT"
                                and order.target == primary.name):
                            has_written_word = True
                        elif order.command_type == "PURSUE":
                            pursue_target = world.marshals.get(order.target)
                            if (pursue_target is not None
                                    and pursue_target.location == battle_region):
                                has_written_word = True
                    if not has_written_word:
                        return False
        # Rule 2: Adjacent region (not same region, not distant)
        if marshal.location not in region.adjacent_regions:
            return False
        # Rule 2b (DEF-5 naval §4.1): a reinforcing corps cannot cross a
        # sea link a hostile fleet covers — the RN interdicts the muster.
        if getattr(world, "fleets", None):
            from backend.game_logic.naval import crossing_allowed
            if not crossing_allowed(world, marshal.nation,
                                    marshal.location, region.name):
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

    # ════════════════════════════════════════════════════════════════════
    # W6-4 MUSTER PREVIEW (EXP-C1 + E-CA-4)
    # ════════════════════════════════════════════════════════════════════

    def _muster_reason(self, candidate, primary, battle_region, nation, world):
        """W6-4: derive (will_join, reason_code) for a nearby friendly.

        Mirrors _is_reinforcement_eligible + the Grouchy Rule as a REASON
        ladder — display only, the mechanics stay in their own functions.
        """
        # Co-located friendlies share the field (and the casualties).
        if candidate.location == battle_region:
            return True, "shares_the_field"
        # NV-9 (shown = applied): reinforcement Rule 2b refuses a corps
        # across a covered sea link, but this ladder had no naval arm —
        # so the muster preview listed a corps as ANSWERING THE GUNS that
        # the crossing gate then silently withheld. Newly common because
        # NV-5's expedition puts armies on the far side of water: a corps
        # landed at Normandy fights while London's garrison is "coming".
        # Sited above every will-join arm, including has_support_order,
        # because a SUPPORT order does not override Rule 2b either.
        if getattr(world, "fleets", None):
            from backend.game_logic.naval import crossing_allowed
            if not crossing_allowed(world, nation, candidate.location,
                                    battle_region):
                return False, "sea_barred"
        if getattr(candidate, 'broken', False) \
                or getattr(candidate, 'retreat_recovery', 0) != 0 \
                or getattr(candidate, 'retreated_this_turn', False):
            return False, "broken_recovering"
        if getattr(candidate, 'fortified', False):
            return False, "fortified_static"
        if getattr(candidate, 'holding_position', False):
            return False, "holding_position"
        if getattr(candidate, 'drilling', False) \
                or getattr(candidate, 'drilling_locked', False):
            return False, "drilling"
        if getattr(candidate, 'square_formation', False):
            return False, "square_formation"
        if getattr(candidate, 'reinforced_this_turn', False) \
                or getattr(candidate, 'moved_this_turn', False):
            return False, "cooldown_spent"
        # Engaged: enemies stand in the candidate's own region.
        engaged = any(
            m.location == candidate.location and m.nation != nation
            and m.strength > 0 and world.is_at_war(nation, m.nation)
            for m in world.marshals.values()
        )
        if engaged:
            return False, "engaged"
        # Relevant standing order (SUPPORT for the primary / PURSUE into
        # the battle region) authorizes anyone — including a literal.
        order = getattr(candidate, 'strategic_order', None)
        has_relevant_order = False
        if order is not None:
            if order.command_type == "SUPPORT" and order.target == primary.name:
                has_relevant_order = True
            elif order.command_type == "PURSUE":
                pursue_target = world.marshals.get(order.target)
                if pursue_target and pursue_target.location == battle_region:
                    has_relevant_order = True
        if has_relevant_order:
            return True, "has_support_order"
        # VS-4 (paired with reinforcement Rule 1b — shown = applied): an
        # assimilated ex-vassal contingent whose homeland wavers will not
        # answer the muster without the written word.
        origin = getattr(candidate, 'original_nation', None)
        if origin:
            vassals = getattr(world, 'vassals', {})
            if origin in vassals and vassals[origin].get("lord") == nation:
                from backend.game_logic.vassal import vassal_military_contribution
                if vassal_military_contribution(world, origin) != "loyal":
                    return False, "vassal_wavering"
        # The Grouchy Rule: a literal marshal without the written word
        # does not march to the sound of the guns.
        if getattr(candidate, 'personality', '') == "literal":
            return False, "literal_awaits_orders"
        # Hostile without SUPPORT refuses (A-D4).
        if candidate.get_relationship(primary.name) == -2:
            return False, "hostile_refuses"
        # MC-1 honest muster arms (W6-4 — the preview must never lie):
        # Roland's +15 makes his arrival near-certain; Eyes on a Crown's -15
        # means Bernadotte usually does NOT come without the written word.
        # Review fix: the hard "WILL NOT" holds only while his relationship
        # with the primary is <= 0 (at +1 friendship the arrival roll turns
        # genuinely winnable, so he falls through to the hedged generic arm
        # — mirrors how the ladder already consults hostility above).
        _ability_name = (candidate.ability.get("name", "")
                         if hasattr(candidate, 'ability') else "")
        if _ability_name == "Roland of the Army":
            return True, "roland_marches"
        if (_ability_name == "Eyes on a Crown"
                and candidate.get_relationship(primary.name) <= 0):
            return False, "eyes_on_a_crown"
        if getattr(candidate, 'personality', '') == "aggressive":
            return True, "aggressive_marches"
        return True, "answers_the_guns"

    def _build_muster_preview(self, marshal, enemy_marshal, world, game_state):
        """W6-4 §6.1: who will fight, who won't, and why — before the shot.

        Fog-legal target strength (exact only at FULL visibility, else the
        band — R5); odds band via the CR-5 single source (GR1 spirit); one
        row per adjacent/co-located friendly with a display reason.
        """
        from backend.commands.objection_v2 import inferred_attack_odds_band
        from backend.display_names import MUSTER_REASON_DISPLAY
        from backend.models.intel import FULL

        battle_region = enemy_marshal.location
        nation = marshal.nation

        # Fog-banded target strength (player's own intel of that region).
        target_strength_display = self._fog_banded_strength(enemy_marshal, world)

        rows = []
        shared_casualty_note = ""
        will_join_marshals = []
        region = world.get_region(battle_region)
        adjacent = set(region.adjacent_regions) if region else set()
        for m in world.marshals.values():
            if m.nation != nation or m.name == marshal.name or m.strength <= 0:
                continue
            if m.location != battle_region and m.location not in adjacent:
                continue
            will_join, code = self._muster_reason(
                m, marshal, battle_region, nation, world)
            if will_join:
                will_join_marshals.append(m)
            row = {
                "marshal": m.name,
                "location": m.location,
                "will_join": bool(will_join),
                "reason": code,
                "reason_display": MUSTER_REASON_DISPLAY.get(code, code),
            }
            if code == "literal_awaits_orders":
                # §6.3: surface the standing order that already exists.
                row["standing_order_hint"] = (
                    f"— order '{m.name}, support {marshal.name}' and he will march"
                )
            if code == "eyes_on_a_crown":
                # MC-1: the counter-lever must be discoverable — put the
                # order in writing and he mostly comes.
                row["standing_order_hint"] = (
                    f"— a written order ('{m.name}, support {marshal.name}') "
                    f"would likely bring him"
                )
            if code == "shares_the_field":
                shared_casualty_note = (
                    f"{m.name} shares the field at {battle_region} — his men "
                    f"will absorb part of any losses."
                )
            rows.append(row)

        # CO-2: the odds band reflects the TOTAL committed force (lead + the
        # personality/relationship-scaled contribution of every marshal that
        # WILL JOIN) so the preview matches what CO-1 resolves.
        committed_attacker = self._committed_reinforcement_strength(
            marshal, will_join_marshals, world)
        odds_band = inferred_attack_odds_band(
            marshal, enemy_marshal, game_state,
            committed_attacker=committed_attacker)

        preview = {
            "attacker": {"name": marshal.name,
                         "strength": int(marshal.strength),
                         "committed_strength": int(marshal.strength + committed_attacker)},
            "target": {"name": enemy_marshal.name,
                       "location": battle_region,
                       "strength_display": target_strength_display},
            "odds_band": odds_band,
            "rows": rows,
            "shared_casualty_note": shared_casualty_note,
        }

        # First-use tutorial line about standing orders — latch-on-surface
        # (shown once per campaign, even if this attack is then cancelled).
        if not getattr(world, 'muster_hint_shown', False):
            world.muster_hint_shown = True
            preview["hint"] = (
                "Standing orders decide who marches: 'Soult, support Ney' "
                "authorizes even a literal marshal to move to his guns."
            )
        return preview

    def _bad_odds_muster_note(self, marshal, enemy, world) -> str:
        """PC-8 (quiet-France played campaign, Aug 3 2026): the staff's
        addendum to a delegation-inferred bad-odds warning.

        The CR-5 gate prices the acting marshal's SOLO strength, and that is
        correct and stays: it is *his* reading of *his* corps against a dug-in
        enemy, and re-pricing it on the joint force flips the canonical case
        from unfavorable to favorable (solo ratio 0.6705 → joint 1.0297) and
        breaks the pin that makes the gate reachable at all. What was wrong is
        that the modal then said "in greater strength" and stopped — while on
        `press on` the muster committed two more corps and the battle was
        fought at ~68k against 52k. The player was deciding without the one
        fact that decided it.

        So the marshal's read is left alone and Berthier appends what the
        marshal cannot see: who will march, and the figure they make together.
        Reads the SAME muster ladder the attack path's preview does
        (`_muster_reason` → `_committed_reinforcement_strength`), so the two
        surfaces cannot drift. Returns "" when nobody would answer.

        Player-nation only — the muster preview's own call site carries the
        same guard (`marshal.nation == world.player_nation`), and this is
        copy on a modal only the player ever sees.
        """
        if world is None:
            return ""
        if marshal.nation != getattr(world, "player_nation", "France"):
            return ""
        battle_region = enemy.location
        region = world.get_region(battle_region)
        adjacent = set(region.adjacent_regions) if region else set()
        will_join = []
        for m in world.marshals.values():
            if (m.nation != marshal.nation or m.name == marshal.name
                    or m.strength <= 0):
                continue
            if m.location != battle_region and m.location not in adjacent:
                continue
            joins, _code = self._muster_reason(
                m, marshal, battle_region, marshal.nation, world)
            if joins:
                will_join.append(m)
        if not will_join:
            return ""
        committed = self._committed_reinforcement_strength(
            marshal, will_join, world)
        if committed <= 0:
            return ""
        # Same prose form the coordination observations use — one source for
        # "A", "A and B", "A, B and C".
        from backend.game_logic.battle_report import _join_names
        names = _join_names([m.name for m in will_join])
        joint = int(marshal.strength + committed)
        # ════════════════════════════════════════════════════════════════
        # CA8-4 (creative audit, Aug 4 2026): this is the game's FIRST
        # modal, and it inverted its own meaning. It read
        #   "...would answer the guns — 82,072 in all, against 24,000 of
        #    Ney's own."
        # Read cold, "against" says the ENEMY has 82,072 — and the
        # preceding clause, the marshal's own "Mack stands dug in and in
        # greater strength", confirms the misreading. Both numbers were
        # French, and Mack's was never printed at all.
        #
        # The readable form already existed one surface away — the muster
        # preview's "Massena (21,606; 48,765 with the muster committed) vs
        # ArchdukeJohn (16,543 men)". This now uses it, and takes the
        # enemy figure through the SAME fog-banded helper the preview does,
        # so a fogged enemy reads as its band and never as a leak.
        # ════════════════════════════════════════════════════════════════
        target_display = self._fog_banded_strength(enemy, world)
        return (f" Berthier adds: {names} would answer the guns — "
                f"{marshal.name} {int(marshal.strength):,}, "
                f"{joint:,} with the muster committed, against "
                f"{enemy.name} ({target_display}).")

    @staticmethod
    def _fog_banded_strength(enemy_marshal, world) -> str:
        """Player-honest strength display for an enemy marshal.

        FULL visibility gives the exact count; anything less gives the
        intel band ("substantial force"), and no intel at all gives
        "strength unknown". Single source (CA8-4) so the bad-odds
        interrupt and the muster preview cannot drift or leak.
        """
        from backend.models.intel import FULL
        intel = world.intel.get(enemy_marshal.location) if world else None
        if intel is None:
            return "strength unknown"
        if intel.visibility == FULL:
            return f"{int(enemy_marshal.strength):,} men"
        for km in intel.known_marshals:
            if km.get("name") == enemy_marshal.name and km.get("band"):
                return km["band"]
        if intel.strength_band and intel.strength_band != "no forces":
            return intel.strength_band
        return "strength unknown"

    def _format_muster_lines(self, preview) -> str:
        """Compact text render of the muster block (1 line per marshal)."""
        # PT-D1: the odds band is priced on the COMMITTED joint force
        # (CO-2), so when reinforcers commit, the header must name that
        # figure — otherwise "looks favorable" beside a weaker solo count
        # reads as a contradiction with the personality line's solo frame.
        attacker_display = f"{preview['attacker']['strength']:,}"
        committed = int(preview['attacker'].get(
            'committed_strength', preview['attacker']['strength']))
        if committed > preview['attacker']['strength']:
            attacker_display += f"; {committed:,} with the muster committed"
        lines = [
            f"MUSTER — {preview['attacker']['name']} "
            f"({attacker_display}) vs "
            f"{preview['target']['name']} "
            f"({preview['target']['strength_display']}) at "
            f"{preview['target']['location']} — the balance of force looks "
            f"{preview['odds_band']}."
        ]
        for row in preview["rows"]:
            verdict = "WILL JOIN" if row["will_join"] else "WILL NOT"
            line = f"  {verdict} — {row['marshal']}: {row['reason_display']}"
            if row.get("standing_order_hint"):
                line += f" {row['standing_order_hint']}"
            lines.append(line)
        if preview.get("shared_casualty_note"):
            lines.append(f"  {preview['shared_casualty_note']}")
        if preview.get("hint"):
            lines.append(f"  ({preview['hint']})")
        return "\n".join(lines)

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

        # MC-1 signature abilities: the Lannes/Bernadotte arrival mirror.
        # Roland of the Army +15 ("marches to the sound of the guns");
        # Eyes on a Crown -15 (the I Corps does not always march — the
        # SUPPORT +10 above is the built-in counter-lever).
        ability_mod = 0
        ability_name = ""
        if hasattr(reinforcing_marshal, 'ability'):
            ability_name = reinforcing_marshal.ability.get("name", "")
        if ability_name == "Roland of the Army":
            ability_mod = 15
        elif ability_name == "Eyes on a Crown":
            ability_mod = -15

        variance = random.randint(-8, 8)

        return (base + logistics_bonus + rel_mod + terrain_mod + personality_mod
                + support_bonus + ability_mod + variance)

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
                    # W6-5: the no-march line lives in the literal voice
                    # bank so all literal copy shares one register.
                    from backend.game_logic.marshal_voice import literal_no_march
                    reinforcement_results.append({
                        "marshal": candidate.name,
                        "arrived": False,
                        "score": None,
                        "threshold": None,
                        "reason": "literal_personality",
                        "near_miss": False,
                        "near_miss_reason": "",
                        "has_explicit_order": False,
                        "message": literal_no_march(
                            candidate.name, int(world.current_turn)),
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
                # MC-1 review fix: Bernadotte's ability-driven no-show is
                # by-design character (like the literal no-march), not a
                # logistics failure — classify it honestly so the failure
                # copy and the Session-61a trust seam treat it as such.
                # A failed arrival UNDER a written SUPPORT order stays
                # "low_score" (the player ordered him and was stood up).
                if (not has_explicit_order and hasattr(candidate, 'ability')
                        and candidate.ability.get("name") == "Eyes on a Crown"):
                    reason = "eyes_on_a_crown"

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

    # Transient coordination field names for cleanup after combat (D5 + X1).
    # CA8-19(i): the names now live on Marshal — the object that carries the
    # fields — so this list and Marshal.clear_combat_transient_state cannot
    # drift. Kept as a class attribute because it is pinned by name
    # (tests/test_auto_bombardment_overwatch.py).
    _COORDINATION_FIELDS = list(Marshal.COORDINATION_TRANSIENT_FIELDS)

    def _clear_coordination_fields(self, regions: set, world: WorldState) -> None:
        """Clear all transient coordination fields from marshals in the given regions."""
        for m in world.marshals.values():
            if m.location in regions:
                m.clear_coordination_transients()

    def _naval_advance_allowed(self, marshal, destination: str, world) -> bool:
        """NV-9 — may this marshal ADVANCE onto `destination` after a
        battle? One seam for every post-combat move (the attack advance,
        the charge advance, the pursuit), so no victory can carry an army
        over water its enemy commands. Reads the host rule too: a beaten
        garrison does not make a defended shore friendly."""
        if not getattr(world, "fleets", None):
            return True
        if marshal.location == destination:
            return True
        from backend.game_logic.naval import crossing_check_reach
        return crossing_check_reach(
            world, marshal.nation, marshal.location, destination)["allowed"]

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
    def _reconcile_report_survivors(battle_result, lead, defender) -> None:
        """CO-5 (Combat Overhaul Phase 1): single-source the survivor count.

        In a coordinated battle resolve_battle builds the battle report from the
        LEAD-vs-lead casualties (battle_report derives attacker_remaining =
        original − whole-corps casualties), while the caller sets the event's
        `remaining` to the lead's strength AFTER distributing the total across
        all participants — so the report and the event disagreed in every
        multi-marshal battle (the "two-truths" bug, spec §3.1 / metric M4).

        Call this AFTER casualties have been distributed and applied (lead and
        defender strengths are final for the clash, before pursuit): both the
        report's casualty_summary and the event now read ONE canonical value —
        the lead's / defender-primary's actual post-battle strength. Reinforcer
        losses continue to be reported separately (reinforcement_messages).
        """
        report = battle_result.get("battle_report")
        if not isinstance(report, dict):
            return
        cs = report.get("casualty_summary")
        if not isinstance(cs, dict):
            return
        a_orig = int(cs.get("attacker_original", getattr(lead, "strength", 0)))
        d_orig = int(cs.get("defender_original", getattr(defender, "strength", 0)))
        a_remaining = int(getattr(lead, "strength", 0))
        d_remaining = int(getattr(defender, "strength", 0))
        cs["attacker_remaining"] = a_remaining
        cs["attacker_casualties"] = max(0, a_orig - a_remaining)
        cs["defender_remaining"] = d_remaining
        cs["defender_casualties"] = max(0, d_orig - d_remaining)

    @staticmethod
    def _rewrite_primary_casualties(description, atk_name, atk_raw, atk_share,
                                    def_name, def_raw, def_share):
        """Attribute a coordinated battle's casualties to the ARMY, not the man.

        resolve_battle formats the casualty line before the caller distributes
        casualties across participants, so it names the primary marshal with
        the entire corps' losses. This corrects the printed line for both the
        "Casualties: <name> <n>" (tactical/stalemate) and "suffered <n>
        casualties" (decisive-victory) templates.

        ────────────────────────────────────────────────────────────────────
        CA8-1 (creative audit, Aug 4 2026) — CONSCIOUS FLIP of the F1a fix
        (playtest bug audit, Jul 6 2026).

        F1a saw `Casualties: Ney 8,141` when Ney personally lost 2,171 and
        rewrote the figure DOWN to the primary's distributed share. That
        fixed the false personal attribution by breaking something worse:
        the terminal and the campaign log then reported the same battle's
        French casualties as `Ney 13` and `197` — a 15x disagreement,
        reproduced on every coordinated battle of the played campaign
        (`13,255/113` vs `13,255/514`; `Davout 56` vs `280`). A player who
        notices two casualty figures for one battle stops trusting every
        number in the game, including the true ones.

        Both readings were right about the defect and wrong about the fix:
        the number was never the problem, the possessive was. So the figure
        goes back to the whole-army total the log already prints, and the
        line names the army that took it. The per-marshal breakdown is
        carried by reinforcement_messages ("his supporting allies lost N"),
        now emitted for BOTH sides, so the parts still sum to the whole and
        nothing is double-counted.

        A side that fielded one corps has raw == share and is untouched —
        a solo battle still reads as the man.
        ────────────────────────────────────────────────────────────────────
        """
        if not description:
            return description
        for name, raw, share in ((atk_name, atk_raw, atk_share),
                                 (def_name, def_raw, def_share)):
            if raw == share:
                continue
            description = description.replace(
                f"{name} {raw:,}", f"{name}'s army {raw:,}")
            description = description.replace(
                f"{name} suffered {raw:,} casualties",
                f"{name}'s army suffered {raw:,} casualties")
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
                coordination_regions (iterable): extra regions the
                    coordination stamp was computed over — required when the
                    attacker has already advanced before this call

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
        # CA8-19(i): `attacker.location` is only the stamped region while the
        # attacker has not moved yet. Paths that advance BEFORE calling the
        # pipeline (the auto-bombardment-kill exit) must name the region the
        # stamp was computed over via `coordination_regions`, or the origin's
        # allies keep a bonus nothing will ever clear.
        if not ctx.get('skip_coordination_clear'):
            involved = {attacker.location, battle_region}
            involved.update(ctx.get('coordination_regions') or ())
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

        # ── 9.5 Jealousy battle resolution (v3.2, EC-F) ──
        # A grievance this battle satisfies clears BEFORE the Win/Loss
        # relationship step so the derived -1 restores first. Participant
        # sets mirror step 10's (relationship.get_battle_participants).
        jealousy_atk_parts = None
        jealousy_def_parts = None
        if (not is_bombardment and not is_auto_kill and not is_garrison
                and battle_result and not ctx.get('skip_jealousy')):
            from backend.game_logic import jealousy as _jealousy
            from backend.game_logic.relationship import get_battle_participants
            jealousy_atk_parts = get_battle_participants(
                attacker, battle_region, attacker.nation, world)
            jealousy_def_parts = get_battle_participants(
                defender, battle_region, defender_nation, world) if defender else []
            _jealousy.check_battle_resolution(
                world, attacker, defender, attacker_won, defender_won,
                int(pre_atk), int(pre_def),
                attacker_participants=jealousy_atk_parts,
                defender_participants=jealousy_def_parts,
                defender_broken=bool(defender and getattr(defender, 'broken', False)))

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

        # ── 10.5 Glory recording + §6b rivalry transitions (v3.2) ──
        # AFTER relationships (spec §0.2 item 4). Primaries score the full
        # formula, participants base ±1. NOTE: the main attack path runs its
        # relationship processing inline BEFORE this pipeline call
        # (skip_relationships=True) — glory here is still strictly after it.
        #
        # CA8-19(ii): `not is_garrison` is now STATED, and it replaces a
        # discriminator that could never be true. Spec §1 authors "Garrison
        # stomp: +0 (defeating a garrison — no glory in that)", and §0.2 item 4
        # implemented that as an `is_garrison` argument to record_battle_glory.
        # No production call site could ever supply it: both garrison ctxs pass
        # `battle_result: None` (the path never calls resolve_battle), so this
        # guard's `battle_result` term already excluded them — the exemption
        # was satisfied by accident, and the argument was dead from the commit
        # that introduced it. A garrison assault is outside the glory ladder in
        # BOTH directions, which is a stronger rule than a caller-supplied flag
        # and cannot be defeated by a caller forgetting to pass it.
        # DIVERGENCE ON RECORD, owner = the CA8-19 parity gate: spec §1's
        # DEFEATS block exempts only "Garrison defense", so a marshal REPULSED
        # from a garrison should read "Base: −1 per defeat". He scores 0 here.
        # Wiring that arm means ungating step 9.5 too, which mutates
        # `jealous_of` — drama-system behaviour with M7 exposure that belongs
        # with the parity work, not in a copy sweep.
        if (not is_bombardment and not is_auto_kill and not is_garrison
                and battle_result and not ctx.get('skip_jealousy')):
            from backend.game_logic import jealousy as _jealousy
            _jealousy.record_battle_glory(
                world, attacker, defender, attacker_won, defender_won,
                int(atk_casualties), int(def_casualties),
                conquered=bool(conquered),
                pre_attacker_strength=int(pre_atk),
                pre_defender_strength=int(pre_def),
                attacker_participants=jealousy_atk_parts,
                defender_participants=jealousy_def_parts)
            _jealousy.check_rivalry_transitions(
                world, pipeline_out.get('relationship_changes'))

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

            # AI-4a step 5 (Stage D): threat's target is the ACTOR — the
            # winner whose deed scares Europe. France's own slot is written
            # by exactly the same events as before (pin 16a byte-identical);
            # a non-player victor now accrues into its own slot instead of
            # nothing. Coalition shock keeps its France-arm gating verbatim
            # (members' WE feeds separate-peace acceptance — widening it is
            # a behaviour change this migration must not smuggle in).
            _third_party_battle = (
                getattr(world, "sovereign_map", "legacy") == "europe"
                and france not in (attacker.nation, defender_nation)
            )
            if attacker_won and attacker.nation:
                add_threat(world, 3, "battle_win", target=attacker.nation)
                # Decisive: ratio > 2:1 AND total > 10,000
                if int(def_casualties) > 0 and int(atk_casualties) > 0:
                    ratio = int(def_casualties) / int(atk_casualties)
                elif int(def_casualties) > 0:
                    ratio = 999
                else:
                    ratio = 0
                if ratio > 2 and total_cas > 10000:
                    add_threat(world, 5, "decisive_victory", target=attacker.nation)
                    if defender and attacker.nation == france:
                        add_coalition_shock(defender_nation, world)
                if conquered:
                    cap_reg = world.get_region(battle_region)
                    if cap_reg and getattr(cap_reg, 'is_capital', False):
                        add_threat(world, 15, "capital_capture", target=attacker.nation)
                if attacker.nation == france:
                    add_war_exhaustion_from_battle(defender_nation, int(def_casualties), world)
                elif (defender_nation == france
                        and getattr(world, "sovereign_map", "legacy") == "europe"):
                    # EC-W2: France mauled as DEFENDER — the loser-accrues
                    # arm (memo ECON_WAR_COUPLING_RESEARCH_2026_07_17 §3).
                    add_war_exhaustion_from_battle(france, int(def_casualties), world)
                elif _third_party_battle and defender_nation:
                    # AI-4c pin 17a: a third-party loser bears its own dead —
                    # the explicit arm both combat copies gain (a trailing
                    # else could not work; the France arms above swallow it).
                    add_war_exhaustion_from_battle(
                        defender_nation, int(def_casualties), world)

            elif defender_won:
                if attacker.nation == france:
                    add_war_exhaustion_from_battle(attacker.nation, int(atk_casualties), world)
                if defender_nation:
                    add_threat(world, 3, "battle_win", target=defender_nation)
                    if int(atk_casualties) > 0 and int(def_casualties) > 0:
                        ratio = int(atk_casualties) / int(def_casualties)
                    elif int(atk_casualties) > 0:
                        ratio = 999
                    else:
                        ratio = 0
                    if ratio > 2 and total_cas > 10000:
                        add_threat(world, 5, "decisive_victory", target=defender_nation)
                        if defender_nation == france:
                            add_coalition_shock(attacker.nation, world)
                    if defender_nation == france:
                        add_war_exhaustion_from_battle(
                            attacker.nation, int(atk_casualties), world)
                if _third_party_battle:
                    add_war_exhaustion_from_battle(
                        attacker.nation, int(atk_casualties), world)

            # CA8-19(iii): there used to be a fourth arm here —
            #   elif not attacker_won and not defender_won and is_garrison:
            #       add_war_exhaustion_from_battle(attacker.nation, atk_cas)
            # — "garrison hold: war exhaustion for the attacking nation". It was
            # unreachable from the day it was written (be596fd): a garrison hold
            # is a DEFENDER VICTORY and its ctx says so (`defender_won: True`),
            # so `elif defender_won:` above always claims it first. Deleted, not
            # repaired, because the arm above already does the job on every cell
            # of the running board — France repulsed pays via the
            # `attacker.nation == france` arm, an AI repulsed from a French
            # garrison pays via `defender_nation == france`, and AI-vs-AI pays
            # via `_third_party_battle`. (The filed claim that "an AI army
            # repulsed from a French garrison accrues no war exhaustion at all"
            # is FALSE; measured Austria +6.) Repairing it by flipping the hold
            # ctx would be strictly worse: as an elif it SUPPRESSES the
            # defender's battle_win threat, decisive_victory, coalition shock
            # and the war-score battle record that the live arm grants.

            # ── 13b. EC-W3: The Butcher's Bill ──
            # Each side pays at once for the guns, horses and stores lost
            # with its men (memo ECON_WAR_COUPLING_RESEARCH_2026_07_17 §3).
            # One-time flow OUTSIDE Net (plunder-gold precedent); rate sits
            # below the war recruit price so men still cost more than kit.
            # Europe-scoped (N1: legacy combat gold pins stand); bombardment
            # excluded with the whole step-13 block (ammunition expenditure
            # is not field-army materiel loss).
            if getattr(world, "sovereign_map", "legacy") == "europe":
                from backend.display_names import humanize_entity_name
                from backend.models.world_state import MATERIEL_RATE
                materiel_parts = []
                for m_nation, m_cas in ((attacker.nation, int(atk_casualties)),
                                        (defender_nation, int(def_casualties))):
                    bill = int(m_cas * MATERIEL_RATE)
                    if bill > 0 and m_nation:
                        world.nation_gold[m_nation] = int(
                            world.nation_gold.get(m_nation, 0) - bill)
                        # NA-6 §11.8-3: a FORMED nation must not be
                        # billed under its dead name (and the camelCase
                        # split also mangles it to "Kingdom Of Italy").
                        materiel_parts.append(
                            f"{formed_display_name(world, m_nation)} -{bill}g")
                if materiel_parts:
                    pipeline_out['materiel_msg'] = (
                        "\n[Materiel] Guns, horses and stores lost with the "
                        "fallen: " + ", ".join(materiel_parts) + ".")

        # ── 14. Exhaustion tracking ──
        if not ctx.get('skip_exhaustion'):
            attacker.increment_attacks_this_turn()

        return pipeline_out

    def _resolve_garrison_combat(self, marshal, target_region, world, game_state) -> dict:
        """
        Resolve combat between an attacking marshal and a capital garrison.

        ── CA8-19 GATE RULING (close-out gate 10.5, Aug 7 2026) ──────────
        Garrison assault is a SEPARATE resolver BY DESIGN, not by neglect.
        An escalade against a static garrison is not a field battle: there
        is no opposing commander to out-general, no morale to break (the
        5,000-collapse threshold IS the garrison's morale model), and no
        maneuver to flank. Full `resolve_battle` parity was REJECTED at the
        gate — it would re-record M1-M7 and BASELINE_SERIES (enemy P4.25
        takes this path every campaign), require a defender object that
        does not exist, and consume battle-name ordinals whose contract
        excludes garrison assaults (PC-4). The repulsed attacker's glory
        reads 0, canonized: the ladder prices reputation between
        COMMANDERS, and an escalade has no opposing commander to lose face
        against (JEALOUSY_SPEC §1 DEFEATS exemption). A future combat gate
        that wants garrison texture starts from the §10.5 record.
        ──────────────────────────────────────────────────────────────────

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
        #
        # CA8-19(i): the recompute STAMPS every eligible marshal in this region
        # (combat_executor.py:498-506), and until Aug 2026 both pipeline calls
        # below suppressed the clear — a flag written in be596fd, when this path
        # computed no coordination at all, and left untouched by b2de36d, which
        # added the recompute. So every garrison assault dressed its whole
        # origin garrison in a permanent attack bonus. `stamp_region` is the
        # region that stamp covered; the attacker leaves it on the capture path.
        stamp_region = marshal.location
        self._calculate_coordination_context(marshal, world)
        # MC-1c: a garrison assault IS an attack — get_attack_modifier below
        # consumes Iron Resolve stacks (anti-banking rule). Save the count
        # pre-consumption so the message can name it (shown = applied).
        iron_stacks_fired = (marshal.iron_resolve_stacks
                             if (hasattr(marshal, 'has_iron_resolve')
                                 and marshal.has_iron_resolve()) else 0)
        iron_note = ""
        if iron_stacks_fired > 0:
            _iron_pct = int(round(iron_stacks_fired
                                  * marshal.IRON_RESOLVE_BONUS_PER_STACK * 100))
            iron_note = (f" (Iron Resolve: {iron_stacks_fired} coiled "
                         f"stack{'s' if iron_stacks_fired != 1 else ''} released — "
                         f"+{_iron_pct}% attack)")
        # Attacker effective strength (uses single-source modifier from marshal.py)
        attacker_modifier = marshal.get_attack_modifier()
        attacker_effective = int(marshal.strength * attacker_modifier)

        # Calculate losses — proportional exchange
        # Garrison damage to attacker: ratio of garrison_effective to attacker_effective
        # Attacker damage to garrison: ratio of attacker_effective to garrison_effective
        if attacker_effective <= 0:
            # CA8-19(i): this exit runs after the stamp and before either
            # pipeline call, so it must clear for itself.
            self._clear_coordination_fields({stamp_region}, world)
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
            garrison_pipeline_out = self._post_combat_pipeline({
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
                # CA8-19(i): the clear runs. It happens BEFORE move_to below,
                # so attacker.location is still the origin; stamp_region is
                # named anyway so the fix survives a reordering.
                'coordination_regions': (stamp_region,),
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
                f"{marshal.name} assaults the {target_region.name} garrison!{iron_note} "
                f"Garrison collapses ({old_garrison:,} -> 0). "
                f"{marshal.name} loses {attacker_losses:,} troops in the assault. "
                f"{marshal.name} marches into {target_region.name}!"
            )
            if attrition_info["total_losses"] > 0:
                msg += f" ({attrition_info['total_losses']:,} lost to march)"
            # EC-W3 (review finding #4): the materiel bill was applied by the
            # pipeline but never SHOWN on garrison assaults — shown = applied.
            if garrison_pipeline_out.get('materiel_msg'):
                msg += garrison_pipeline_out['materiel_msg']

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
                from backend.models.world_state import capture_choice_prompt
                result["message"] += capture_choice_prompt(
                    world.pending_capture_choice)
                result["pending_capture_choice"] = True
                result["capture_data"] = world.pending_capture_choice

            return result
        else:
            # Garrison holds — attacker stays in place
            msg = (
                f"{marshal.name} assaults the {target_region.name} garrison!{iron_note} "
                f"Garrison: {old_garrison:,} -> {target_region.garrison_strength:,} "
                f"(-{garrison_losses:,}). "
                f"{marshal.name} loses {attacker_losses:,} troops. "
                f"Garrison holds — {target_region.garrison_strength:,} defenders remain."
            )
            if target_region.has_building("fortification"):
                msg += " Fortifications bolster the defense."

            # R1 Pipeline: centralized post-combat recording
            hold_pipeline_out = self._post_combat_pipeline({
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
                # CA8-19(i): the attacker never moves on a hold, but name the
                # stamped region explicitly for the same reason.
                'coordination_regions': (stamp_region,),
                'skip_log_battle_event': True,
                'skip_intel_update': True,
                'skip_war_damage': True,
                'skip_exhaustion': True,
            }, world)
            # EC-W3 (review finding #4): shown = applied on the hold path too.
            if hold_pipeline_out.get('materiel_msg'):
                msg += hold_pipeline_out['materiel_msg']

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

    # ════════════════════════════════════════════════════════════════════
    # W6-7 MARSHAL FATES (EXP-M1) — capture, ransom, the last stand.
    # Blessed defaults (band notes in WAVE6_FUN_FACTOR_SPEC §9/§14).
    # ════════════════════════════════════════════════════════════════════
    MARSHAL_FATE_STRENGTH_FLOOR = 5000   # band 3k-8k
    MARSHAL_FATE_ESCAPE_CHANCE = 0.60    # captured 40%; band ±15
    LAST_STAND_BONUS = 0.25              # band 15-35%
    LAST_STAND_BREAKOUT_PENALTY = 0.10   # breakout escape = 60% - 10%

    def _check_marshal_fate(self, marshal, enemy, world: 'WorldState'):
        """W6-7 §9.1: when a forced retreat fires on a cornered marshal,
        the man himself is at stake.

        Trigger: post-battle strength < MARSHAL_FATE_STRENGTH_FLOOR, OR the
        only retreat is encirclement (None) / at-war desperation soil
        (the W6-1 tier 5). Then:
          - pure encirclement = captured outright (replaces the old silent
            shatter),
          - an AGGRESSIVE marshal gets the last stand — player-owned as a
            pending_interrupt choice, AI by deterministic rule (fights when
            defending home/capital-adjacent ground, else breaks out),
          - everyone else rolls escape/capture (combat's RNG — seedable).

        Returns a message when the fate machinery consumed the retreat,
        None when the normal forced-retreat flow should proceed.
        """
        import random

        if marshal.strength <= 0 or getattr(marshal, "captured_by", ""):
            return None
        # W6-11 review hardening: an annihilated enemy takes no prisoners —
        # the fate machinery needs a LIVE captor army (belt-and-braces with
        # the victor forced-retreat guard in combat.py/the S62 loop).
        if enemy is None or getattr(enemy, "strength", 0) <= 0:
            return None
        captor_nation = getattr(enemy, "nation", "") if enemy else ""
        if not captor_nation or captor_nation == marshal.nation:
            return None

        attacker_location = getattr(enemy, 'location', None) if enemy else None
        retreat_to = world.get_safe_retreat_destination(
            marshal.name, attacker_location)
        encircled = retreat_to is None
        desperation_only = False
        if retreat_to is not None:
            dest = world.get_region(retreat_to)
            dest_controller = getattr(dest, "controller", None) if dest else None
            desperation_only = (
                dest_controller is not None
                and dest_controller != marshal.nation
                and world.is_at_war(marshal.nation, dest_controller)
            )
        low_strength = marshal.strength < self.MARSHAL_FATE_STRENGTH_FLOOR

        if not (low_strength or encircled or desperation_only):
            return None

        # Pure encirclement: nowhere to run — captured outright.
        if encircled:
            return self._capture_marshal(marshal, captor_nation, world,
                                         context="encircled")

        is_aggressive = getattr(marshal, "personality", "") == "aggressive"
        if is_aggressive and marshal.nation == world.player_nation:
            # The player chooses: die on his feet or run for it.
            interrupt = {
                "interrupt_type": "last_stand",
                "marshal": marshal.name,
                "enemy": getattr(enemy, "name", ""),
                "enemy_nation": captor_nation,
                "options": ["fight_to_the_last", "attempt_breakout"],
                "message": (
                    f"{marshal.name} is cornered at {marshal.location} with "
                    f"{int(marshal.strength):,} men, Sire — capture looms. "
                    f"He asks leave to fight to the last, or he can attempt "
                    f"a breakout."
                ),
            }
            marshal.pending_interrupt = interrupt
            # This interrupt is raised DURING the enemy phase, where choice
            # popups are deferred — so without a persistent notice the player
            # would have to blind-type the answer. Surface it on the rail so
            # the decision is visible and actionable after the turn report.
            try:
                from backend.notifications import (
                    NotificationPriority, create_notification,
                )
                world.notifications.add(create_notification(
                    notification_type="marshal_last_stand",
                    priority=NotificationPriority.CRITICAL,
                    title=f"{marshal.name} is cornered",
                    message=(
                        f"{marshal.name} is surrounded at {marshal.location} "
                        f"— type 'fight to the last' or 'attempt breakout' to "
                        f"decide his fate before he is taken."
                    ),
                    turn_created=int(getattr(world, "current_turn", 0)),
                    details={"marshal": marshal.name},
                ))
            except Exception:
                pass
            return (f"[!] {marshal.name} is CORNERED at {marshal.location} "
                    f"— awaiting your word: fight to the last, or attempt "
                    f"a breakout.")

        if is_aggressive:
            # AI rule (GR5, deterministic — no roll for the decision):
            # fight the last stand when defending homeland or
            # capital-adjacent ground, else break out.
            home = set(world.nation_starting_regions.get(marshal.nation, []) or [])
            capital = world.get_nation_capital(marshal.nation)
            capital_adjacent = False
            if capital:
                cap_region = world.get_region(capital)
                capital_adjacent = bool(
                    cap_region and (marshal.location == capital
                                    or marshal.location in cap_region.adjacent_regions))
            if marshal.location in home or capital_adjacent:
                return self._resolve_last_stand_fight(marshal, enemy, world)
            escape_chance = (self.MARSHAL_FATE_ESCAPE_CHANCE
                             - self.LAST_STAND_BREAKOUT_PENALTY)
        else:
            escape_chance = self.MARSHAL_FATE_ESCAPE_CHANCE

        if random.random() < escape_chance:
            return None  # He slips the net — the normal retreat proceeds.
        return self._capture_marshal(marshal, captor_nation, world,
                                     context="overrun")

    def _resolve_last_stand_fight(self, marshal, enemy, world: 'WorldState') -> str:
        """One final defense at +LAST_STAND_BONUS: the attacker is bled and
        halted for the turn; the survivors are captured after."""
        damage = int(marshal.strength * 0.25 * (1.0 + self.LAST_STAND_BONUS))
        enemy_name = getattr(enemy, "name", "")
        if enemy is not None and damage > 0:
            enemy.take_casualties(damage)
            enemy.adjust_morale(-5)
            # Halted this turn: the pursuit stops at the hill he died on.
            enemy.moved_this_turn = True
        world.log_event({
            "type": "last_stand",
            "marshal": marshal.name,
            "nation": marshal.nation,
            "location": marshal.location,
            "enemy": enemy_name,
            "casualties_inflicted": int(damage),
            "message": (
                f"{marshal.name} makes his last stand at {marshal.location} "
                f"— {damage:,} of {enemy_name}'s men fall before the end."
            ),
        })
        capture_msg = self._capture_marshal(
            marshal, getattr(enemy, "nation", ""), world,
            context="last_stand")
        return (f"[!] LAST STAND — {marshal.name} turns at bay at "
                f"{marshal.location}! {damage:,} enemy casualties; the "
                f"pursuit is halted. {capture_msg}")

    def _capture_marshal(self, marshal, captor_nation: str,
                         world: 'WorldState', context: str = "") -> str:
        """W6-7 §9.1: the marshal is taken. He leaves the map (held at the
        captor's capital, strength 0), his remaining troops disband — half
        make their way home to the owner's manpower pool."""
        owner = marshal.nation
        old_location = marshal.location
        remaining = int(marshal.strength)

        # 50% of remaining troops filter home to the manpower pool.
        returned = remaining // 2
        pools = getattr(world, "manpower_pools", None)
        if returned > 0 and isinstance(pools, dict) and owner in pools:
            pool = pools[owner]
            if getattr(marshal, "cavalry", False):
                pool["cavalry"] = int(pool.get("cavalry", 0)) + returned
            elif getattr(marshal, "artillery", False):
                pool["artillery"] = int(pool.get("artillery", 0)) + returned
            else:
                pool["infantry"] = int(pool.get("infantry", 0)) + returned

        # The captured state: off the map, held at the captor's capital.
        marshal.captured_by = captor_nation
        marshal.captured_turn = int(world.current_turn)
        marshal.strength = 0
        marshal.pending_interrupt = None
        # PC-9: the "is cornered — decide his fate" rail notice is an ASK.
        # Once he is taken there is nothing left to decide, and a notice that
        # outlives its decision is what left a turn-3 alert live at turn 42.
        try:
            world.notifications.dismiss_by_type(
                "marshal_last_stand",
                lambda n: n.get("details", {}).get("marshal") == marshal.name)
        except Exception:
            pass
        marshal.strategic_order = None
        marshal.holding_position = False
        marshal.hold_region = ""
        marshal.occupation_region = None
        marshal.occupation_turns_held = 0
        marshal.occupation_turns_required = 0
        marshal.retreating = False
        marshal.broken = False
        marshal.clear_iron_resolve()  # MC-1c: captured — the coil is gone
        captor_capital = world.get_nation_capital(captor_nation)
        if captor_capital:
            marshal.location = captor_capital

        world.log_event({
            "type": "marshal_captured",
            "marshal": marshal.name,
            "nation": owner,
            "captor": captor_nation,
            "location": old_location,
            "returned_troops": int(returned),
            "context": context,
            "message": (
                f"Marshal {marshal.name} has been CAPTURED by "
                f"{captor_nation} at {old_location}."
            ),
        })
        return (f"[!] MARSHAL CAPTURED — {marshal.name} is taken by "
                f"{captor_nation} at {old_location}! "
                f"{returned:,} of his men escape home to the depots.")

    def _apply_forced_retreat_or_break(self, marshal, enemy, world: 'WorldState',
                                       skip_fate: bool = False) -> str:
        """
        Apply forced retreat or break the army if surrounded.

        Uses get_safe_retreat_destination (BUG-009 fix) which properly checks
        threat zones. If no safe retreat exists, army is BROKEN.

        W6-7: the marshal-fate check runs FIRST — a cornered marshal
        (strength < 5,000 or desperation-only/encircled retreat) may be
        captured, offered a last stand, or slip away into the normal flow.

        Returns message describing what happened.
        """
        import random

        if not skip_fate:
            fate_msg = self._check_marshal_fate(marshal, enemy, world)
            if fate_msg is not None:
                return fate_msg

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
                # CA8-5: this is a ROUT, not an ordered withdrawal. The
                # dispatch's `own_broken` headline reads this flag; without
                # it the class was unreachable in ordinary play (see
                # dispatch.py). Voluntary retreats never carry it.
                "forced": True,
            })
            # Recovery duration is command-aware (MC gate Q3): 3 turns baseline,
            # 2 for a high-command marshal who rallies 2 stages/turn.
            recovery_turns = -(-3 // marshal.get_rally_stages_per_turn())
            return f"[!] {marshal.name}'s broken army flees to {retreat_to}!{strategic_msg}{attrition_note} (recovering for {recovery_turns} turns)"
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
            # Command-aware duration (MC gate Q3): 4 turns baseline, 2 for a
            # high-command marshal who rallies 2 stages/turn.
            broken_turns = -(-4 // marshal.get_rally_stages_per_turn())
            return (
                f"[BROKEN] {marshal.name}'s army is SURROUNDED and SHATTERED at {old_loc}! "
                f"Only {survivors:,} survivors ({survival_percent}%) escape to {spawn_loc}.{strategic_msg} "
                f"Army is BROKEN - can only recruit for {broken_turns} turns!"
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
        # S5-5: NO-GUNS GUARD (single source). Every bombardment caller —
        # the normal attack route, the strategic/defiant re-exec, and the
        # meta post-objection route — funnels through here, so a marshal
        # with no artillery can never open a bombardment. Previously the
        # post-objection path (meta_executor) re-ran this unguarded.
        # ════════════════════════════════════════════════════════════
        if not getattr(marshal, 'artillery', False):
            return {
                "success": False,
                "message": (
                    f"{marshal.name} commands no artillery — there are no guns "
                    f"to open a bombardment. Order an assault to close with the "
                    f"enemy instead."
                ),
            }

        # ════════════════════════════════════════════════════════════
        # NV-4 review (Aug 2, 2026): GUNS DO NOT CARRY ACROSS A STRAIT.
        # A PHYSICAL rule, not a naval-control one — which is why it lives
        # here at the single bombardment seam and not in crossing_check.
        # The attack-arm crossing gate already refuses a COVERED link, but
        # once the covering fleet was sunk the water read "open" and a
        # London battery could shell Flanders across 30km of sea (measured:
        # success=True with both fleets at 0). Range across water is an
        # expedition's problem; a battery's is powder and ballistics.
        # Same seam both call sites (normal route + SUPPORT auto-bombard),
        # both sides (GR5). Dormant in one read on fleet-less worlds —
        # legacy maps have no sea links, so is_sea_link is always False.
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.naval import is_sea_link
        if is_sea_link(world, marshal.location, defender.location):
            return {
                "success": False,
                "message": (
                    f"{marshal.name}'s guns cannot reach {defender.location} — "
                    f"no battery carries across open water, Sire. The sea is "
                    f"the fleet's business."
                ),
            }

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
        world.record_attack(marshal.name, marshal.location, target_location,
                            marshal.nation)

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

    def _execute_attack(self, marshal, target, world: WorldState, game_state,
                        skip_reckless_popup: bool = False,
                        command: Dict = None) -> Dict:
        """
        Execute an attack order with combat and region conquest.

        If attacking a region, will capture it after defeated all defenders.
        Handles undefended regions with instant capture.

        Args:
            skip_reckless_popup: If True, skip the recklessness popup check.
                                 Used when called from respond_to_glorious_charge.
            command: W6-4 — the parsed command dict, passed ONLY by the
                direct player dispatch. Its presence (minus the AI /
                strategic / muster-confirmed flags) arms the muster-preview
                gate; every other caller (strategic execution, auto-dispatch,
                defiance, post-objection) leaves it None and bypasses.
        """
        # Auto-break square formation (Session 67)
        self._executor._auto_break_square(marshal, "attack")

        def _stage_war_purpose_for_attack(target_nation: str) -> Dict:
            """Stage WPS-A purpose selection instead of auto-declaring by attack."""
            popup = self._stage_war_purpose_selection(
                world, marshal.nation, target_nation)
            return {
                "success": True,
                "message": (
                    f"Choose your war purpose against {target_nation}. "
                    "Issue the attack again after the declaration is settled."
                ),
                "war_purpose_popup": popup,
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

                # ESP-EV-4: this block returns early (charge popup / auto-
                # charge), so it is a lethal seam of its own and must consult
                # the SAME guessed-target guard the main path uses — otherwise
                # a reckless cavalry marshal charges a target the player never
                # named. The guard decides delegation-vs-guess from the raw
                # words alone, so a target the engine picked just above (for an
                # order that named no foe) correctly stands it down.
                _charge_guess = guessed_target_refusal(
                    world, marshal, command, target,
                    resolved_target=resolved_target,
                    enemy_candidates=(
                        world.get_enemy_by_name_for_nation(
                            resolved_target, marshal.nation),
                    ),
                    auto_resolved=not target,
                ) if resolved_target else None
                if _charge_guess is not None:
                    return _charge_guess

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

        # ESP-EV-4 fix (July 12, 2026): remember when the ENGINE chose the
        # target because the player left it open (bare "Ney, attack"). The
        # guessed-target guard below must never fire on a delegated target —
        # only on a SPECIFIC name the player typed that resolution overrode.
        _target_auto_resolved = False

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
                    _target_auto_resolved = True
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
                        # DEF-5 naval §4.1: the approach may not walk a covered strait
                        if getattr(world, "fleets", None):
                            from backend.game_logic.naval import crossing_check
                            _cross = crossing_check(world, marshal.nation,
                                                    marshal.location, best_next)
                            if not _cross["allowed"]:
                                return {
                                    "success": False,
                                    "message": _cross["message"],
                                    "blocked_naval": _cross["coverer"],
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

            # IGR-A3: "Ney, attack Austria" names a COUNTRY. Say so and list
            # its provinces rather than falling through to the bare
            # "Unknown target: Austria" — and never let the old fuzzy pass
            # stage a muster in Asturias.
            if region_error and region_error.get("nation_named"):
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

        # ════════════════════════════════════════════════════════════
        # ESP-EV-4 guessed-target guard — see guessed_target_refusal().
        #
        # Runs HERE, immediately after resolution and BEFORE the range check,
        # because the range check returns early with a strategic PURSUE. Until
        # July 18, 2026 the guard sat after that block, so a guessed target
        # that happened to be out of range marched off unguarded. Placed before
        # auto-war-declaration too, so a guess can never drag France into a war.
        # ════════════════════════════════════════════════════════════
        _guess_refusal = guessed_target_refusal(
            world, marshal, command, target,
            resolved_target=resolved_target,
            enemy_candidates=(
                enemy_by_name,
                world.get_enemy_by_name_for_nation(target, marshal.nation),
                world.get_enemy_at_location_for_nation(resolved_target,
                                                       marshal.nation),
            ),
            auto_resolved=_target_auto_resolved,
        )
        if _guess_refusal is not None:
            return _guess_refusal

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
                # S5-2: humanize marshal keys for the player-facing copy so a
                # camelCase name ("ArchdukeCharles") never leaks into prose.
                from backend.display_names import humanize_entity_name
                enemy_names = [e.name for e in enemies_here]
                enemy_display = [humanize_entity_name(n) for n in enemy_names]
                return {
                    "success": False,
                    "message": f"Cannot attack elsewhere while engaged with enemy forces! {', '.join(enemy_display)} must be dealt with first.",
                    "engaged_with": enemy_names,
                    "suggestion": f"Attack {humanize_entity_name(enemies_here[0].name)} in {marshal.location} first"
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
        # THE CROSSING GATE — attack arm (DEF-5 naval §4.1). An assault
        # whose battle stands ACROSS a covered sea link is an amphibious
        # attack the hostile fleet interdicts: "a blockade that stops
        # MOVE but not ATTACK is not a blockade." Same predicate as the
        # movement seam, both sides (GR5); one truthiness read dormant.
        # ════════════════════════════════════════════════════════════
        if getattr(world, "fleets", None):
            _battle_region_name = None
            if enemy_marshal and enemy_marshal.location != marshal.location:
                _battle_region_name = enemy_marshal.location
            elif not enemy_marshal and resolved_target != marshal.location:
                _battle_region_name = resolved_target
            if _battle_region_name:
                # NV-9: the REACH gate, not the direct pair. A cavalry
                # strike at range 2 may put the water on its MIDDLE leg —
                # measured on master, Murat charged Paris→(Normandy)→
                # London and ended the turn standing in London.
                from backend.game_logic.naval import crossing_check_reach
                _cross = crossing_check_reach(world, marshal.nation,
                                              marshal.location,
                                              _battle_region_name)
                if not _cross["allowed"]:
                    return {
                        "success": False,
                        "message": _cross["message"],
                        "blocked_naval": _cross["coverer"],
                        "naval_ratio": _cross["ratio"],
                    }

        # ════════════════════════════════════════════════════════════
        # NV-9: GUNS DO NOT CARRY ACROSS A STRAIT — checked HERE, above
        # the declaration, not only at the bombardment seam far below.
        # The crossing gate is deliberately sited before the declaration
        # ("the water is the first reality"), and at PEACE nothing covers
        # a strait, so a peacetime bombardment order sailed through the
        # gate, bought a war at the war-purpose card, and only THEN met
        # the physical refusal. A player must never pay for a war to be
        # told the order was impossible all along.
        # ════════════════════════════════════════════════════════════
        if (getattr(marshal, "artillery", False) and enemy_marshal
                and marshal.location != enemy_marshal.location):
            from backend.game_logic.naval import is_sea_link
            if is_sea_link(world, marshal.location, enemy_marshal.location):
                return {
                    "success": False,
                    "message": (
                        f"{marshal.name}'s guns cannot reach "
                        f"{enemy_marshal.location} — no battery carries "
                        f"across open water, Sire. The sea is the fleet's "
                        f"business."),
                }

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
            if not war_result.get("success"):
                # §4.3a-3 (pin 15): the declaration is the GATE, not a side
                # effect — a refused declaration (armistice cooldown, side
                # conflict, unavailable objective) aborts the attack instead
                # of proceeding against a nation still at peace.
                return {
                    "success": False,
                    "message": (f"{marshal.name} cannot open hostilities with "
                                f"{enemy_marshal.nation}: "
                                f"{war_result.get('message', 'the declaration was refused.')}"),
                }
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
                # §4.3a / pin 15: an ATTACK on a peace-nation's province
                # always requires a successful declaration — the old
                # can_enter_territory shortcut let an OPEN_MOVEMENT
                # treaty-holder march in and capture with no war, no
                # objective and no reason to render ("no unannounced
                # conquest"). Plain movement under those treaties is
                # untouched (movement_executor); this is the CAPTURE path.
                if target_region.controller and not world.is_at_war(marshal.nation, target_region.controller):
                    # Don't declare war on our own ally/vassal to seize their land.
                    _refusal = friendly_fire_refusal(world, marshal, target_region.controller)
                    if _refusal is not None:
                        return _refusal
                    from backend.game_logic.diplomacy import declare_war
                    if marshal.nation == world.player_nation:
                        return _stage_war_purpose_for_attack(target_region.controller)
                    war_result = declare_war(world, marshal.nation, target_region.controller)
                    if not war_result.get("success"):
                        # §4.3a-3: refused declaration aborts the capture —
                        # region.controller, marshals and strengths stay
                        # byte-identical, no war_instance, no conquest event.
                        return {
                            "success": False,
                            "message": (f"{marshal.name} cannot seize "
                                        f"{resolved_target}: "
                                        f"{war_result.get('message', 'the declaration was refused.')}"),
                        }

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
                        from backend.models.world_state import capture_choice_prompt
                        result["message"] += capture_choice_prompt(
                            world.pending_capture_choice)
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

        # PF-7: a "bombard" verb issued to a marshal with NO guns previously
        # fell straight through to a melee assault (no artillery -> the routing
        # below is skipped and resolve_battle runs). Reject it clearly BEFORE
        # the muster gate / AP spend / resolve_battle. Player-issued only:
        # command carries raw_command; AI / strategic-execution / auto-dispatch
        # / defiance callers pass command=None and are unaffected. Same-region
        # artillery "bombard" -> full battle is intended (BOMBARDMENT_SPEC §3)
        # and handled by the routing below, so this only fires with no guns.
        _bombard_verbs = ("bombard", "barrage", "shell", "cannonade")
        if (command
                and any(v in (command.get("raw_command") or "").lower()
                        for v in _bombard_verbs)
                and not getattr(marshal, 'artillery', False)):
            return {
                "success": False,
                "message": (f"Berthier shakes his head. \"{marshal.name} commands "
                            f"no guns, Sire — he cannot bombard. Order a direct "
                            f"assault, or bring an artillery corps within range.\""),
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

        # ════════════════════════════════════════════════════════════
        # W6-4 MUSTER PREVIEW + GATE (EXP-C1 + E-CA-4). Player-issued
        # field attacks only: the direct dispatch passes `command`; AI /
        # strategic-execution / auto-dispatch / post-objection callers pass
        # None and bypass entirely (GR5 — the AI has its own scoring; this
        # is a player legibility surface). Counter-punch attacks skip the
        # gate too (the free attack was already earned and consumed).
        # ════════════════════════════════════════════════════════════
        muster_preview = None
        if (command is not None
                and not command.get("_strategic_execution")
                and not command.get("_autonomous_execution")
                and marshal.nation == world.player_nation):
            muster_preview = self._build_muster_preview(
                marshal, enemy_marshal, world, game_state)
            gate_armed = (not command.get("_muster_confirmed")
                          and not is_counter_punch)
            if gate_armed and muster_preview["odds_band"] != "favorable":
                # E-CA-4: the attack does NOT resolve on the first call —
                # the muster block IS the odds warning. The interrupt
                # carries `marshal` (the July-7 L1 lesson) and resolves
                # via /strategic_response.
                muster_text = self._format_muster_lines(muster_preview)
                interrupt = {
                    "interrupt_type": "muster_confirm",
                    "marshal": marshal.name,
                    "target": enemy_marshal.name,
                    "options": ["attack_anyway", "cancel_order"],
                    "message": (
                        f"The odds read {muster_preview['odds_band']}, Sire. "
                        f"Review the muster, then [b]Commit the Attack[/b] to "
                        f"send {marshal.name} in — or Cancel to hold him "
                        f"back.\n{muster_text}"
                    ),
                    "muster_preview": muster_preview,
                }
                marshal.pending_interrupt = interrupt
                return {
                    "success": True,
                    "requires_input": True,
                    "no_action_cost": True,
                    "pending_interrupt": interrupt,
                    "muster_preview": muster_preview,
                    "message": interrupt["message"],
                }

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

        # §0.6.8 item 4c: snapshot both principals' battles_won BEFORE any
        # resolve path runs. The increment seams differ (combat.py bumps on
        # decisive outcomes only; the coordination caller bumps on tactical
        # wins too; the destruction sweep can turn a tactical outcome into a
        # kill) — the DELTA is the single truth the expectation note reads.
        _exp_wins_before = {
            m_.name: int(getattr(m_, "battles_won", 0))
            for m_ in (marshal, enemy_marshal) if m_ is not None
        }

        # ============================================================
        # FLANKING SYSTEM (Phase 2.5): Record attack origin BEFORE combat
        # ============================================================
        origin_region = marshal.location  # Capture origin BEFORE any movement
        target_location = enemy_marshal.location

        # Record this attack for flanking calculation.
        # PC-6: the pincer is counted among the ATTACKER'S OWN columns. Two
        # armies contesting one province used to pool their approaches, so
        # each side was handed a flanking bonus for the other side's march —
        # and the message named the enemy's start line as a friendly one.
        world.record_attack(marshal.name, origin_region, target_location,
                            marshal.nation)

        # Calculate flanking bonus based on all attacks this turn
        flanking_info = world.calculate_flanking_bonus(target_location,
                                                       marshal.nation)
        flanking_bonus = flanking_info["bonus"]

        # Generate flanking message if applicable
        flanking_message = world.get_flanking_message(
            marshal.name, origin_region, target_location, marshal.nation)

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
                            # MC-1c: direct assignment bypasses move_to —
                            # marching to the guns uncoils Iron Resolve.
                            arriving.clear_iron_resolve()
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

        # BD (Battle Diorama): every participant's strength at muster,
        # captured BEFORE support bombardment / resolve_battle /
        # take_casualties mutate anyone — the contingents' committed
        # figures (display-only, GR6).
        from backend.game_logic.battle_diorama import (
            build_battle_diorama, snapshot_pre_battle_strengths,
        )
        _bd_pre_strengths = snapshot_pre_battle_strengths(
            atk_participants, def_participants)

        # Jealousy v3.2 (spec §3): the grievance as fuel — a jealous marshal
        # attacking ALONE (no same-side participants) fights at +15%.
        # Transient stamp consumed by get_attack_modifier; cleared with the
        # other coordination transients (GR4: read, use, clear).
        if getattr(marshal, 'jealous_of', None) and len(atk_participants) <= 1:
            marshal._jealousy_solo_attack = True

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
            # CA8-19(i): this exit ADVANCES the attacker (below) before it
            # calls the pipeline, and the defender is popped from world.marshals
            # a line from here — so by clear time `{attacker.location,
            # battle_region}` has collapsed to the destination alone and the
            # origin's allies (an artillery marshal on SUPPORT, typically)
            # keep the stamp forever. Name the origin now, while it is still
            # the attacker's location.
            auto_kill_stamp_region = marshal.location
            # Remove destroyed defender
            world.marshals.pop(enemy_marshal.name, None)

            # PT-F1: same guard as the main battle-advance — the soil of a
            # court we are not at war with never transfers by pursuit.
            pursuit_block = self._pursuit_capture_guard(marshal, battle_region_name, world)

            # Advance attacker if not artillery
            advance_msg = ""
            if not getattr(marshal, 'artillery', False) and marshal.location != battle_region_name:
                if pursuit_block and pursuit_block["arm"] == "neutral":
                    advance_msg = (
                        f" {marshal.name} halts at the frontier of "
                        f"{battle_region_name} — {pursuit_block['owner']}'s soil, "
                        f"and we are not at war with {pursuit_block['owner']}.")
                else:
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
                if pursuit_block is not None and not remaining_defenders:
                    if pursuit_block["arm"] == "ally":
                        conquest_msg = pursuit_block["message"]
                    if (pursuit_block["arm"] == "neutral"
                            and marshal.nation == world.player_nation):
                        self._stage_war_purpose_selection(
                            world, marshal.nation, pursuit_block["owner"])
                        conquest_msg = (
                            f" To seize {battle_region_name} is to make war on "
                            f"{pursuit_block['owner']} — choose our purpose, "
                            f"or let the province stand.")
                elif not remaining_defenders:
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
                'coordination_regions': (
                    auto_kill_stamp_region,
                    # ... and the adjacent guns that overwatch stamped but
                    # that never move (review finding, same class).
                    *(a.location for a in artillery_reinforced_adjacent),
                ),
            }, world)

            # EC-W3 (review finding #4): shown = applied on the auto-kill path.
            auto_kill_materiel = pipeline_out.get('materiel_msg', '')

            auto_kill_event = {
                "type": "battle",
                "attacker": {"name": marshal.name},
                "defender": {"name": enemy_marshal.name},
                "attacker_nation": getattr(marshal, "nation", ""),
                "defender_nation": getattr(enemy_marshal, "nation", ""),
                "location": battle_region_name,
                "outcome": "attacker_victory",
                "auto_bombardment_kill": True,
            }
            # IGR-X8: parity with the garrison/unopposed routes — the AI's
            # decided choice rides the event (enemy_phase_dialog renders
            # "(plundered)"/"(secured)"), and the region flag tells the bare
            # " CAPTURED!" arm which province fell.
            if conquest_msg:
                auto_kill_event["region_conquered"] = True
                auto_kill_event["region_name"] = battle_region_name
                if capture_result.get("capture_choice"):
                    auto_kill_event["capture_choice"] = (
                        capture_result["capture_choice"])

            result = {
                "success": True,
                "action": "attack",
                "message": f"{preamble}\n\n{main_msg}{advance_msg}{conquest_msg}{auto_kill_materiel}",
                "auto_bombardment": True,
                "auto_bombardment_results": [
                    r.get("bombardment_result", {}) for r in auto_bombardment_results
                ],
                "events": [auto_kill_event],
                "new_state": game_state,
            }
            # IGR-X8: this route SET the world-side pending choice but never
            # told the response — the player got an invisible question that
            # only surfaced as a block on their next command. Same
            # prompt+flags block as the garrison route.
            if (conquest_msg and marshal.nation == world.player_nation
                    and world.pending_capture_choice):
                from backend.models.world_state import capture_choice_prompt
                result["message"] += capture_choice_prompt(
                    world.pending_capture_choice)
                result["pending_capture_choice"] = True
                result["capture_data"] = world.pending_capture_choice
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
        def_distribution = {}  # BD: initialized both paths — the diorama builder reads it
        if is_coordinated_battle:
            # CO-1/CO-1b: committed reinforcement strength adds to the clash,
            # personality- & relationship-scaled (single source, GR1-safe read).
            # Symmetric for a reinforced defender (GR5).
            committed_attacker = self._committed_reinforcement_strength(
                marshal, atk_participants, world)
            committed_defender = self._committed_reinforcement_strength(
                enemy_marshal, def_participants, world)
            # CO-6 (Combat Overhaul Phase 2): capture the pre-battle lead
            # strength and the committed sum for the reinforcement legibility
            # line (built with reinforcement_messages below). marshal.strength
            # here is still pre-distribution (casualties applied later).
            _co6_lead_pre_strength = int(marshal.strength)
            _co6_committed_attacker = committed_attacker
            # CA8-1 (creative audit, Aug 4 2026): the SAME two numbers for the
            # defending side. `combat.py:1098` puts the whole friendly stack
            # into the defensive ratio — committed mass is the variable that
            # decided every battle of the played campaign — and it was
            # printed only for the attacker, i.e. only for the side that does
            # not need it. When the player is attacked he was told
            # "+25% mountains" and shown a 567:1 exchange.
            _co6_lead_pre_strength_def = int(enemy_marshal.strength)
            _co6_committed_defender = committed_defender
            battle_result = self.combat_resolver.resolve_battle(
                attacker=marshal,
                defender=enemy_marshal,
                terrain=battle_terrain,
                flanking_bonus=flanking_bonus,
                flanking_message=flanking_message,
                fortification_bonus=fort_bonus,
                apply_casualties=False,
                committed_attacker=committed_attacker,
                committed_defender=committed_defender,
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

            # CO-5: single-source the survivor count — reconcile the battle
            # report's casualty_summary to the SAME post-distribution strengths
            # the event carries (the "two-truths" fix, M4). Runs before the
            # pursuit block, which then adds pursuit to BOTH surfaces.
            self._reconcile_report_survivors(
                battle_result, marshal, enemy_marshal)

            # Set forced_retreat flags per-primary for _handle_forced_retreat
            # Uses module-level FORCED_RETREAT_THRESHOLD from combat.py (Bug 7 fix)
            # W6-11 review guard (mirrors resolve_battle): the VICTOR of
            # this battle is never routed BY it — the symmetric morale cost
            # weakens his next fight instead.
            # MC-1: rout thresholds are per-marshal (Habsburg Resolve holds
            # to 15) — MUST mirror resolve_battle's get_rout_threshold call.
            _atk_victor = outcome in ("attacker_victory", "attacker_tactical_victory")
            _def_victor = outcome in ("defender_victory", "defender_tactical_victory")
            battle_result["attacker"]["forced_retreat"] = (
                marshal.strength > 0
                and marshal.morale <= marshal.get_rout_threshold(FORCED_RETREAT_THRESHOLD)
                and not _atk_victor
            )
            battle_result["defender"]["forced_retreat"] = (
                enemy_marshal.strength > 0
                and enemy_marshal.morale <= enemy_marshal.get_rout_threshold(FORCED_RETREAT_THRESHOLD)
                and not _def_victor
            )

            # MC-1 legibility rider (mirrors resolve_battle): when Habsburg
            # Resolve is the ONLY reason a beaten primary has not routed,
            # the battle description says so.
            for combatant, is_victor in ((marshal, _atk_victor), (enemy_marshal, _def_victor)):
                _personal = combatant.get_rout_threshold(FORCED_RETREAT_THRESHOLD)
                if (combatant.strength > 0 and not is_victor
                        and _personal < FORCED_RETREAT_THRESHOLD
                        and _personal < combatant.morale <= FORCED_RETREAT_THRESHOLD):
                    battle_result["description"] = battle_result.get("description", "") + (
                        f"\n\n{combatant.name}'s regiments close ranks — they will not break. "
                        f"(Habsburg Resolve: holds to {int(_personal)}% morale)"
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

            # Pursuit damage: primary attacker vs primary defender only —
            # a reinforcing Murat earns nothing; he must LEAD the killing
            # blow (MC-1, pinned). MUST mirror resolve_battle's pursuit block.
            if battle_result["defender"]["forced_retreat"] and atk_won:
                attacker_ability_name = ""
                if hasattr(marshal, 'ability'):
                    attacker_ability_name = marshal.ability.get("name", "")

                pursuit_damage = 0
                pursuit_message = None
                if attacker_ability_name == "First Horseman of Europe" and getattr(marshal, 'cavalry', False):
                    pursuit_damage = 5000
                elif attacker_ability_name == "Pursuit Master" and getattr(marshal, 'cavalry', False):
                    pursuit_damage = 5000
                elif attacker_ability_name == "Vorwärts!":
                    pursuit_damage = 3000

                # The Old Fox: halve AFTER the attacker's bonus (5,000 -> 2,500)
                old_fox_screens = (pursuit_damage > 0 and hasattr(enemy_marshal, 'ability')
                                   and enemy_marshal.ability.get("name") == "The Old Fox")
                if old_fox_screens:
                    pursuit_damage = int(pursuit_damage * 0.5)

                # Fire only above the 1,000-survivor floor (mirrors the solo
                # copy's P1-5 guard — the old `> 0` guard let max() RAISE a
                # sub-1,000 defender back up to the floor).
                if pursuit_damage > 0 and enemy_marshal.strength > 1000:
                    # Clamp BEFORE composing the copy (shown = applied — the
                    # message and every casualty total carry the ACTUAL figure).
                    pursuit_damage = min(pursuit_damage, enemy_marshal.strength - 1000)
                    enemy_marshal.strength -= pursuit_damage
                    if attacker_ability_name == "First Horseman of Europe":
                        pursuit_message = (
                            f"[Cavalry] {marshal.name}'s '{marshal.ability['name']}' — "
                            f"the cavalry turns the rout into annihilation! (+{pursuit_damage:,} pursuit casualties)"
                        )
                    elif attacker_ability_name == "Pursuit Master":
                        pursuit_message = (
                            f"[Cavalry] {marshal.name}'s '{marshal.ability['name']}' — "
                            f"cavalry runs down the retreating enemy! (+{pursuit_damage:,} pursuit casualties)"
                        )
                    else:  # Vorwärts!
                        pursuit_message = (
                            f"[Combat] {marshal.name}'s '{marshal.ability['name']}' — "
                            f"relentless pursuit inflicts extra casualties! (+{pursuit_damage:,} pursuit casualties)"
                        )
                    if old_fox_screens:
                        pursuit_message += (
                            f" But {enemy_marshal.name}'s rearguard screens the retreat — "
                            f"The Old Fox halves the harvest."
                        )
                    battle_result["pursuit_damage"] = int(pursuit_damage)
                    battle_result["pursuit_message"] = pursuit_message
                    # MC-1 legibility fix: this message was stored but
                    # never surfaced (resolve_battle folds its copy into
                    # the description; the coordinated copy must too).
                    battle_result["description"] = (
                        battle_result.get("description", "") + f"\n\n{pursuit_message}"
                    )
                    # Review fix (mirror the solo copy's accounting — solo
                    # folds pursuit into defender_casualties BEFORE its
                    # result dict/report/log are built; the coordinated copy
                    # builds them pre-pursuit, so every frozen number surface
                    # must be patched or the report contradicts the prose):
                    battle_result["defender"]["remaining"] = int(enemy_marshal.strength)
                    battle_result["defender"]["casualties"] = (
                        int(battle_result["defender"].get("casualties", 0)) + int(pursuit_damage))
                    # Pursuit is primary-defender-only: his distributed share
                    # carries it (stored below for event logging).
                    def_distribution[enemy_marshal.name] = (
                        def_distribution.get(enemy_marshal.name, 0) + int(pursuit_damage))
                    log_event = battle_result.get("log_battle_event")
                    if isinstance(log_event, dict):
                        log_event["defender_casualties"] = (
                            int(log_event.get("defender_casualties", 0)) + int(pursuit_damage))
                    report = battle_result.get("battle_report")
                    if isinstance(report, dict) and isinstance(report.get("casualty_summary"), dict):
                        cs = report["casualty_summary"]
                        cs["defender_casualties"] = int(cs.get("defender_casualties", 0)) + int(pursuit_damage)
                        cs["defender_remaining"] = max(
                            0, int(cs.get("defender_remaining", 0)) - int(pursuit_damage))

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
            # PC-5 (quiet-France played campaign, Aug 3 2026): who actually
            # STOOD on the field, per side — the same lists the diorama's
            # fought line is built from. The Berthier observation could say
            # "held the field alone" over a tableau showing three engaged
            # corps because the failed-reinforcement branch never had a way
            # to ask whether anyone else was there. Display-only; the primary
            # is always element one (_get_casualty_participants).
            "attacker_participants": [p.name for p in atk_participants],
            "defender_participants": [p.name for p in def_participants],
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

        # ════════════════════════════════════════════════════════════
        # W6-6 ENEMY VOICE (EXP-M2): after a battle that involves the
        # player, the enemy commander gets one line in his register —
        # display-only (GR6), deterministic rotation via battle_counts.
        # ════════════════════════════════════════════════════════════
        _player_nation = world.player_nation
        _enemy_side = None
        if marshal.nation != _player_nation and enemy_marshal.nation == _player_nation:
            _enemy_side = (marshal, True)   # the enemy attacked us
        elif marshal.nation == _player_nation and enemy_marshal.nation != _player_nation:
            _enemy_side = (enemy_marshal, False)  # we attacked the enemy
        if _enemy_side is not None:
            from backend.game_logic.enemy_voice import (
                derive_enemy_situation, pick_enemy_voice,
            )
            _enemy_m, _enemy_attacked = _enemy_side
            _side_key = "attacker" if _enemy_attacked else "defender"
            _situation = derive_enemy_situation(
                battle_result.get("outcome", ""), _enemy_attacked,
                bool(battle_result.get(_side_key, {}).get("forced_retreat")))
            if _situation and _enemy_m.strength > 0:
                _voice = pick_enemy_voice(
                    _enemy_m.name,
                    getattr(_enemy_m, "personality", "cautious"),
                    _situation,
                    int(world.battle_counts.get(target_location, 0)))
                if _voice:
                    battle_result["enemy_voice"] = _voice
                    if isinstance(battle_result.get("log_battle_event"), dict):
                        battle_result["log_battle_event"]["enemy_voice"] = _voice

        # Clear coordination transient fields (D5 + X1)
        # CA8 sweep 4 review: three regions cannot cover every stamped
        # marshal. `_calculate_overwatch` stamps `overwatch_penalty` on every
        # attack participant, and artillery that reinforces from an ADJACENT
        # province deliberately never relocates — so the gun stayed home
        # carrying a permanent −3%..−9% attack that nothing ever cleared.
        # Seed the set from the participants, which is the general form: the
        # bug is not a missing name, it is a missing REGION.
        involved_regions = {marshal.location}
        if enemy_marshal.strength > 0:
            involved_regions.add(enemy_marshal.location)
        involved_regions.add(battle_region_name)
        involved_regions.update(p.location for p in atk_participants)
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
        # Jealousy v3.2 (EC-F): resolution runs BEFORE this inline
        # relationship pass — a grievance the battle satisfied restores
        # its derived -1 first. The pipeline's own 9.5 hook no-ops after
        # this (already cleared). Participants mirror step-10 semantics.
        from backend.game_logic import jealousy as _jealousy
        from backend.game_logic.relationship import get_battle_participants
        _jl_outcome = battle_result.get("outcome", "")
        _jl_atk_won = "attacker" in _jl_outcome and "victory" in _jl_outcome
        _jl_def_won = "defender" in _jl_outcome and "victory" in _jl_outcome
        _jealousy.check_battle_resolution(
            world, marshal, enemy_marshal, _jl_atk_won, _jl_def_won,
            int(pre_battle_attacker_strength), int(pre_battle_defender_strength),
            attacker_participants=get_battle_participants(
                marshal, battle_region_name, marshal.nation, world),
            defender_participants=get_battle_participants(
                enemy_marshal, battle_region_name, enemy_marshal.nation, world),
            defender_broken=bool(getattr(enemy_marshal, 'broken', False)))
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
        # W6-11 review guard: participants on the WINNING side are never
        # routed by the battle they just won (mirrors resolve_battle).
        # MC-1 review fix: this is the THIRD rout-decision copy — it must
        # consult get_rout_threshold like the two primary copies (Habsburg
        # Resolve holds a non-primary Charles to 15, and the close-ranks
        # line names the hold when the ability is the only reason he stands).
        if is_coordinated_battle:
            if not atk_won:
                for p in atk_participants:
                    if p.name != marshal.name and p.strength > 0:
                        _p_threshold = p.get_rout_threshold(FORCED_RETREAT_THRESHOLD)
                        if p.morale <= _p_threshold:
                            msg = self._apply_forced_retreat_or_break(p, enemy_marshal, world)
                            if msg:
                                forced_retreat_msg += "\n" + msg
                        elif p.morale <= FORCED_RETREAT_THRESHOLD:
                            forced_retreat_msg += (
                                f"\n{p.name}'s regiments close ranks — they will not break. "
                                f"(Habsburg Resolve: holds to {int(_p_threshold)}% morale)")
            if not def_won:
                for p in def_participants:
                    if p.name != enemy_marshal.name and p.strength > 0:
                        _p_threshold = p.get_rout_threshold(FORCED_RETREAT_THRESHOLD)
                        if p.morale <= _p_threshold:
                            msg = self._apply_forced_retreat_or_break(p, marshal, world)
                            if msg:
                                forced_retreat_msg += "\n" + msg
                        elif p.morale <= FORCED_RETREAT_THRESHOLD:
                            forced_retreat_msg += (
                                f"\n{p.name}'s regiments close ranks — they will not break. "
                                f"(Habsburg Resolve: holds to {int(_p_threshold)}% morale)")

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
                        p.clear_iron_resolve()  # MC-1c: a move (direct assignment)
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
                        p.clear_iron_resolve()  # MC-1c: a move (direct assignment)
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
        capture_result = None  # IGR-X8: read by the event-parity block below

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

        # PT-F1: classify the region's OWNER before any advance — a pursuit
        # may only transfer soil of a court we are AT WAR with.
        pursuit_block = self._pursuit_capture_guard(marshal, target_location, world)

        # ARTILLERY: No advance on win — positional platform stays in place
        pursuit_halted = False
        is_artillery_no_advance = getattr(marshal, 'artillery', False) and marshal.location != target_location
        if is_artillery_no_advance:
            if can_advance:
                movement_msg = (f" {marshal.name}'s bombardment forces the enemy to retreat from {target_location}. "
                                f"Region must be secured by infantry to complete the capture.")
            print(f"[ATTACK MOVEMENT] Artillery {marshal.name} stays at {marshal.location} (no advance on win)")
        elif can_advance and marshal.strength > 0 and not getattr(self._executor, '_current_sortie', False):
            if marshal.location != target_location:
                if pursuit_block and pursuit_block["arm"] == "neutral":
                    # The frontier halt: no uninvited army on a peaceful
                    # court's soil — the movement rule this seam mirrors.
                    pursuit_halted = True
                    movement_msg = (
                        f" {marshal.name} halts at the frontier of "
                        f"{target_location} — {pursuit_block['owner']}'s soil, "
                        f"and we are not at war with {pursuit_block['owner']}.")
                    print(f"[ATTACK MOVEMENT] PT-F1 frontier halt: {marshal.name} stays at {marshal.location}")
                elif (getattr(world, "fleets", None)
                      and not self._naval_advance_allowed(
                          marshal, target_location, world)):
                    # NV-9: the ADVANCE is a move, and a move across water
                    # the enemy commands is the one thing the whole naval
                    # phase exists to refuse. The victor holds the field
                    # and stays on his own shore — the same shape as the
                    # PT-F1 frontier halt directly above.
                    pursuit_halted = True
                    movement_msg = (
                        f" {marshal.name} holds the shore — the enemy's "
                        f"sail still command the water between him and "
                        f"{target_location}, and no victory ashore puts "
                        f"boats under an army.")
                    print(f"[ATTACK MOVEMENT] NV-9 naval halt: {marshal.name} stays at {marshal.location}")
                else:
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

            if pursuit_block is not None and not remaining_defenders:
                # PT-F1: no transfer. The ally arm advanced as liberator;
                # the neutral arm halted at the frontier above. The player
                # may still choose the war — the pin-15 dialogue, never a
                # silent annexation.
                if not pursuit_halted:
                    conquest_msg = pursuit_block["message"]
                if (pursuit_block["arm"] == "neutral"
                        and marshal.nation == world.player_nation
                        and can_advance and marshal.strength > 0):
                    self._stage_war_purpose_selection(
                        world, marshal.nation, pursuit_block["owner"])
                    conquest_msg += (
                        f" To seize it is to make war on "
                        f"{pursuit_block['owner']} — choose our purpose, "
                        f"or let the province stand.")
            # If no defenders left, attempt capture (may start occupation if fortified)
            elif not remaining_defenders:
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
        # EC-W3: the materiel bill line (both sides' losses named)
        materiel_msg = pipeline_out.get('materiel_msg', '')

        # Build auto-bombardment preamble (Session 68) — prepended before combat description
        auto_bombard_preamble = ""
        if auto_bombardment_messages:
            auto_bombard_preamble = "\n".join(auto_bombardment_messages) + "\n\n"

        # Build final message with optional drill cancellation prefix, counter-punch, cavalry charge, and covering
        battle_message = counter_punch_message + cavalry_charge_message + covering_message + flanking_prefix + auto_bombard_preamble + battle_result["description"] + destroyed_msg + movement_msg + conquest_msg + vindication_msg + materiel_msg + forced_retreat_msg
        if drill_cancelled_message:
            battle_message = drill_cancelled_message + battle_message
        # W6-4: the muster block rides every resolved player attack —
        # prepended compact (favorable odds resolve straight through; a
        # confirmed re-issue still shows who mustered and why).
        if muster_preview is not None:
            battle_message = (self._format_muster_lines(muster_preview)
                              + "\n\n" + battle_message)

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
                # Side nations so the enemy-phase dialog can color the outcome
                # by WHO WON (the victor's side), not a hardcoded roster guess.
                "attacker_nation": battle_result.get("attacker_nation", ""),
                "defender_nation": battle_result.get("defender_nation", ""),
                "outcome": battle_result["outcome"],
                "victor": battle_result["victor"],
                "enemy_destroyed": enemy_destroyed,
                "region_conquered": conquered,
                # PC-1 (quiet-France played campaign, Aug 3 2026): this was
                # `resolved_target`, which is only a REGION when the attacker
                # named a region. `resolved_target` is reassigned to a region
                # solely in the fuzzy-region branch (~:3374); when the target
                # is a marshal, the `enemy_by_name` branch takes
                # `target_location = enemy_by_name.location` (~:3425) and
                # leaves `resolved_target` holding the MAN's name. The enemy
                # AI always targets marshals by name, so every AI conquest
                # shipped the wrong noun: measured 8 of 8 conquest events in
                # a 42-turn campaign carried "Ney" / "Deroy" / "Massena" /
                # "Paget" here, and both clients render it as a capture —
                # `enemy_phase_dialog.gd:291` and `main.gd:1977-1978` print
                # "⚑ Ney captured! ⚑" when a PROVINCE fell. The comment at
                # ~:5114 already warned against exactly this substitution.
                "region_name": target_location if conquered else None,
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

        # ════════════════════════════════════════════════════════════
        # BD (Battle Diorama): the self-contained tableau payload — one
        # builder for the solo and coordinated paths, fog-gated inside.
        # Rides BOTH surfaces: the top-level result field (the player's
        # own command response, whitelisted in main.py) and the battle
        # event (the enemy-phase transport, filtered with the action).
        # ════════════════════════════════════════════════════════════
        _bd_payload = build_battle_diorama(
            world=world, attacker=marshal, defender=enemy_marshal,
            battle_result=battle_result, battle_region=battle_region_name,
            atk_participants=atk_participants,
            def_participants=def_participants,
            pre_strengths=_bd_pre_strengths,
            atk_distribution=atk_distribution,
            def_distribution=def_distribution,
            attacker_reinforcements=attacker_reinforcements,
            defender_reinforcements=defender_reinforcements,
            region_conquered=conquered,
            total_engaged=total_engaged_strength,
            # PT-D2 muster-promise parity: every WILL JOIN name renders
            # with SOME status even when the resolve ladder dropped him.
            muster_rows=(muster_preview or {}).get("rows"),
        )
        if _bd_payload:
            result["battle_diorama"] = _bd_payload
            result["events"][0]["diorama"] = _bd_payload

        # Phase 6.1: Pass cavalry terrain message through as separate field
        # so Godot can display it in structured UI (not just embedded in description text)
        if battle_result.get("cavalry_terrain_message"):
            result["cavalry_terrain_message"] = battle_result["cavalry_terrain_message"]

        # W6-4: structured muster block rides the result for UI rendering.
        if muster_preview is not None:
            result["muster_preview"] = muster_preview

        # W6-7: a cornered PLAYER marshal's last-stand choice surfaces
        # synchronously on this response (the enemy-phase path reaches the
        # player via the stored marshal.pending_interrupt + typed answers).
        for _fate_m in (marshal, enemy_marshal):
            _fate_pi = getattr(_fate_m, "pending_interrupt", None)
            if (_fate_pi
                    and _fate_pi.get("interrupt_type") == "last_stand"
                    and _fate_m.nation == world.player_nation):
                result["pending_interrupt"] = _fate_pi
                result["requires_input"] = True
                break

        # Berthier's After-Action Report
        if battle_result.get("battle_report"):
            result["battle_report"] = battle_result["battle_report"]
            # W6-6: the enemy commander's line rides the report.
            if battle_result.get("enemy_voice"):
                result["battle_report"]["enemy_voice"] = battle_result["enemy_voice"]
            # §0.6.8 item 4c: a victory that raised the winner's reward
            # expectation says so in the report at the moment it happens,
            # not just in tomorrow's dispatch. Read as a battles_won DELTA
            # against the pre-combat snapshot — decisive outcomes, tactical
            # coordination wins, and destruction-sweep kills all land here
            # regardless of which seam did the increment. Player marshals
            # only; display-only (Golden Rule 6). Reinforcing participants
            # surface via the next dispatch's expectation_rises instead.
            from backend.game_logic.dotation import (
                EXPECTATION_CAP, REP_STEP, get_expectation,
                get_satisfaction, is_dotation_world,
            )
            if is_dotation_world(world):
                for _exp_winner in (marshal, enemy_marshal):
                    if (_exp_winner is None
                            or _exp_winner.nation != world.player_nation):
                        continue
                    _exp_before = _exp_wins_before.get(_exp_winner.name)
                    if (_exp_before is None
                            or int(getattr(_exp_winner, "battles_won", 0))
                            <= _exp_before):
                        continue
                    _exp_now = get_expectation(_exp_winner)
                    _exp_prev = int(min(REP_STEP * _exp_before,
                                        EXPECTATION_CAP))
                    if _exp_now > _exp_prev:
                        result["battle_report"]["expectation_note"] = (
                            f"Victory raises Marshal {_exp_winner.name}'s "
                            f"expectation of reward — he now looks for "
                            f"{_exp_now}g/turn (holds "
                            f"{get_satisfaction(_exp_winner, world)}g).")
                    break

        # Jealousy v3.2 (spec §11): Berthier notes jealous conduct on the
        # field — display-only rider on the battle report (GR6), player
        # marshals only. Mirrors the expectation_note glue above.
        if isinstance(result.get("battle_report"), dict):
            _jl_notes = []
            for _jl_m in (marshal, enemy_marshal):
                if _jl_m is None or _jl_m.nation != world.player_nation:
                    continue
                if getattr(_jl_m, "jealousy_surge_turns", 0) > 0 \
                        and not getattr(_jl_m, "jealous_of", None):
                    _jl_notes.append(
                        f"{_jl_m.name} fought like a man with something to "
                        f"prove — and proved it. His grievance is settled.")
                elif getattr(_jl_m, "jealous_of", None):
                    if _jl_m.personality == "aggressive":
                        _jl_notes.append(
                            f"{_jl_m.name} fought with particular ferocity — "
                            f"though one wonders if it was for France or for "
                            f"himself.")
                    elif _jl_m.personality == "cautious":
                        _jl_notes.append(
                            f"{_jl_m.name}'s commitment was... measured. His "
                            f"grievance against {_jl_m.jealous_of} shows in "
                            f"the field.")
                    else:
                        _jl_notes.append(
                            f"{_jl_m.name} fought with an intensity "
                            f"suggesting something to prove.")
            if _jl_notes:
                result["battle_report"]["jealousy_note"] = " ".join(_jl_notes)

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
                elif reason == "eyes_on_a_crown":
                    # MC-1: the post-battle copy must match the muster
                    # preview's honest arm — ambition, not the roads.
                    friendly_reason = (f"{r['marshal']} hesitated — the I Corps weighed "
                                       f"its own ambitions and did not march.")
                else:
                    friendly_reason = f"{r['marshal']} could not reach the battlefield in time."
                reinf_messages.append(friendly_reason)

        # CO-6 (Combat Overhaul Phase 2): reinforcement legibility — name the
        # committed effective strength so the player SEES that massing corps
        # adds weight to the clash (the CO-1 additive model, previously
        # invisible). Only when reinforcers actually arrived and contributed.
        _co6_committed = int(locals().get("_co6_committed_attacker", 0) or 0)
        if arrived_names and _co6_committed > 0:
            _co6_lead = int(locals().get("_co6_lead_pre_strength", 0) or 0)
            _co6_total = _co6_lead + _co6_committed
            joined = ", ".join(arrived_names)
            reinf_messages.append(
                f"Massed effective strength: {_co6_lead:,} (lead) + "
                f"{_co6_committed:,} committed ({joined}) = {_co6_total:,}.")

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

        # ════════════════════════════════════════════════════════════════
        # CA8-1: THE DEFENDING ARMY IS AN ARMY. Mirror of the two lines
        # above, which were both attacker-only with no defender equivalent
        # anywhere in this file. Without them, a battle where the player
        # massed five corps in defence reported his losses as the lead
        # marshal's personal share — `Ney 13` against the campaign log's
        # `197` for the same battle — and never once named the mass that
        # won it. Massing was an invisible dominant strategy: the player
        # could not see it, could not price it against the starvation it
        # causes (the campaign's other headline), and on reading two
        # casualty figures for one battle learned to distrust both.
        # ════════════════════════════════════════════════════════════════
        def_arrived = [r["marshal"] for r in defender_reinforcements
                       if r.get("arrived")]
        _co6_committed_def = int(locals().get("_co6_committed_defender", 0) or 0)
        if def_arrived and _co6_committed_def > 0:
            _co6_lead_def = int(locals().get("_co6_lead_pre_strength_def", 0) or 0)
            joined_def = ", ".join(def_arrived)
            reinf_messages.append(
                f"{enemy_marshal.name} was reinforced — massed effective "
                f"strength: {_co6_lead_def:,} (lead) + {_co6_committed_def:,} "
                f"committed ({joined_def}) = "
                f"{_co6_lead_def + _co6_committed_def:,}.")
        if def_arrived and def_distribution:
            def_ally_casualties = sum(
                def_distribution.get(name, 0) for name in def_arrived)
            if def_ally_casualties > 0:
                _plural = "allies" if len(def_arrived) > 1 else "ally"
                reinf_messages.append(
                    f"{enemy_marshal.name}'s supporting {_plural} lost "
                    f"{int(def_ally_casualties):,} men.")

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
            # IGR-X8: the field-battle conquest (the most common capture)
            # never stated the question in the message — a typed-path player
            # had strictly less information than one clicking. Same priced
            # sentence as the garrison/unopposed routes. Review fix: gated
            # on THIS attack having conquered (like the auto-kill sibling) —
            # a stale pending from an EARLIER marshal's strategic capture
            # must not append "Your forces have taken Tyrol" to an unrelated
            # battle report.
            if (conquered and marshal.nation == world.player_nation
                    and world.pending_capture_choice.get("stage") != "estate"):
                from backend.models.world_state import capture_choice_prompt
                result["message"] += capture_choice_prompt(
                    world.pending_capture_choice)

        # IGR-X8: an AI field-battle conquest rendered a bare " CAPTURED!"
        # in the enemy-phase dialog while garrison/unopposed conquests said
        # "(plundered)"/"(secured)" — the decided choice now rides the event.
        if conquered and capture_result and capture_result.get("capture_choice"):
            result["events"][0]["capture_choice"] = capture_result["capture_choice"]

        # ════════════════════════════════════════════════════════════
        # REINFORCEMENT TRUST PENALTIES (Session 61a)
        # Non-Literal, non-Hostile marshals who fail to arrive lose -3 trust.
        # MC-1 review fix: "eyes_on_a_crown" is exempt like the literal
        # no-march — a by-design character refusal, not a failure to be
        # punished (the gate priced the ability as defiance + arrival only;
        # a silent recurring trust drain was never blessed). A no-show
        # UNDER a written SUPPORT order keeps reason "low_score" and is
        # still docked.
        # ════════════════════════════════════════════════════════════
        all_reinforcements = attacker_reinforcements + defender_reinforcements
        for reinf_result in all_reinforcements:
            if not reinf_result["arrived"] and reinf_result["reason"] not in (
                    "literal_personality", "fate_intervened", "eyes_on_a_crown"):
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

        # PC-9 (quiet-France played campaign, Aug 3 2026): the second line is
        # a rule addressed to the PLAYER ("any order you give…"), and it was
        # appended unconditionally — so it rode the enemy phase and appeared
        # under [Austria], instructing the player about the discipline of an
        # Austrian square. The mechanic is symmetric; the tutorial sentence is
        # not, because only one side takes orders from the reader.
        is_player = marshal.nation == getattr(world, "player_nation", "France")
        square_discipline_note = (
            "\nAny order — even one that fails — will break the discipline "
            "required to hold square." if is_player else "")
        message = fortify_break_msg + (
            f"{marshal.name} forms square at {marshal.location}! "
            f"Bayonets bristle in all directions. (+5% defense, cavalry -40%, "
            f"but artillery +50% damage vs packed ranks){strategic_cancel_msg}"
            f"{square_discipline_note}"
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

        # ════════════════════════════════════════════════════════════
        # NV-9 THE CROSSING GATE — the charge's INITIATION, not just its
        # advance. Only the advance was gated, so a reckless squadron
        # could fight the full 2x-damage battle across water the Royal
        # Navy commands and simply not move — free, repeatable, and the
        # exact thing the attack arm refuses outright two thousand lines
        # up ("a blockade that stops MOVE but not ATTACK is not a
        # blockade"). The reach form covers the range-2 middle leg.
        # ════════════════════════════════════════════════════════════
        if getattr(world, "fleets", None):
            from backend.game_logic.naval import crossing_check_reach
            _charge_cross = crossing_check_reach(
                world, marshal.nation, marshal.location,
                target_marshal.location)
            if not _charge_cross["allowed"]:
                return {
                    "success": False,
                    "message": _charge_cross["message"],
                    "blocked_naval": _charge_cross["coverer"],
                    "naval_ratio": _charge_cross["ratio"],
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
        world.record_attack(marshal.name, marshal.location,
                            target_marshal.location, marshal.nation)

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
            # DEF-5 naval §4.1: cavalry does not swim — a charge's advance
            # never crosses a covered strait (the battle itself was fought
            # at range; the squadron holds the water).
            # NV-9: one advance seam for every post-combat move, reach-aware.
            _charge_cross_ok = self._naval_advance_allowed(
                marshal, charge_battle_region, world)
            if marshal.location != charge_battle_region and _charge_cross_ok:
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
        capture_result = None  # IGR-X8: read by the event-parity block below
        if attacker_won and marshal.strength > 0 and marshal.location == charge_battle_region:
            target_region = world.get_region(charge_battle_region)
            if target_region and target_region.controller != marshal.nation:
                remaining_defenders = [
                    m for m in world.marshals.values()
                    if m.location == charge_battle_region and m.strength > 0 and m.nation != marshal.nation
                    and world.is_at_war(marshal.nation, m.nation)
                ]
                # PT-F1: the charge's momentum carried the cavalry in, but a
                # third party's soil still never transfers by pursuit.
                pursuit_block = self._pursuit_capture_guard(
                    marshal, charge_battle_region, world)
                if pursuit_block is not None and not remaining_defenders:
                    conquest_msg = pursuit_block["message"]
                    if (pursuit_block["arm"] == "neutral"
                            and marshal.nation == world.player_nation):
                        self._stage_war_purpose_selection(
                            world, marshal.nation, pursuit_block["owner"])
                        conquest_msg += (
                            f" To seize it is to make war on "
                            f"{pursuit_block['owner']} — choose our purpose, "
                            f"or let the province stand.")
                elif not remaining_defenders:
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
        # EC-W3: the materiel bill line
        if pipeline_out.get('materiel_msg'):
            charge_message += pipeline_out['materiel_msg']
        charge_message += f"\n\n[color=#cd6b6b]Recklessness reset: {recklessness_before} → 0[/color]"

        charge_event = {
            "type": "glorious_charge",
            "marshal": marshal.name,
            "target": target_marshal.name,
            "attacker_won": attacker_won,
            "recklessness_reset": True
        }
        # IGR-X8: parity with the other conquest events — the enemy-phase
        # dialog can attribute what became of the province.
        if conquered:
            charge_event["region_conquered"] = True
            charge_event["region_name"] = charge_battle_region
            if capture_result and capture_result.get("capture_choice"):
                charge_event["capture_choice"] = capture_result["capture_choice"]

        charge_result = {
            "success": True,
            "message": charge_message,
            "glorious_charge": True,
            "damage_multiplier": 2,
            "recklessness_before": recklessness_before,
            "recklessness_after": 0,
            "combat_result": combat_result,
            "events": [charge_event],
            "new_state": game_state
        }
        # Berthier's After-Action Report
        if combat_result.get("battle_report"):
            charge_result["battle_report"] = combat_result["battle_report"]
        # Flag pending capture choice for popup
        if world.pending_capture_choice:
            charge_result["pending_capture_choice"] = True
            charge_result["capture_data"] = world.pending_capture_choice
            # IGR-X8: state the priced question here too (route parity).
            # Review fix: gated on THIS charge having conquered — never a
            # stale pending's prompt on an unrelated charge report.
            if (conquered and marshal.nation == world.player_nation
                    and world.pending_capture_choice.get("stage") != "estate"):
                from backend.models.world_state import capture_choice_prompt
                charge_result["message"] += capture_choice_prompt(
                    world.pending_capture_choice)
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

    # EC-W5a: single source lives in world_state.py so the AI personality
    # auto-decide path (world_state capture handling) pays the SAME rate
    # (GR5 — it silently paid ×1.0 before). Class attr kept for tests.
    PLUNDER_INCOME_MULTIPLIER = WS_PLUNDER_INCOME_MULTIPLIER

    def _apply_plunder(self, region, world, nation: str = None) -> Dict:
        """Apply plunder effects to a captured region.

        IGR-E post-landing review #5: the effects live in ONE place —
        `world_state.apply_plunder_effects` — shared with the AI
        occupation-capture branch, which used to carry a hand-inlined copy
        that silently dropped the per-building event logging.

        Args:
            nation: Nation receiving the gold. MUST be passed explicitly for AI nations.
                    Do NOT use world.gold (property targeting player_nation) for AI plunder.
                    Defaults to player_nation for backward compat only.
        """
        from backend.models.world_state import apply_plunder_effects
        receiving_nation = nation or world.player_nation
        gold_gained = apply_plunder_effects(world, region, receiving_nation)
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

    def _stage_war_purpose_selection(self, world, attacker_nation: str,
                                     target_nation: str) -> dict:
        """Push the WPS-A war-purpose selection dialogue (the pin-15
        machinery) and return the popup payload. Shared by the undefended
        -territory attack gate and the PT-F1 pursuit-capture guard."""
        from backend.game_logic.diplomacy import get_available_war_objectives

        objectives = get_available_war_objectives(
            world, attacker_nation, target_nation)
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
        return {"target_nation": target_nation, "objectives": objectives}

    def _pursuit_capture_guard(self, marshal, region_name: str, world) -> Optional[dict]:
        """PT-F1 (Aug-1 played-world re-measure): a battle-advance may only
        TRANSFER the soil of a court the victor is AT WAR with. Attacking
        the enemy army standing on a third party's province stays legal —
        the annexation is what needs a war.

        Seen live twice: Ney destroyed Mack in Nassau (Hesse, at PEACE) and
        Nassau silently became French; and the Ulm strike transferred
        Swabia — BAVARIAN soil Mack merely occupied — from a bloc ally.
        Pin-15 closed the movement-capture hole; this closes its
        battle-advance sibling at the same seam family, keyed off the
        region's controller at the moment of transfer (GR5: one predicate,
        both sides — the player chooses via the War Purpose dialogue, the
        AI restrains, since its war decisions belong to the Stage-D
        machinery, never to a pursuit's momentum).

        Returns None when capture may proceed, else:
          {"arm": "ally"|"neutral", "owner": str, "message": str}
        Neutral arm additionally means the ADVANCE halts (an uninvited army
        on a peaceful court's soil is the movement rule this mirrors);
        the ally arm advances but never transfers — pursuit is not conquest.
        """
        region = world.get_region(region_name)
        owner = getattr(region, "controller", None) if region else None
        if not owner or owner == marshal.nation:
            return None
        if world.is_at_war(marshal.nation, owner):
            return None
        if not world.can_attack_nation(marshal.nation, owner):
            rel = ("vassal" if world.get_diplomatic_state(
                marshal.nation, owner) == "VASSAL" else "ally")
            return {
                "arm": "ally",
                "owner": owner,
                "message": (
                    f" {region_name} remains {owner}'s soil — we drove the "
                    f"enemy from our {rel}'s province; it is not ours to take."),
            }
        return {
            "arm": "neutral",
            "owner": owner,
            "message": (
                f" {region_name} is {owner}'s soil, and we are not at war "
                f"with {owner}. {marshal.name} halts at the edge of conquest."),
        }

    def _get_ai_capture_choice(self, marshal, region, world) -> str:
        """AI decides plunder vs secure based on personality.

        IGR-E addendum: routed through the single source. This read
        `marshal.personality_type` — an attribute that does not exist — so
        it returned "secure" unconditionally and the AI could never plunder.
        Post-landing review P2 #1 added the own-soil guard (an AI never
        sacks its own homeland on recapture), which needs region + world —
        both live in the single source, so the signature carries them.
        """
        from backend.models.world_state import ai_prefers_plunder
        return ("plunder" if ai_prefers_plunder(marshal, world, region.name)
                else "secure")

    def _apply_ai_capture_choice(self, marshal, region, world, old_controller: str = "") -> str:
        """Apply AI's automatic capture choice (no popup). Returns the choice made."""
        choice = self._get_ai_capture_choice(marshal, region, world)
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
        # W6-8 (GR5): an enemy estate on the captured soil is resolved by
        # rule, mirroring the player's confiscate/respect choice.
        from backend.game_logic.dotation import apply_ai_estate_rule
        apply_ai_estate_rule(world, region, marshal.nation)
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
                # ────────────────────────────────────────────────────────
                # CA8-13 (creative audit, Aug 4 2026): liberating your OWN
                # homeland province opened a mandatory modal asking whether
                # to burn it — and blocked end-turn until answered. The
                # played campaign offered 600 gold to sack Rhineland forty
                # lines after the treasury report listed Rhineland's 150g
                # among France's own income. The player could not decline
                # to have an opinion about sacking his own country.
                #
                # IGR-E's review installed exactly this guard on the AI
                # branch and recorded the player modal as a deliberate
                # choice. It is not one: there is no decision here, and the
                # prompt asserts the province is foreign.
                # ────────────────────────────────────────────────────────
                from backend.models.world_state import (
                    build_capture_choice, is_own_soil_recapture)
                if is_own_soil_recapture(world, region_name, marshal.nation):
                    self._apply_secure(region)
                    ai_choice = "secure"
                else:
                    world.pending_capture_choice = build_capture_choice(
                        world, region, marshal.name, old_controller)
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

    def _scan_general_attack_candidates(self, world, player_marshals=None):
        """Single-source scan for a bare "attack": partition player marshals
        into ``combat_ready`` [(marshal, enemy, distance<=1)], ``out_of_range``
        [(marshal, enemy, distance)], and ``filtered_out`` (explanation
        strings for the dead/weak/fortified/drill-locked). Shared by
        ``_execute_general_attack`` AND the CR-6 dispatch resolver
        (``resolve_auto_attack``) so the two never diverge (S5-D3).
        """
        if player_marshals is None:
            player_marshals = world.get_player_marshals()

        combat_ready = []   # [(marshal, enemy, distance)]
        out_of_range = []   # [(marshal, enemy, distance)] - for fallback move
        filtered_out = []   # Explanations for non-combat-ready

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

        return combat_ready, out_of_range, filtered_out

    def _execute_general_attack(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute general attack - finds nearest enemy automatically.

        If no marshal can attack (all out of range), moves the closest
        marshal toward the nearest enemy instead.

        NOTE: for a PLAYER command this is reached only via the CR-6 resolver's
        "passthrough" verdict (nobody in contact → move-toward / no-enemies);
        the in-contact case is rewritten to a named attack upstream so it flows
        through clarification / muster / objection. Direct callers and tests
        still get the full instant-pick behavior below.
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        player_marshals = world.get_player_marshals()

        if not player_marshals:
            return {"success": False, "message": "No marshals available to attack"}

        combat_ready, out_of_range, filtered_out = \
            self._scan_general_attack_candidates(world, player_marshals)

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

                # DEF-5 naval §4.1: the general-attack approach may not walk
                # a covered strait (the path planner is edge-blind; refuse
                # the hop here with the honest reason).
                if getattr(world, "fleets", None):
                    from backend.game_logic.naval import crossing_check
                    _cross = crossing_check(world, closest_marshal.nation,
                                            closest_marshal.location, next_region)
                    if not _cross["allowed"]:
                        return {
                            "success": False,
                            "message": _cross["message"],
                            "blocked_naval": _cross["coverer"],
                        }

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

    def _resolve_auto_assign_attacker(self, command: Dict, world) -> Dict:
        """Single-source resolution for "attack <target>" (auto_assign_attack):
        resolve the target (enemy marshal name first, then region) and pick the
        nearest player marshal. Shared by ``_execute_auto_assign_attack`` AND
        the CR-6 dispatch resolver so the two never diverge (S5-D3). Returns:
          {"kind": "named", "marshal": <name>, "target": <display>}
          {"kind": "error", "error": <response dict>}  — destroyed target / no
              marshal in range / unresolvable region (exact copy preserved).
        """
        target = command.get("target")
        if not world or not target:
            return {"kind": "error", "error": {
                "success": False,
                "message": "Error: No target or world state"}}

        # FIRST: Try to find target as enemy marshal name
        enemy = world.get_enemy_by_name(target)
        if enemy:
            if enemy.strength <= 0:
                return {"kind": "error", "error": {
                    "success": False,
                    "message": f"{target} has already been destroyed!"}}
            result = world.find_nearest_marshal_to_region(enemy.location)
            if not result:
                return {"kind": "error", "error": {
                    "success": False,
                    "message": f"No marshals in range of {target}"}}
            nearest_marshal, _distance = result
            return {"kind": "named", "marshal": nearest_marshal.name,
                    "target": target}

        # SECOND: Check if target is a region name with fuzzy matching
        target_region, error = self._executor._fuzzy_match_region(target, world)
        if error:
            return {"kind": "error", "error": error}
        target_name = target_region.name if hasattr(target_region, 'name') else target
        result = world.find_nearest_marshal_to_region(target_name)
        if not result:
            return {"kind": "error", "error": {
                "success": False,
                "message": f"No marshals in range of {target_name}"}}
        nearest_marshal, _distance = result
        return {"kind": "named", "marshal": nearest_marshal.name,
                "target": target_name}

    def _execute_auto_assign_attack(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute attack with auto-assigned marshal.
        Example: "Attack Wellington" or "Attack Rhine"
        Delegates to _execute_attack() after finding nearest marshal (Building Blocks).

        NOTE: for a PLAYER command the CR-6 resolver rewrites this to a named
        attack upstream (muster gate + objection apply); this method is reached
        directly (tests / internal callers) or via the resolver's "passthrough"
        error verdict, and keeps its full instant behavior below.
        """
        world: WorldState = game_state.get("world")
        resolution = self._resolve_auto_assign_attacker(command, world)
        if resolution["kind"] == "error":
            return resolution["error"]

        nearest_marshal = world.get_marshal(resolution["marshal"])
        target_name = resolution["target"]

        # Delegate to _execute_attack with full coordination support
        attack_result = self._execute_attack(nearest_marshal, target_name, world, game_state)
        # Tag as auto-assigned for UI display
        if attack_result.get("events"):
            for ev in attack_result["events"]:
                ev["auto_assigned"] = True
        return attack_result

    def resolve_auto_attack(self, command: Dict, world, raw_input: str = "") -> Dict:
        """CR-6 / S5-D1 dispatch resolver (blessed CR-6 mini-gate, July 16,
        2026). A player bare "attack" (general_attack) or "attack <target>"
        (auto_assign_attack) auto-picked a marshal into a real battle, skipping
        CR-2 clarification, the W6-4 muster gate, and the objection gate — the
        most ambiguous lethal order had the fewest safeguards. This resolves
        the marshal so the pick can flow through the ordinary named-attack
        pipeline. Returns one of:
          {"kind": "clarify", "response": <dict>}  — >1 commandable marshal in
              enemy contact for a bare attack; ask which one (a).
          {"kind": "named", "marshal", "target", "explanation"}  — rewrite to a
              specific named attack; muster gate (b) + objection (c) apply.
          {"kind": "passthrough"}  — nobody in contact (move-toward /
              no-enemies) or a resolution error; leave the original command for
              _execute_general_attack / _execute_auto_assign_attack.
        Caller (executor.execute) guards this to player commands only (GR5).
        """
        ctype = command.get("type")

        if ctype == "general_attack":
            combat_ready, _out, filtered_out = \
                self._scan_general_attack_candidates(world)
            if not combat_ready:
                return {"kind": "passthrough"}
            combat_ready.sort(key=lambda x: (x[2], -x[0].strength))
            # Prefer a commandable marshal — an autonomous marshal would be
            # blocked downstream, so a bare "attack" reaches for whoever CAN be
            # ordered when one is in contact.
            pool = [c for c in combat_ready
                    if not getattr(c[0], 'autonomous', False)] or combat_ready
            if len(pool) > 1:
                from backend.commands.clarification import (
                    build_contact_attack_clarification,
                )
                resp = build_contact_attack_clarification(
                    world, [(m, e) for m, e, _ in pool], raw_input)
                if resp is not None:
                    return {"kind": "clarify", "response": resp}
                # Affordability guard failed → fall through to instant pick.
            best_marshal, best_enemy, _d = pool[0]
            explanation = ""
            if filtered_out:
                explanation = f"[NOTE: {', '.join(filtered_out)}]\n"
            explanation += (f"{best_marshal.name} "
                            f"({best_marshal.strength:,} troops) attacks!\n\n")
            return {"kind": "named", "marshal": best_marshal.name,
                    "target": best_enemy.name, "explanation": explanation}

        if ctype == "auto_assign_attack":
            resolution = self._resolve_auto_assign_attacker(command, world)
            if resolution["kind"] == "named":
                return {"kind": "named", "marshal": resolution["marshal"],
                        "target": resolution["target"], "explanation": ""}
            return {"kind": "passthrough"}

        return {"kind": "passthrough"}

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

