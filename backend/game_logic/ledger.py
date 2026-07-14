"""
Strategic Ledger — 6-section backend builder (Session B + Orders tab)

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
        Dict with forces, territories, economy, intel, manpower, orders sections.
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
        "orders": _build_orders(world, player),
        "authority": int(authority),
        "authority_label": authority_label,
        "actions_remaining": int(world.actions_remaining),
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
    """Format strategic order summary string (player-facing verbs, R7)."""
    from backend.display_names import get_strategic_display

    order = marshal.strategic_order
    if order is None:
        return "None"
    cmd = order.command_type
    target = order.target
    if cmd == "MOVE_TO":
        turns_left = len(order.path)
        return f"{get_strategic_display(cmd)} {target} ({turns_left} turns left)"
    if cmd == "PURSUE":
        return f"{get_strategic_display(cmd)} {target} (tracking)"
    if cmd == "SUPPORT":
        return f"{get_strategic_display(cmd)} {target} (active)"
    if cmd == "HOLD":
        return f"{get_strategic_display(cmd)} at {target}"
    return f"{get_strategic_display(cmd)} {target}"


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
    # ES-3 (S5): the over-limit surcharge is split out of Upkeep so the
    # economy tab can render it as its own line (§3 breakdown-visible).
    # calculate_turn_upkeep guarantees total == base + surcharge (even
    # under bankruptcy mercy), so the split lines reconcile to Net.
    upkeep_surcharge = int(upkeep_data.get("surcharge", 0))
    upkeep_base = upkeep - upkeep_surcharge
    # ES-2 (S6): recurring cost of holding non-homeland soil — its own
    # signed Net component (income stays GROSS), rendered as an
    # "Occupation" line so the visible lines still sum to Net (SC-33).
    occupation = int(income_data.get("occupation", 0))
    # ES-7 (S7): full income of endowed provinces redirected to marshals'
    # estates — its own signed Net component, rendered as a "Dotations"
    # line (SC-33 both-halves; forced by the NET_GOLD_COMPONENTS guard).
    dotation_skim = int(income_data.get("dotation_skim", 0))
    # ES-7 second pass (§0.6.8): the rente bill — its own signed Net
    # component, rendered as a "Rentes" line (same SC-33 contract).
    rente_cost = int(income_data.get("rente_cost", 0))
    # EC-U2 (Combat Overhaul Phase 4): per-turn maintenance of built
    # structures — its own signed Net component, rendered as an
    # "Infrastructure" line (same SC-33 contract; NET_GOLD_COMPONENTS-guarded).
    infrastructure = int(income_data.get("infrastructure", 0))

    # Trade income from diplomatic states (read-only calculation)
    from backend.game_logic.diplomacy import calculate_trade_income
    trade_income_all = calculate_trade_income(world)
    trade_income = int(trade_income_all.get(player, 0))

    # Admin bonus (unused AP → gold)
    admin_bonus = int(world._calculate_admin_bonus(player))

    # Treaty gold/turn income (clauses where we receive gold)
    treaty_gold = 0
    for pair_key, treaty in world.active_treaties.items():
        for clause in treaty.get("clauses", []):
            if clause.get("type") == "gold_per_turn" and clause.get("to") == player:
                treaty_gold += abs(clause.get("amount", 0))
            elif clause.get("type") == "gold_per_turn" and clause.get("from") == player:
                treaty_gold -= abs(clause.get("amount", 0))
    treaty_gold = int(treaty_gold)

    # Vassal tribute income
    # Golden Rule 8: mirror process_vassal_tribute's cached-index derivation —
    # a per-vassal full region scan here was O(vassals × regions) per request.
    vassal_tribute = 0
    for vassal_name, state in world.vassals.items():
        if state.get("lord") == player:
            tribute_rate = state.get("tribute_rate", 0.5)
            v_income = sum(
                world.regions[name].get_effective_income()
                for name in world.get_nation_regions(vassal_name)
            )
            vassal_tribute += int(v_income * tribute_rate)

    # SC-33 recurring settlement streams (G4F smoke follow-up): the
    # ratified gold_per_turn obligations the income phase actually moves —
    # previously the per-turn tribute was invisible everywhere except the
    # one-morning dispatch line. Sign mirrors `treaty_gold` (incoming
    # positive).
    settlement_gold = 0
    settlement_streams = []
    for entry in getattr(world, "recurring_settlement_payments", None) or []:
        if not isinstance(entry, dict):
            continue
        payer = str(entry.get("from") or "")
        recipient = str(entry.get("to") or "")
        stream_amount = int(entry.get("amount_per_turn", 0) or 0)
        stream_turns = int(entry.get("turns_remaining", 0) or 0)
        if stream_amount <= 0 or stream_turns <= 0:
            continue
        if player not in (payer, recipient):
            continue
        incoming = recipient == player
        settlement_gold += stream_amount if incoming else -stream_amount
        counterparty = payer if incoming else recipient
        settlement_streams.append({
            "direction": "incoming" if incoming else "outgoing",
            "counterparty": counterparty,
            "amount_per_turn": int(stream_amount),
            "turns_remaining": int(stream_turns),
            "display": (
                f"{'+' if incoming else '-'}{stream_amount}g/turn "
                f"{'from' if incoming else 'to'} {counterparty} "
                f"({stream_turns} turns remain)"
            ),
        })
    settlement_gold = int(settlement_gold)

    net = int(
        income + trade_income + admin_bonus + treaty_gold + vassal_tribute
        + settlement_gold - occupation - dotation_skim - rente_cost
        - infrastructure - upkeep_base - upkeep_surcharge
    )

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
        "trade_income": trade_income,
        "admin_bonus": admin_bonus,
        "treaty_gold": treaty_gold,
        "vassal_tribute": vassal_tribute,
        "settlement_gold": settlement_gold,
        "settlement_streams": settlement_streams,
        "occupation": occupation,
        "dotation_skim": dotation_skim,
        "rente_cost": rente_cost,
        "infrastructure": infrastructure,
        "upkeep": upkeep,
        "upkeep_base": upkeep_base,
        "upkeep_surcharge": upkeep_surcharge,
        # 0 = no limit (legacy world) — int-safe sentinel for Godot (GR2)
        "force_limit": int(upkeep_data.get("force_limit") or 0),
        "over_force_limit": bool(upkeep_data.get("over_limit", False)),
        "army_strength_total": int(upkeep_data.get("total_strength", 0)),
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
                strength_display = f"last seen: {get_strength_band(frozen)}"
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
            band = enemy["strength_display"].replace("last seen: ", "")
            nation_data[nation]["estimated_strength"] += BAND_MIDPOINTS.get(band, 0)
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


# ============================================================================
# ORDERS SECTION
# ============================================================================

from backend.display_names import get_strategic_display as _derive_order_display_name


def _derive_condition_text(order, world) -> str:
    """Derive human-readable condition text from StrategicCondition."""
    cond = order.condition
    if cond is None:
        if order.command_type == "MOVE_TO":
            remaining = len(order.path)
            if remaining > 0:
                return f"{remaining} region(s) left"
            return "arriving"
        if order.command_type == "PURSUE":
            return "tracking"
        if order.command_type == "HOLD":
            return "indefinite"
        if order.command_type == "SUPPORT":
            return "active"
        return "active"

    if cond.max_turns is not None:
        ref_turn = order.arrived_turn if order.arrived_turn is not None else order.started_turn
        elapsed = world.current_turn - ref_turn
        remaining = max(0, cond.max_turns - elapsed)
        return f"{remaining} turn(s) remaining"
    if cond.until_relieved:
        return "until relieved"
    if cond.until_battle_won:
        return "until battle won"
    if cond.until_marshal_arrives:
        return f"until {cond.until_marshal_arrives} arrives"
    if cond.until_marshal_destroyed:
        return f"until {cond.until_marshal_destroyed} destroyed"
    return "active"


def _build_orders(world, player: str) -> list:
    """Build orders section: per player marshal strategic order status."""
    active_orders = []
    idle_marshals = []

    for marshal in world.marshals.values():
        if marshal.nation != player:
            continue

        order = marshal.strategic_order
        if order is not None:
            condition_text = _derive_condition_text(order, world)

            active_orders.append({
                "marshal": marshal.name,
                "unit_type": _derive_unit_type(marshal),
                "location": marshal.location,
                "order_type": _derive_order_display_name(order.command_type),
                "order_type_raw": order.command_type,
                "target": order.target,
                "path_remaining": int(len(order.path)),
                "turns_active": int(world.current_turn - order.started_turn),
                "condition": condition_text,
                "started_turn": int(order.started_turn),
                "arrived_turn": int(order.arrived_turn) if order.arrived_turn is not None else -1,
                "has_order": True,
            })
        else:
            idle_marshals.append({
                "marshal": marshal.name,
                "unit_type": _derive_unit_type(marshal),
                "location": marshal.location,
                "order_type": "No active orders",
                "order_type_raw": "",
                "target": "",
                "path_remaining": 0,
                "turns_active": 0,
                "condition": "idle",
                "started_turn": 0,
                "arrived_turn": -1,
                "has_order": False,
            })

    return active_orders + idle_marshals
