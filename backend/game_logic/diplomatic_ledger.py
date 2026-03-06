"""
Diplomatic Ledger — 4-section backend builder (Session 8A)

Builds a structured dict for the Godot Diplomatic Ledger screen.
All values int()-wrapped per CLAUDE.md rule: "All numbers to Godot: int()".

Fog-filtered: army_strength uses diplomatic intelligence model —
national-level visibility based on best marshal visibility per nation.
"""

from typing import Dict, Any, List

from backend.models.intel import (
    FULL, PARTIAL, STALE, UNKNOWN,
    VISIBILITY_PRIORITY,
)


def build_diplomatic_ledger(world) -> Dict[str, Any]:
    """
    Build the diplomatic ledger dict for Godot rendering.

    Args:
        world: WorldState instance

    Returns:
        Dict with nations, treaties, threat_coalition, talleyrand sections.
        All numeric values int()-wrapped.
    """
    return {
        "nations": _build_nations(world),
        "treaties": _build_treaties(world),
        "threat_coalition": _build_threat_coalition(world),
        "talleyrand": _build_talleyrand(world),
    }


# ============================================================================
# FOG HELPER: National-level visibility
# ============================================================================

def _get_nation_visibility(nation_name: str, world) -> str:
    """Get the best visibility tier across all marshals belonging to a nation.

    Diplomatic intelligence: Talleyrand's ambassadors know court gossip and
    troop levies — national-level picture, not per-army positions.

    Returns the best VisibilityTier (FULL > PARTIAL > STALE > UNKNOWN).
    If nation has no marshals, returns UNKNOWN.
    """
    best_vis = UNKNOWN
    best_priority = VISIBILITY_PRIORITY.get(UNKNOWN, 0)

    for marshal in world.marshals.values():
        if marshal.nation != nation_name:
            continue
        if marshal.strength <= 0:
            continue

        # Get visibility for the region this marshal is in
        intel = world.get_region_intel(marshal.location)
        vis = intel.visibility
        vis_priority = VISIBILITY_PRIORITY.get(vis, 0)

        if vis_priority > best_priority:
            best_vis = vis
            best_priority = vis_priority

            # Early exit if we found FULL — can't get better
            if best_vis == FULL:
                return FULL

    return best_vis


def _format_army_strength(total_strength: int, visibility: str) -> str:
    """Format army strength display based on visibility tier.

    NONE (UNKNOWN): "Unknown"
    STALE: Named bands
    PARTIAL: Approximate (~nearest 5k)
    FULL: Exact aggregate
    """
    if visibility == UNKNOWN:
        return "Unknown"

    if visibility == STALE:
        if total_strength < 10000:
            return "Negligible"
        elif total_strength < 30000:
            return "Minor Force"
        elif total_strength < 60000:
            return "Considerable"
        elif total_strength < 100000:
            return "Powerful"
        else:
            return "Dominant"

    if visibility == PARTIAL:
        rounded = round(total_strength / 5000) * 5000
        rounded = max(rounded, 5000) if total_strength > 0 else 0
        return f"~{int(rounded):,} men"

    # FULL
    return f"{int(total_strength):,} men"


# ============================================================================
# TAB 1: NATIONS
# ============================================================================

def _build_nations(world) -> List[Dict[str, Any]]:
    """Build nations tab: per-nation diplomatic overview."""
    player = world.player_nation
    all_nations = list(getattr(world, 'enemy_nations', []))
    nations = []

    for nation in all_nations:
        diplo_key = world._make_diplo_key(player, nation)
        diplomatic_state = world.diplomatic_states.get(diplo_key, "PEACE")
        relation = world.nation_relations.get(diplo_key, 0) or 0

        # Diplomat info
        diplomats = getattr(world, 'diplomats', {})
        diplomat = diplomats.get(nation)
        diplomat_info = None
        if diplomat:
            diplomat_info = {
                "name": diplomat.name,
                "personality": diplomat.personality,
                "skill": int(diplomat.skill or 0),
            }

        # Army strength with fog
        total_strength = sum(
            m.strength for m in world.marshals.values()
            if m.nation == nation and m.strength > 0
        )

        if nation == player:
            # Player always knows own army
            army_strength = f"{int(total_strength):,} men"
        else:
            visibility = _get_nation_visibility(nation, world)
            army_strength = _format_army_strength(total_strength, visibility)

        # Regions controlled (always visible — map control is public)
        regions_controlled = sum(
            1 for r in world.regions.values()
            if r.controller == nation
        )

        # Active treaties involving this nation
        active_treaties = []
        for pair_key, treaty in getattr(world, 'active_treaties', {}).items():
            treaty_nations = treaty.get("nations", [])
            if nation in treaty_nations or (player in treaty_nations and nation in treaty_nations):
                treaty_type = treaty.get("type", "unknown")
                if treaty_type not in active_treaties:
                    active_treaties.append(treaty_type)

        # Vassal eligibility: not already vassal, relation < -10 or at war, not France
        vassals = getattr(world, 'vassals', {})
        is_vassal = nation in vassals
        at_war = diplomatic_state == "WAR"
        vassal_eligible = (
            not is_vassal
            and (relation < -10 or at_war)
            and nation != player
        )

        # AI-AI relations: show diplomatic states with other AI nations
        # Fog-filtered: only show if player has PARTIAL+ intel on either nation
        ai_relations = []
        nation_vis = _get_nation_visibility(nation, world)
        nation_vis_priority = VISIBILITY_PRIORITY.get(nation_vis, 0)
        partial_priority = VISIBILITY_PRIORITY.get(PARTIAL, 3)

        for other_ai in all_nations:
            if other_ai == nation:
                continue
            other_vis = _get_nation_visibility(other_ai, world)
            other_vis_priority = VISIBILITY_PRIORITY.get(other_vis, 0)

            # Show if player has PARTIAL+ on either nation in the pair
            if nation_vis_priority >= partial_priority or other_vis_priority >= partial_priority:
                ai_diplo_key = world._make_diplo_key(nation, other_ai)
                ai_state = world.diplomatic_states.get(ai_diplo_key, "PEACE")
                ai_relations.append({
                    "nation": other_ai,
                    "state": ai_state,
                })

        # R17a: War score component breakdown for AT_WAR nations
        war_score_breakdown = None
        if diplomatic_state == "WAR":
            from backend.game_logic.diplomacy import calculate_war_score
            war_score_breakdown = calculate_war_score(
                player, nation, world, return_components=True
            )
            # int()-wrap all components for Godot
            if war_score_breakdown:
                war_score_breakdown = {
                    k: int(v) for k, v in war_score_breakdown.items()
                }

        # R17b: Proposal cooldowns remaining for this nation
        cooldowns = getattr(world, 'player_proposal_cooldowns', {})
        proposal_cooldowns = {}
        # Check nation-level cooldown (e.g. "Prussia": 3)
        nation_cd = cooldowns.get(nation, 0)
        if nation_cd > 0:
            proposal_cooldowns["nation"] = int(nation_cd)
        # Check per-type cooldowns (e.g. "Prussia_peace": 5)
        for cd_key, cd_val in cooldowns.items():
            if cd_key.startswith(f"{nation}_") and cd_val > 0:
                ptype = cd_key[len(nation) + 1:]
                proposal_cooldowns[ptype] = int(cd_val)

        nations.append({
            "name": nation,
            "diplomatic_state": diplomatic_state,
            "relation": int(relation),
            "diplomat": diplomat_info,
            "army_strength": army_strength,
            "regions_controlled": int(regions_controlled),
            "active_treaties": active_treaties,
            "vassal_eligible": vassal_eligible,
            "ai_relations": ai_relations,
            "war_score_breakdown": war_score_breakdown,
            "proposal_cooldowns": proposal_cooldowns if proposal_cooldowns else None,
        })

    return nations


# ============================================================================
# TAB 2: TREATIES
# ============================================================================

def _build_treaties(world) -> List[Dict[str, Any]]:
    """Build treaties tab: per active treaty."""
    treaties = []
    for pair_key, treaty in getattr(world, 'active_treaties', {}).items():
        nations = treaty.get("nations", [])
        nation_a = nations[0] if len(nations) > 0 else ""
        nation_b = nations[1] if len(nations) > 1 else ""

        clauses = []
        for clause in treaty.get("clauses", []):
            if isinstance(clause, dict):
                clauses.append(clause.get("description", str(clause)))
            else:
                clauses.append(str(clause))

        duration = treaty.get("duration", "permanent")
        if isinstance(duration, int):
            duration = int(duration)

        # R17c: Calculate ongoing gold/turn costs from treaty clauses
        gold_per_turn_costs = []
        for clause in treaty.get("clauses", []):
            if isinstance(clause, dict) and clause.get("type") == "gold_per_turn":
                gold_per_turn_costs.append({
                    "from": clause.get("from", ""),
                    "to": clause.get("to", ""),
                    "amount": int(clause.get("amount") or 0),
                })

        treaties.append({
            "nation_a": nation_a,
            "nation_b": nation_b,
            "treaty_type": treaty.get("type", "unknown"),
            "clauses": clauses,
            "duration": duration,
            "cancel_cost": 1,
            "gold_per_turn": gold_per_turn_costs if gold_per_turn_costs else None,
        })

    return treaties


# ============================================================================
# TAB 3: THREAT & COALITION
# ============================================================================

def _build_threat_coalition(world) -> Dict[str, Any]:
    """Build threat & coalition tab."""
    threat_level = int(getattr(world, 'threat_level', 0) or 0)

    # Threat tier
    if threat_level >= 80:
        threat_tier = "CRITICAL"
    elif threat_level >= 60:
        threat_tier = "HIGH"
    elif threat_level >= 30:
        threat_tier = "MODERATE"
    else:
        threat_tier = "LOW"

    # Threat sources this turn
    threat_sources = list(getattr(world, 'threat_sources_this_turn', []))

    # Qualifying nations
    from backend.game_logic.coalition import get_qualifying_nations
    qualifying = get_qualifying_nations(world)

    # Brewing
    brewing = getattr(world, 'coalition_brewing', None)
    coalition_brewing = brewing is not None
    brewing_turns_remaining = None
    if brewing:
        brewing_turns_remaining = int(brewing.get("turns_remaining") or 0)

    # Active coalition
    active_coalition_data = None
    coalition = getattr(world, 'active_coalition', None)
    if coalition:
        members_data = []
        combined_strength = 0
        for member in coalition.get("members", []):
            member_strength = sum(
                m.strength for m in world.marshals.values()
                if m.nation == member and m.strength > 0
            )
            combined_strength += member_strength

            # Fog band logic for coalition members
            vis = _get_nation_visibility(member, world)
            strength_display = _format_army_strength(member_strength, vis)

            we = world.war_exhaustion.get(member, 0) or 0
            members_data.append({
                "nation": member,
                "strength_display": strength_display,
                "war_exhaustion": int(we),
            })

        # Combined strength display — use best visibility across all members
        best_vis = UNKNOWN
        best_p = 0
        for member in coalition.get("members", []):
            vis = _get_nation_visibility(member, world)
            p = VISIBILITY_PRIORITY.get(vis, 0)
            if p > best_p:
                best_vis = vis
                best_p = p
        combined_strength_display = _format_army_strength(
            combined_strength, best_vis
        )

        active_coalition_data = {
            "name": coalition.get("name", "Unknown Coalition"),
            "leader": coalition.get("leader", ""),
            "posture": coalition.get("strategic_posture", "defensive"),
            "members": members_data,
            "combined_strength_display": combined_strength_display,
        }

    return {
        "threat_level": threat_level,
        "threat_tier": threat_tier,
        "threat_sources_this_turn": threat_sources,
        "qualifying_nations": qualifying,
        "coalition_brewing": coalition_brewing,
        "brewing_turns_remaining": brewing_turns_remaining,
        "active_coalition": active_coalition_data,
    }


# ============================================================================
# TAB 4: TALLEYRAND
# ============================================================================

def _build_talleyrand(world) -> Dict[str, Any]:
    """Build Talleyrand status tab."""
    player = world.player_nation
    diplomats = getattr(world, 'diplomats', {})
    talleyrand = diplomats.get(player)

    trust = int(talleyrand.trust or 0) if talleyrand else 0
    skill = int(talleyrand.skill or 0) if talleyrand else 0

    # Trust label
    if trust >= 80:
        trust_label = "Loyal"
    elif trust >= 50:
        trust_label = "Wary"
    elif trust >= 25:
        trust_label = "Suspicious"
    else:
        trust_label = "Treacherous"

    dp_remaining = int(getattr(world, 'diplomatic_points', 0) or 0)
    dp_max = int(getattr(world, 'max_diplomatic_points', 3) or 0)

    # Active mission
    active_mission = None
    mission = getattr(world, 'active_diplomatic_mission', None)
    if mission and not mission.get("completed"):
        active_mission = {
            "type": mission.get("type", ""),
            "target": mission.get("target", ""),
            "duration": int(mission.get("turns_active") or 0),
            "progress": mission.get("paused", False),
        }

    # Proposal in transit
    proposal_in_transit = None
    pit = getattr(world, 'proposal_in_transit', None)
    if pit:
        proposal_in_transit = {
            "target": pit.get("target", ""),
            "type": pit.get("type", pit.get("proposal", {}).get("type", "")),
            "eta": int(pit.get("eta") or pit.get("delivery_turn") or 0),
        }

    # Pending envoy count
    pending_envoy_count = int(len(getattr(world, 'diplomatic_queue', [])))

    # Sabotage warnings
    sabotage_warnings = []
    raw_sabotages = getattr(world, 'undetected_sabotages', [])
    for sab in raw_sabotages:
        if isinstance(sab, dict):
            sabotage_warnings.append({
                "target": sab.get("target", ""),
                "type": sab.get("type", ""),
                "turn": int(sab.get("turn") or 0),
            })
        else:
            sabotage_warnings.append(str(sab))

    # R29: Diplomatic history (last 20 events)
    diplomatic_history = []
    raw_history = getattr(world, 'diplomatic_history', [])
    for entry in raw_history:
        if isinstance(entry, dict):
            diplomatic_history.append({
                "turn": int(entry.get("turn") or 0),
                "type": entry.get("type", ""),
                "target": entry.get("target", ""),
                "nation": entry.get("nation", ""),
                "detail": entry.get("proposal_type", entry.get("treaty_type", "")),
            })
        else:
            diplomatic_history.append({"turn": 0, "type": str(entry), "target": "", "nation": "", "detail": ""})

    # R34: Diplomatic reliability
    reliability = getattr(world, 'diplomatic_reliability', {})
    player_reliability = int(reliability.get(player, 0))

    return {
        "trust": trust,
        "trust_label": trust_label,
        "skill": skill,
        "dp_remaining": dp_remaining,
        "dp_max": dp_max,
        "active_mission": active_mission,
        "proposal_in_transit": proposal_in_transit,
        "pending_envoy_count": pending_envoy_count,
        "sabotage_warnings": sabotage_warnings,
        "diplomatic_history": diplomatic_history,
        "diplomatic_reliability": player_reliability,
    }
