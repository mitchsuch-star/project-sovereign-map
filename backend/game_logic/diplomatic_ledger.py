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

ARMISTICE_DURATION = 5  # Must match diplomacy.py

# TH3: Human-readable threat source labels (module-level to avoid re-creation per call)
_THREAT_SOURCE_LABELS = {
    "battle_win": "Won a battle",
    "battle_loss": "Lost a battle",
    "capital_capture": "Captured an enemy capital",
    "region_capture": "Conquered territory",
    "war_declaration": "Declared war",
    "treaty_vassalization": "Vassalized via treaty",
    "conquest_vassalization": "Vassalized by conquest",
    "decisive_victory": "Won a decisive battle",
    "decay": "Natural threat decay",
    "treaty_annex": "Annexed territory via treaty",
    "territory_return": "Returned territory",
    "generous_peace": "Offered generous peace",
    "diplomatic_downgrade": "Downgraded diplomatic relations",
    "vassal_rebellion": "Vassal rebellion",
    "voluntary_vassal_release": "Released vassal voluntarily",
    "region_control_80": "Controls 80%+ of map",
    "region_control_70": "Controls 70%+ of map",
    "region_control_60": "Controls 60%+ of map",
}


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
        "current_turn": int(world.current_turn),
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
    active = set(world.get_active_nations())  # DLF-11
    all_nations = [n for n in getattr(world, 'enemy_nations', []) if n in active]
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
            # Defensive guard: enemy_nations should never include the player, but
            # if it does, show "Exact" for own army strength rather than fog-filtered.
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
        # DPF-1: No fog gate — diplomatic relations are public knowledge
        from backend.game_logic.diplomacy import get_relation_descriptor  # noqa: E402
        ai_relations = []
        for other_ai in all_nations:
            if other_ai == nation:
                continue
            ai_diplo_key = world._make_diplo_key(nation, other_ai)
            ai_state = world.diplomatic_states.get(ai_diplo_key, "PEACE")
            ai_relation_value = int(world.nation_relations.get(ai_diplo_key, 0) or 0)
            ai_relations.append({
                "nation": other_ai,
                "state": ai_state,
                "relation": ai_relation_value,
                "relation_descriptor": get_relation_descriptor(ai_relation_value),
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

        # N5: Trade income from diplomatic state
        from backend.game_logic.diplomacy import TRADE_INCOME
        trade_income = int(TRADE_INCOME.get(diplomatic_state, 0))

        # N6: Relation descriptor
        from backend.game_logic.diplomacy import get_relation_descriptor
        relation_descriptor = get_relation_descriptor(relation)

        # N7: Relation trend (rising/falling/stable from history)
        relation_trend = "stable"
        relation_history = getattr(world, 'relation_history', {})
        history_list = relation_history.get(diplo_key, [])
        if len(history_list) >= 2:
            delta = relation - history_list[-1]
            if delta > 2:
                relation_trend = "rising"
            elif delta < -2:
                relation_trend = "falling"

        nations.append({
            "name": nation,
            "diplomatic_state": diplomatic_state,
            "relation": int(relation),
            "relation_descriptor": relation_descriptor,
            "relation_trend": relation_trend,
            "diplomat": diplomat_info,
            "army_strength": army_strength,
            "regions_controlled": int(regions_controlled),
            "active_treaties": active_treaties,
            "vassal_eligible": vassal_eligible,
            "ai_relations": ai_relations,
            "war_score_breakdown": war_score_breakdown,
            "proposal_cooldowns": proposal_cooldowns if proposal_cooldowns else None,
            "trade_income": trade_income,
        })

    return nations


# ============================================================================
# TAB 2: TREATIES
# ============================================================================

def _build_treaties(world) -> List[Dict[str, Any]]:
    """Build treaties tab: per active treaty."""
    player = world.player_nation
    treaties = []
    for pair_key, treaty in getattr(world, 'active_treaties', {}).items():
        nations = treaty.get("nations", [])
        nation_a = nations[0] if len(nations) > 0 else ""
        nation_b = nations[1] if len(nations) > 1 else ""

        clauses = []
        for clause in treaty.get("clauses", []):
            if isinstance(clause, dict):
                desc = clause.get("description")
                if not desc:
                    # Bug 6 fix: Generate human-readable description from clause fields
                    ctype = clause.get("type", "unknown")
                    amount = clause.get("amount", 0)
                    c_from = clause.get("from", "")
                    c_to = clause.get("to", "")
                    _CLAUSE_LABELS = {
                        "gold_lump": "Gold payment",
                        "gold_per_turn": "Gold/turn",
                        "manpower_per_turn": "Manpower/turn",
                        "ap_per_turn": "AP/turn",
                        "territory_cede": "Territory cession",
                        "infantry_manpower": "Infantry levy",
                        "cavalry_manpower": "Cavalry levy",
                        "artillery_manpower": "Artillery provision",
                        "open_borders": "Open borders",
                        "non_aggression": "Non-aggression",
                        "protection_promised": "Military protection",
                    }
                    label = _CLAUSE_LABELS.get(ctype, ctype.replace("_", " ").title())
                    if amount and c_from:
                        desc = f"{label}: {int(amount)} ({c_from} -> {c_to})"
                    elif amount:
                        desc = f"{label}: {int(amount)}"
                    else:
                        desc = label
                clauses.append(desc)
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

        # T2: Turn signed
        turn_signed = int(treaty.get("turn_signed") or 0)

        # T3: Player vs AI-AI distinction
        involves_player = player in nations

        # T4: Armistice countdown
        armistice_remaining = None
        treaty_type = treaty.get("type", "unknown")
        if treaty_type == "armistice":
            armistice_turns = getattr(world, 'armistice_turns', {})
            pair_armistice = armistice_turns.get(pair_key, 0)
            armistice_remaining = int(max(0, ARMISTICE_DURATION - pair_armistice))

        treaties.append({
            "nation_a": nation_a,
            "nation_b": nation_b,
            "treaty_type": treaty_type,
            "clauses": clauses,
            "duration": duration,
            "cancel_cost": 1,
            "gold_per_turn": gold_per_turn_costs if gold_per_turn_costs else None,
            "turn_signed": turn_signed,
            "involves_player": involves_player,
            "armistice_remaining": armistice_remaining,
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

    # Threat sources this turn — with human-readable labels (TH3)
    raw_sources = list(getattr(world, 'threat_sources_this_turn', []))
    threat_sources = []
    for s in raw_sources:
        if isinstance(s, dict):
            source_key = s.get("source", "")
            amount = int(s.get("amount") or 0)
            label = _THREAT_SOURCE_LABELS.get(source_key, source_key.replace("_", " ").title())
            sign = "+" if amount >= 0 else ""
            threat_sources.append({
                "source": source_key,
                "label": label,
                "amount": amount,
                "display": f"{label} ({sign}{amount})",
            })
        else:
            threat_sources.append({"source": str(s), "label": str(s), "amount": 0, "display": str(s)})

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
    partial_priority = VISIBILITY_PRIORITY.get(PARTIAL, 3)
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

            we_raw = world.war_exhaustion.get(member, 0) or 0
            # Fix 13: Only show WE if PARTIAL+ visibility
            if VISIBILITY_PRIORITY.get(vis, 0) < partial_priority:
                we = 0
            else:
                we = we_raw
            # S4a: WE trend
            prev_we = getattr(world, '_prev_war_exhaustion', {}).get(member, 0)
            if we > prev_we:
                we_trend = "rising"
            elif we < prev_we:
                we_trend = "falling"
            else:
                we_trend = "stable"
            members_data.append({
                "nation": member,
                "strength_display": strength_display,
                "war_exhaustion": int(we),
                "war_exhaustion_trend": we_trend,
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

    # TH2: Coalition cooldown
    coalition_cooldown = int(getattr(world, 'coalition_cooldown', 0) or 0)

    # S5: Threat projection
    next_war_projection = min(100, threat_level + 20)
    threat_projection = {
        "current": threat_level,
        "after_next_war": next_war_projection,
        "brewing_threshold": 60,
        "instant_threshold": 80,
        "wars_until_brewing": max(0, (60 - threat_level + 19) // 20) if threat_level < 60 else 0,
        "wars_until_instant": max(0, (80 - threat_level + 19) // 20) if threat_level < 80 else 0,
    }

    return {
        "threat_level": threat_level,
        "threat_tier": threat_tier,
        "threat_sources_this_turn": threat_sources,
        "qualifying_nations": qualifying,
        "coalition_brewing": coalition_brewing,
        "brewing_turns_remaining": brewing_turns_remaining,
        "active_coalition": active_coalition_data,
        "coalition_cooldown": coalition_cooldown,
        # TH4: Dissolution conditions (static thresholds for display)
        "dissolution_threat_threshold": 20,
        "dissolution_war_exhaustion_limit": 80,
        # S5: Threat projection
        "threat_projection": threat_projection,
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

    # TA3: DP breakdown
    from backend.models.region import NATION_CAPITALS
    player_capital = NATION_CAPITALS.get(player, "Paris")
    controls_capital = False
    cap_region = world.regions.get(player_capital)
    if cap_region:
        controls_capital = cap_region.controller == player
    # Player uses authority_tracker, not nation_authority (matches calculate_dp caller in diplomacy.py)
    authority = world.authority_tracker.authority if hasattr(world, 'authority_tracker') else 60
    # Components
    dp_base = 3
    dp_skill_bonus = 1 if talleyrand and talleyrand.skill >= 8 else 0
    dp_authority_bonus = 1 if authority >= 60 else (-1 if authority < 30 else 0)
    dp_capital_penalty = -1 if not controls_capital else 0
    dp_breakdown = {
        "base": dp_base,
        "skill_bonus": dp_skill_bonus,
        "authority_bonus": dp_authority_bonus,
        "capital_penalty": dp_capital_penalty,
    }

    # Active mission
    active_mission = None
    mission = getattr(world, 'active_diplomatic_mission', None)
    if mission and not mission.get("completed"):
        mission_type = mission.get("type", "")

        # TA4: Mission effect descriptions
        from backend.game_logic.diplomatic_dialogue import MISSION_EFFECTS, MISSION_DP_COSTS
        _MISSION_EFFECT_TEXT = {
            "IMPROVE_RELATIONS": "+5 relation per turn",
            "COURT_NATION": "+5 relation per turn, 20% blowback risk",
            "GATHER_INTEL": "Full intel for 3 turns",
            "UNDERMINE_ALLIANCE": "-3 relation between targets per turn",
            "REASSURE_ALLY": "+3 relation per turn",
        }
        effect_text = _MISSION_EFFECT_TEXT.get(mission_type, "")
        dp_cost_per_turn = int(MISSION_DP_COSTS.get(mission_type, 1))

        # TA5: Remaining turns for fixed-duration missions
        remaining_turns = None
        effects = MISSION_EFFECTS.get(mission_type, {})
        if "duration" in effects:
            total_duration = effects["duration"]
            turns_active = int(mission.get("turns_active") or 0)
            remaining_turns = int(max(0, total_duration - turns_active))

        # DPF-2: Mission progress tracking
        from backend.game_logic.diplomacy import get_relation_descriptor as _get_rel_desc
        mission_target = mission.get("target", "")
        initial_relation = int(mission.get("initial_relation") or 0)
        player = getattr(world, 'player_nation', 'France')
        current_relation = int(world.nation_relations.get(
            world._make_diplo_key(player, mission_target), 0
        ) or 0)

        active_mission = {
            "type": mission_type,
            "target": mission_target,
            "duration": int(mission.get("turns_active") or 0),
            "paused": mission.get("paused", False),
            "effect_text": effect_text,
            "dp_cost_per_turn": dp_cost_per_turn,
            "remaining_turns": remaining_turns,
            "started_turn": int(mission.get("started_turn") or 0),
            "initial_relation": initial_relation,
            "current_relation": current_relation,
            "relation_delta": int(current_relation - initial_relation),
            "initial_descriptor": _get_rel_desc(initial_relation),
            "current_descriptor": _get_rel_desc(current_relation),
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
    SABOTAGE_TYPE_DISPLAY = {
        "softened": "Terms Weakened",
        "hardened": "Terms Hardened",
        "stalled": "Proposal Delayed",
        "ap_downgrade": "Authority Undermined",
        "unit_overpay": "Resources Wasted",
    }
    sabotage_warnings = []
    raw_sabotages = getattr(world, 'undetected_sabotages', [])
    for sab in raw_sabotages:
        if isinstance(sab, dict):
            raw_type = sab.get("type", "")
            sabotage_warnings.append({
                "target": sab.get("target", ""),
                "type": SABOTAGE_TYPE_DISPLAY.get(raw_type, raw_type.replace("_", " ").title()),
                "turn": int(sab.get("turn") or 0),
            })
        else:
            sabotage_warnings.append(str(sab))

    # R29: Diplomatic history (last 20 events)
    diplomatic_history = []
    raw_history = getattr(world, 'diplomatic_history', [])
    for entry in raw_history[-20:]:
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
        "dp_breakdown": dp_breakdown,
        "active_mission": active_mission,
        "proposal_in_transit": proposal_in_transit,
        "pending_envoy_count": pending_envoy_count,
        "sabotage_warnings": sabotage_warnings,
        "diplomatic_history": diplomatic_history,
        "diplomatic_reliability": player_reliability,
    }
