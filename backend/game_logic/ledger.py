"""
Strategic Ledger — 5-section backend builder (Session B)

Builds a structured dict for the Godot Strategic Ledger screen.
All values int()-wrapped per CLAUDE.md rule: "All numbers to Godot: int()".

Fog-filtered: intel section uses RegionIntel visibility, never raw marshal data.
"""

import math
from typing import Dict, Any

from backend.models.intel import (
    FULL, PARTIAL, STALE, UNKNOWN,
    get_strength_band,
)
from backend.game_logic.dispatch import BAND_MIDPOINTS
from backend.models.world_state import (
    MAX_INFANTRY_POOL, MAX_CAVALRY_POOL, MAX_ARTILLERY_POOL,
    INFANTRY_RECRUIT_AMOUNT, CAVALRY_RECRUIT_AMOUNT, ARTILLERY_RECRUIT_AMOUNT,
    INFANTRY_RECRUIT_GOLD_COST_BASE, CAVALRY_RECRUIT_GOLD_COST_BASE,
    ARTILLERY_RECRUIT_GOLD_COST_BASE,
)


def build_strategic_ledger(world) -> Dict[str, Any]:
    """
    Build the strategic ledger dict for Godot rendering.

    Args:
        world: WorldState instance

    Returns:
        Dict with forces, territories, economy, intel, manpower sections.
        All numeric values int()-wrapped.
    """
    player = world.player_nation

    # Authority — global player stat (V2b)
    authority = int(world.authority_tracker.authority) if hasattr(world, 'authority_tracker') else 100
    if authority >= 80:
        authority_label = "Strong"
    elif authority >= 50:
        authority_label = "Normal"
    else:
        authority_label = "Weak"

    return {
        "forces": _build_forces(world, player),
        "territories": _build_territories(world, player),
        "economy": _build_economy(world, player),
        "intel": _build_intel(world, player),
        "manpower": _build_manpower(world, player),
        "authority": int(authority),
        "authority_label": authority_label,
    }


# ============================================================================
# FORCES SECTION
# ============================================================================

def _derive_status(marshal) -> str:
    """Derive marshal status from priority chain (highest wins)."""
    if marshal.broken:
        return "broken"
    if marshal.retreating:
        return "retreating"
    if marshal.drilling or marshal.drilling_locked:
        return "drilling"
    if marshal.fortified:
        return "fortified"
    if marshal.in_strategic_mode:
        cmd = marshal.strategic_order.command_type
        if cmd == "HOLD":
            return "holding"
        if cmd == "PURSUE":
            return "pursuing"
        if cmd == "MOVE_TO":
            return "moving_to"
        if cmd == "SUPPORT":
            return "supporting"
    return "idle"


def _derive_strategic_order_summary(marshal) -> str:
    """Format strategic order summary string."""
    order = marshal.strategic_order
    if order is None:
        return "None"
    cmd = order.command_type
    target = order.target
    if cmd == "MOVE_TO":
        turns_left = len(order.path)
        return f"MOVE_TO {target} ({turns_left} turns left)"
    if cmd == "PURSUE":
        return f"PURSUE {target} (tracking)"
    if cmd == "SUPPORT":
        return f"SUPPORT {target} (active)"
    if cmd == "HOLD":
        return f"HOLD at {target}"
    return f"{cmd} {target}"


def _derive_unit_type(marshal) -> str:
    """Derive unit type string."""
    if getattr(marshal, 'artillery', False):
        return "artillery"
    if getattr(marshal, 'cavalry', False):
        return "cavalry"
    return "infantry"


def _build_forces(world, player: str) -> list:
    """Build forces section: per player marshal."""
    forces = []
    for marshal in world.marshals.values():
        if marshal.nation != player:
            continue
        forces.append({
            "name": marshal.name,
            "type": _derive_unit_type(marshal),
            "personality": marshal.personality,
            "location": marshal.location,
            "strength": int(marshal.strength),
            "morale": int(marshal.morale),
            "trust": int(marshal.trust.value),
            "stance": marshal.stance.value,
            "status": _derive_status(marshal),
            "strategic_order": _derive_strategic_order_summary(marshal),
            "battles_won": int(marshal.battles_won),
            "battles_lost": int(marshal.battles_lost),
            "special_flags": {
                "shock_ready": marshal.shock_bonus > 0,
                "counter_punch": marshal.counter_punch_available,
                "reckless": int(marshal.recklessness) if getattr(marshal, 'cavalry', False) else 0,
                "exhausted": marshal._get_exhaustion_penalty() > 0,
            },
        })
    return forces


# ============================================================================
# TERRITORIES SECTION
# ============================================================================

def _build_territories(world, player: str) -> list:
    """Build territories section: per player-controlled region."""
    territories = []
    for region in world.regions.values():
        if region.controller != player:
            continue

        # Buildings
        buildings = []
        for b in region.buildings:
            status = "damaged" if b.get("damaged", False) else "built"
            buildings.append({"name": b["type"], "status": status})
        if region.building_under_construction:
            buc = region.building_under_construction
            buildings.append({
                "name": buc["type"],
                "status": f"constructing ({buc['turns_remaining']}t)",
            })

        # Supply status
        total_occupant_strength = sum(
            m.strength for m in world.marshals.values()
            if m.location == region.name
        )
        supply_status = "OK"
        if total_occupant_strength > region.supply_capacity:
            supply_status = "Over capacity"

        # Occupant count
        occupant_count = sum(
            1 for m in world.marshals.values()
            if m.location == region.name
        )

        territories.append({
            "name": region.name,
            "terrain": region.terrain,
            "region_type": region.region_type,
            "buildings": buildings,
            "garrison": int(region.garrison_strength),
            "supply_capacity": int(region.supply_capacity),
            "occupant_count": int(occupant_count),
            "supply_status": supply_status,
            "stability": int(region.stability),
            "war_damage": int(region.war_damage * 100),
            "income": int(region.get_effective_income()),
        })
    return territories


# ============================================================================
# ECONOMY SECTION
# ============================================================================

def _build_economy(world, player: str) -> dict:
    """Build economy section."""
    income_data = world.calculate_turn_income(player)
    upkeep_data = world.calculate_turn_upkeep(player)

    income = int(income_data["income"])
    upkeep = int(upkeep_data["total"])
    net = int(income - upkeep)

    # Construction queue: iterate player regions with active builds
    construction_queue = []
    for region in world.regions.values():
        if region.controller != player:
            continue
        if region.building_under_construction is not None:
            buc = region.building_under_construction
            construction_queue.append({
                "region": region.name,
                "building": buc["type"],
                "turns_remaining": int(buc["turns_remaining"]),
            })

    # Income breakdown per region
    income_breakdown = []
    for region in world.regions.values():
        if region.controller != player:
            continue
        income_breakdown.append({
            "region": region.name,
            "income": int(region.get_effective_income()),
            "type": region.region_type,
        })

    return {
        "treasury": int(world.gold),
        "income": income,
        "upkeep": upkeep,
        "net": net,
        "bankruptcy_turns": int(world.bankruptcy_turns),
        "construction_queue": construction_queue,
        "income_breakdown": income_breakdown,
    }


# ============================================================================
# INTEL SECTION
# ============================================================================

def _format_strength_display(strength: int) -> str:
    """Format exact strength with commas (e.g. 45000 -> '45,000')."""
    return f"{int(strength):,}"


def _build_intel(world, player: str) -> dict:
    """Build intel section: fog-filtered enemy sightings."""
    known_enemies = []
    # Track best sighting per marshal name to dedup
    best_sightings: Dict[str, dict] = {}

    unknown_count = 0

    for region_name, region in world.regions.items():
        intel = world.get_region_intel(region_name)
        if intel.visibility == UNKNOWN:
            unknown_count += 1
            continue

        for km in intel.known_marshals:
            name = km.get("name", "?")
            nation = km.get("nation", "?")

            # Skip player marshals
            if nation == player:
                continue

            # Determine strength display based on visibility
            if intel.visibility == FULL:
                strength_val = km.get("strength", 0)
                strength_display = _format_strength_display(strength_val)
            elif intel.visibility == PARTIAL:
                band = km.get("band") or get_strength_band(km.get("strength", 0))
                strength_display = band
            elif intel.visibility == STALE:
                frozen = km.get("strength", 0)
                strength_display = f"last seen: {_format_strength_display(frozen)}"
            else:  # LAST_KNOWN
                strength_display = "unknown"

            entry = {
                "name": name,
                "nation": nation,
                "location": region_name,
                "strength_display": strength_display,
                "visibility": intel.visibility,
            }

            # Dedup: best visibility wins
            from backend.models.intel import VISIBILITY_PRIORITY
            if name not in best_sightings:
                best_sightings[name] = entry
            else:
                existing_vis = best_sightings[name]["visibility"]
                if VISIBILITY_PRIORITY.get(intel.visibility, 0) > VISIBILITY_PRIORITY.get(existing_vis, 0):
                    best_sightings[name] = entry

    known_enemies = list(best_sightings.values())

    # Nation summaries
    nation_data: Dict[str, dict] = {}
    for enemy in known_enemies:
        nation = enemy["nation"]
        if nation not in nation_data:
            nation_data[nation] = {
                "nation": nation,
                "known_marshals": 0,
                "estimated_strength": 0,
                "regions_controlled": 0,
            }
        nation_data[nation]["known_marshals"] += 1

        # Estimate strength from display
        vis = enemy["visibility"]
        if vis == FULL:
            # Parse exact strength from formatted string
            raw = enemy["strength_display"].replace(",", "")
            try:
                nation_data[nation]["estimated_strength"] += int(raw)
            except ValueError:
                pass
        elif vis == PARTIAL:
            band = enemy["strength_display"]
            nation_data[nation]["estimated_strength"] += BAND_MIDPOINTS.get(band, 0)
        elif vis == STALE:
            # Parse "last seen: N" format
            parts = enemy["strength_display"].replace("last seen: ", "").replace(",", "")
            try:
                nation_data[nation]["estimated_strength"] += int(parts)
            except ValueError:
                pass
        # LAST_KNOWN: "unknown" — add 0

    # Count regions controlled per enemy nation
    for region in world.regions.values():
        if region.controller and region.controller != player:
            nation = region.controller
            if nation not in nation_data:
                nation_data[nation] = {
                    "nation": nation,
                    "known_marshals": 0,
                    "estimated_strength": 0,
                    "regions_controlled": 0,
                }
            nation_data[nation]["regions_controlled"] += 1

    # Ensure all estimated_strength values are int
    nation_summaries = []
    for nd in nation_data.values():
        nd["estimated_strength"] = int(nd["estimated_strength"])
        nd["regions_controlled"] = int(nd["regions_controlled"])
        nd["known_marshals"] = int(nd["known_marshals"])
        nation_summaries.append(nd)

    return {
        "known_enemies": known_enemies,
        "nation_summaries": nation_summaries,
        "unknown_region_count": int(unknown_count),
    }


# ============================================================================
# MANPOWER SECTION
# ============================================================================

def _build_manpower(world, player: str) -> dict:
    """Build manpower section: pool status + regen rates."""
    pools = world.manpower_pools.get(player, {})
    rates = world.get_manpower_regen_rates(player)

    pool_configs = {
        "infantry": {
            "max": MAX_INFANTRY_POOL,
            "recruit_amount": INFANTRY_RECRUIT_AMOUNT,
            "recruit_base_cost": INFANTRY_RECRUIT_GOLD_COST_BASE,
        },
        "cavalry": {
            "max": MAX_CAVALRY_POOL,
            "recruit_amount": CAVALRY_RECRUIT_AMOUNT,
            "recruit_base_cost": CAVALRY_RECRUIT_GOLD_COST_BASE,
        },
        "artillery": {
            "max": MAX_ARTILLERY_POOL,
            "recruit_amount": ARTILLERY_RECRUIT_AMOUNT,
            "recruit_base_cost": ARTILLERY_RECRUIT_GOLD_COST_BASE,
        },
    }

    result = {}
    for pool_type, config in pool_configs.items():
        current = int(pools.get(pool_type, 0))
        max_val = int(config["max"])
        regen = int(rates.get(pool_type, 0))

        # turns_until_full
        if current >= max_val:
            turns_until_full = 0
        elif regen > 0:
            turns_until_full = int(math.ceil((max_val - current) / regen))
        else:
            turns_until_full = -1

        result[pool_type] = {
            "current": current,
            "max": max_val,
            "regen_rate": regen,
            "recruit_amount": int(config["recruit_amount"]),
            "recruit_base_cost": int(config["recruit_base_cost"]),
            "cost_note": "Modified by region stability (+/-25%)",
            "turns_until_full": int(turns_until_full),
        }

    return result
