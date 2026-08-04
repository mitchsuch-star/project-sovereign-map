"""
Economy Executor — Economy, recruitment, garrison, building, and repair commands (R13A)

Extracted from executor.py: _execute_economy, _execute_recruit, _execute_garrison,
_execute_build, _execute_build_watchtower, _execute_repair.
Also includes _calculate_recruit_cost, _extract_building_type, and garrison constants.
"""
from typing import Dict, Optional
from backend.models.world_state import (
    WorldState,
    INFANTRY_RECRUIT_AMOUNT, CAVALRY_RECRUIT_AMOUNT, ARTILLERY_RECRUIT_AMOUNT,
    INFANTRY_RECRUIT_GOLD_COST_BASE, CAVALRY_RECRUIT_GOLD_COST_BASE, ARTILLERY_RECRUIT_GOLD_COST_BASE,
    INFANTRY_BASE_REGEN,
)


# ── CO-4 (Combat Overhaul Phase 2): cap the per-corps regeneration ──────────
# The Field Review saw a besieged corps (Mack in Swabia) reinforce +10,000 in
# a single turn while the best assault removed ~5,000 — frontal attrition was
# literally unwinnable (spec §0.1, metric M3). A corps recruiting AWAY from a
# friendly supply depot or capital cannot raise a full batch: the reinforcement
# is capped to AI_CORPS_REGEN_CAP men. Sweep-tuned (spec §2.1); start 3,000.
#
# GR5: the cap is a property of the SHARED recruit executor, keyed on the
# recruiting corps' supply context — the enemy AI recruit rung supplies the
# cap when its corps is in the field (the input value that differs), and the
# same helper is available to any caller. Per spec §4 Phase 2, the player's
# own base recruit at a capital/depot is untouched (it satisfies the exemption)
# and retreat-recovery is a separate path the cap never sees.
AI_CORPS_REGEN_CAP = 3000


def region_has_friendly_supply(region) -> bool:
    """CO-4: a corps recruiting here can draw a full reinforcement batch —
    the region is a capital or hosts a supply depot. Everywhere else is 'the
    field' and reinforcement is capped to AI_CORPS_REGEN_CAP."""
    if region is None:
        return False
    if getattr(region, "region_type", None) == "capital":
        return True
    try:
        return bool(region.has_building("supply_depot"))
    except Exception:
        return False


class EconomyExecutor:
    """Handles economy, recruitment, garrison, building, and repair commands."""

    # Garrison constants (Phase 6.2)
    GARRISON_DETACHMENT_SIZE = 3000
    GARRISON_MIN_MARSHAL_STRENGTH = 8000
    GARRISON_MAX_PER_NATION = 3  # Cap includes capital garrisons

    # Watchtower cost constants (Phase 6 Fog - Session 35)
    WATCHTOWER_GOLD_COST = 250
    WATCHTOWER_BUILD_TIME = 2

    def __init__(self, parent_executor):
        self._executor = parent_executor

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
        admin_bonus = world.admin_actions_remaining * 25  # Potential bonus if saved

        # ES-2 (S6): occupation cost is a separate Net component (income is gross)
        occupation = int(income_data.get("occupation", 0))
        # EC-W1: income suspended by hostile armies — separate Net component
        contributions = int(income_data.get("contributions", 0))
        # EC-W2: war-effort spending from the chest — separate Net component
        war_effort = int(income_data.get("war_effort", 0))
        # ES-7 (S7): estate redirect is a separate Net component too
        dotation_skim = int(income_data.get("dotation_skim", 0))
        # ES-7 second pass (§0.6.8): the rente bill
        rente_cost = int(income_data.get("rente_cost", 0))
        # EC-W5b: infrastructure maintenance was MISSING from this report's
        # net (the applied net in process_income_phase subtracts it), so the
        # projection lied whenever structures existed.
        infrastructure = int(income_data.get("infrastructure", 0))
        net = (income_data["income"] - occupation - contributions - war_effort
               - dotation_skim - rente_cost - infrastructure
               - upkeep_data["total"] + admin_bonus)
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

        # ES-2 (S6): occupation cost on non-homeland provinces
        if occupation > 0:
            occupied = [rd for rd in region_details if rd.get("occupation_cost", 0) > 0]
            lines.append(f"\n  Occupation: -{occupation}g  ({len(occupied)} non-homeland regions)")
            if income_data.get("occupation_halved"):
                lines.append("    (HALVED - bankruptcy mercy)")
            for rd in occupied:
                lines.append(
                    f"    {rd['region']}: -{rd['occupation_cost']}g "
                    f"({rd['stability_label'].lower()})"
                )

        # EC-W1: hostile armies standing on our provinces — revenues eaten
        # in place, named by province
        if contributions > 0:
            disrupted_rows = [rd for rd in region_details if rd.get("disrupted")]
            lines.append(f"\n  Contributions: -{contributions}g  "
                         f"({len(disrupted_rows)} provinces under enemy occupation)")
            for rd in disrupted_rows:
                lines.append(
                    f"    {rd['region']}: -{rd['contributions_cost']}g "
                    f"(enemy army on our soil)"
                )

        # EC-W2: the war consuming the war chest (scaled by war exhaustion)
        if war_effort > 0:
            we_val = int(getattr(world, "war_exhaustion", {}).get(nation, 0) or 0)
            lines.append(f"\n  War Effort: -{war_effort}g  "
                         f"(war exhaustion {we_val} drains the war chest)")

        # ES-7 (S7): estate endowments — full income redirected to marshals
        if dotation_skim > 0:
            estates = [rd for rd in region_details if rd.get("estate_of")]
            lines.append(f"\n  Dotations: -{dotation_skim}g  ({len(estates)} endowed estates)")
            for rd in estates:
                lines.append(
                    f"    {rd['region']}: -{rd['dotation_cost']}g "
                    f"(estate of Marshal {rd['estate_of']})"
                )

        # ES-7 second pass (§0.6.8): rentes — treasury pensions at premium
        if rente_cost > 0:
            from backend.game_logic.dotation import get_rente_cost
            pensioned = [
                m for m in world.marshals.values()
                if m.nation == nation and int(getattr(m, "pension", 0)) > 0
                and not getattr(m, "captured_by", "")
            ]
            lines.append(f"\n  Rentes: -{rente_cost}g  "
                         f"({len(pensioned)} pensioned marshals)")
            for m in pensioned:
                lines.append(
                    f"    Marshal {m.name}: {int(m.pension)}g/turn face "
                    f"-> -{get_rente_cost(int(m.pension))}g with fees"
                )

        # EC-W5b: infrastructure maintenance line (was missing entirely —
        # the cost applied every turn but the report never named it)
        if infrastructure > 0:
            lines.append(f"\n  Infrastructure: -{infrastructure}g  "
                         f"(structure maintenance)")

        # Upkeep breakdown
        upkeep_breakdown = upkeep_data["breakdown"]
        lines.append(f"\n  Upkeep: -{upkeep_data['total']}g  ({len(upkeep_breakdown)} marshals)")
        if upkeep_data.get("halved"):
            lines.append("    (HALVED - bankruptcy mercy)")
        for ub in upkeep_breakdown:
            lines.append(f"    {ub['marshal']} ({ub['strength']:,} troops): -{ub['upkeep']}g")
        # ES-3 (S5): over-limit surcharge line — the army exceeds the
        # nation's force limit, so the excess pays super-linear upkeep
        if upkeep_data.get("surcharge", 0) > 0:
            lines.append(
                f"    Over force limit "
                f"({upkeep_data['total_strength']:,} / {upkeep_data['force_limit']:,}): "
                f"-{upkeep_data['surcharge']}g surcharge"
            )

        # Admin bonus
        if admin_bonus > 0:
            lines.append(f"\n  Admin bonus: +{admin_bonus}g  ({world.admin_actions_remaining} unused AP x 25)")
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
                "occupation": int(occupation),
                "contributions": int(contributions),
                "war_effort": int(war_effort),
                "dotation_skim": int(dotation_skim),
                "rente_cost": int(rente_cost),
                "infrastructure": int(infrastructure),
                "upkeep": int(upkeep_data["total"]),
                "admin_bonus": int(admin_bonus),
                "net": int(net),
                "treasury": int(treasury),
                "bankruptcy_turns": int(bankruptcy),
            }],
            "new_state": game_state
        }

    # W6-11 (E-CA-3) blessed defaults: recruiting mid-war costs 3x (band
    # 2-4x), and recruiting above the ES-3 force limit costs a further
    # (1 + overage ratio) — rebuilding a mauled army mid-war becomes a
    # treasury event instead of a rounding error; peacetime rebuilding
    # stays cheap. Europe-scoped (N1: the legacy fixture world BOOTS at
    # war with Britain/Prussia — its economy pins must not move).
    WAR_RECRUIT_COST_MULT = 3

    def _calculate_recruit_cost(self, region, world, base_cost: int = 200,
                                nation: str = None, marshal=None) -> int:
        """Calculate recruitment gold cost based on region properties.

        Priority: Capital discount wins over settling premium.
        Parameterized base_cost: 200 for infantry, 300 for cavalry.

        W6-11: pass `nation` to price the recruit for that nation's
        situation — x3 at war, x(1 + overage) above the force limit
        (Europe-scoped; both multipliers compose on the regional price).
        The AI pays the same price through this same helper (GR5).

        MC-2b: pass `marshal` (the recruiting marshal) to apply The
        Intendance — administration >= 8 prices the levy 15% under, <= 3
        prices it 15% over (marshal.get_recruit_cost_modifier, single
        source). Composes LAST, on the full nation-priced cost; scoped
        inside the same Europe block for the same N1 reason.
        """
        # Capital discount: 25% off (checked first — always wins)
        if region.region_type == "capital":
            cost = int(base_cost * 0.75)
        # Settling stability premium: 50% more (stability 51-75)
        elif 51 <= region.stability <= 75:
            cost = int(base_cost * 1.50)
        else:
            cost = int(base_cost)

        if (nation
                and getattr(world, "sovereign_map", "legacy") == "europe"):
            if world.get_nations_at_war_with(nation):
                cost = int(cost * self.WAR_RECRUIT_COST_MULT)
            force_limit = world.get_force_limit(nation)
            if force_limit:
                total_strength = int(
                    world.calculate_turn_upkeep(nation)["total_strength"])
                if total_strength > force_limit:
                    overage = (total_strength - force_limit) / force_limit
                    cost = int(cost * (1.0 + overage))
            if marshal is not None:
                # round(), not int(): 200 * 1.15 is 229.999... in floats, and
                # truncation would break shown-=-applied by a gold.
                cost = int(round(cost * marshal.get_recruit_cost_modifier()))
        return int(cost)

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
            marshal, error = self._executor._fuzzy_match_marshal(marshal_specified, world)
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
            from backend.models.region import NATION_CAPITALS
            capital = world.player_capital or NATION_CAPITALS.get(world.player_nation, "Paris")
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
            self._executor._auto_break_square(recruit_marshal, "recruit")
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

        # S5-5: the TRUE fixed corps size, captured before the CO-4 field cap
        # may lower NEW_TROOPS. The PF-7 "drafted in fixed corps of N" note must
        # cite the batch, not the capped delivery (else a field-capped levy
        # misreports the corps size as, e.g., 3,000 when infantry corps are
        # 10,000).
        full_corps_size = NEW_TROOPS

        # CO-4 (Combat Overhaul Phase 2): the SYMMETRIC field-regen cap. A corps
        # reinforcing in the field — away from a friendly supply depot or
        # capital — cannot raise a full batch; the levy is capped to
        # AI_CORPS_REGEN_CAP men. This is ONE rule keyed on the recruit
        # region's supply, identical for player and enemy (GR5 — "same executor,
        # the supply context is the differing input"): it makes a besieged
        # corps net-lose ground under sustained superior assault (metric M3) and
        # stops EITHER side out-regenerating an assault by rebuilding a forward
        # corps. Recruiting at a depot or capital is uncapped, so the strategic
        # loop is "reinforce at your bases, then march to the front" (build a
        # forward supply_depot to levy there). Artillery's 3,000 batch is
        # already at the floor. Manpower drawn and morale dilution follow the
        # capped figure; gold stays the batch price (a pure throughput cap, not
        # a price penalty — keeps the ledger simple). An explicit
        # command["reinforcement_cap"] may only lower it further, never raise.
        _recruit_region = world.get_region(recruitment_location)
        field_cap = (None if region_has_friendly_supply(_recruit_region)
                     else AI_CORPS_REGEN_CAP)
        _override = command.get("reinforcement_cap")
        if _override is not None and _override > 0:
            field_cap = _override if field_cap is None else min(field_cap, _override)
        field_regen_capped = False
        if field_cap is not None and 0 < field_cap < NEW_TROOPS:
            NEW_TROOPS = int(field_cap)
            field_regen_capped = True

        # Build base_message with correct type and amount
        type_label = recruit_type
        if marshal_specified:
            base_message = f"{recruit_marshal.name} recruits {NEW_TROOPS:,} {type_label} at {recruit_marshal.location}"
        elif location_specified:
            base_message = f"{recruit_marshal.name} recruits {NEW_TROOPS:,} {type_label} for {location_specified} ({distance} regions away)"
        else:
            base_message = f"{recruit_marshal.name} recruits {NEW_TROOPS:,} {type_label} (nearest to capital)"

        # CO-4: name the field-levy cap so a capped reinforcement is legible.
        if field_regen_capped:
            base_message += f" (field levy — no depot; capped at {NEW_TROOPS:,})"

        # PF-7: acknowledge a requested troop COUNT. Recruitment is drafted in
        # fixed per-arm corps (the batch size is deliberate — honoring an
        # arbitrary number is an escalated balance change, homed in
        # DESIGN_REFINEMENT), so a requested amount is NOTED rather than
        # silently dropped. AI recruits pass no raw_command, so this is
        # player-facing only.
        import re as _re
        _raw_recruit = (command.get("raw_command") or "").lower()
        _amt = _re.search(r'(\d[\d,]*)\s*(k|thousand)?', _raw_recruit)
        if _amt:
            _req = int(_amt.group(1).replace(",", ""))
            if _amt.group(2):
                _req *= 1000
            if _req > 0 and _req != full_corps_size:
                base_message += (f" (recruitment is drafted in fixed corps of "
                                 f"{full_corps_size:,}, Sire — your {_req:,} is noted)")

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
                regen_rate = world.get_manpower_regen_rates(acting_nation)["infantry"]
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
        gold_cost = self._calculate_recruit_cost(
            region, world, base_cost=cost_base, nation=acting_nation,
            marshal=recruit_marshal)

        nation_treasury = world.nation_gold.get(acting_nation, 0)
        if nation_treasury < gold_cost:
            return {
                "success": False,
                "message": f"Berthier shakes his head. 'The treasury cannot support this, Sire. Need {gold_cost} gold, have {nation_treasury}.'"
            }

        # Phase 6.2 Audit Fix #6: Training Ground morale bonus buffed from +15% to +30%
        if region.has_building("training_ground"):
            RECRUIT_MORALE = 70

        # MC-1: Moore's "Shorncliffe System" — his recruits arrive drilled,
        # morale floor 60. max() keeps the Training Ground's 70 strictly
        # better. One name-check covers the AI recruit path too (GR5).
        shorncliffe_note = ""
        if (recruit_marshal and hasattr(recruit_marshal, 'ability')
                and recruit_marshal.ability.get("name") == "Shorncliffe System"
                and RECRUIT_MORALE < 60):
            RECRUIT_MORALE = 60
            shorncliffe_note = (
                f" The recruits arrive drilled — {recruit_marshal.name}'s "
                f"Shorncliffe System (morale {RECRUIT_MORALE}, not 40)."
            )

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

        # MC-2b: The Intendance — the note appears exactly when the modifier
        # priced this levy (shown = applied; Europe-scoped like the seam).
        intendance_pct = 0
        if (recruit_marshal is not None
                and getattr(world, "sovereign_map", "legacy") == "europe"):
            mod = recruit_marshal.get_recruit_cost_modifier()
            intendance_pct = int(round((mod - 1.0) * 100))
        if intendance_pct != 0:
            sign = "+" if intendance_pct > 0 else ""
            cost_note += (
                f" ({recruit_marshal.name}'s intendance: "
                f"{sign}{intendance_pct}%)"
            )

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
            "message": f"{soft_correction}{base_message} - Cost: {gold_cost} gold{cost_note}. Morale: {old_morale}% -> {new_morale}%{shorncliffe_note}{pool_line}{morale_warning}",
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
                "intendance_pct": int(intendance_pct),
                "pool_before": int(available),
                "pool_after": int(pool_after),
            }],
            "new_state": game_state
        }

    # ========================================
    # MARSHAL RECRUITMENT — "The Marshalate" (Jealousy v3.2 final phase)
    # docs/MARSHAL_RECRUITMENT_SPEC.md — player and AI share this path (GR5).
    # ========================================

    def _execute_recruit_marshal(self, command: Dict, game_state) -> Dict:
        """Commission a new marshal from the nation's authored candidate
        pool: authored gold price + an initial corps drawn from the
        infantry manpower pool; arrives at the capital (or the richest
        held homeland province). AI commissions through the same gate
        via `_acting_nation` (GR5)."""
        from backend.game_logic.recruitment import (
            check_commission, commission_marshal, find_candidate,
            get_marshal_pool,
        )
        world = game_state["world"]
        acting_nation = command.get("_acting_nation") or world.player_nation

        pool = get_marshal_pool(world, acting_nation)
        if not pool:
            return {
                "success": False,
                "message": ("No candidates await a commission — the "
                            "marshalate's bench is empty."),
            }

        wanted = (command.get("target") or command.get("marshal") or "").strip()
        if not wanted:
            names = ", ".join(c.get("name", "?") for c in pool)
            return {
                "success": False,
                "message": (f"Whom shall we raise to the marshalate, Sire? "
                            f"Candidates: {names}."),
            }
        candidate = find_candidate(world, acting_nation, wanted)
        if candidate is None:
            names = ", ".join(c.get("name", "?") for c in pool)
            return {
                "success": False,
                "message": (f"No candidate named '{wanted}' awaits a "
                            f"commission. Candidates: {names}."),
            }

        refusal = check_commission(world, acting_nation, candidate)
        if refusal is not None:
            return {"success": False, "message": refusal}

        summary = commission_marshal(world, acting_nation, candidate)
        seeds = summary.get("seeds", {})
        seed_note = ""
        if seeds and acting_nation == world.player_nation:
            from backend.models.marshal import Marshal
            parts = [f"{name} ({Marshal.get_relationship_label(value)})"
                     for name, value in sorted(seeds.items())]
            seed_note = " He arrives with a history: " + ", ".join(parts) + "."

        return {
            "success": True,
            "message": (f"Marshal {summary['marshal']} accepts his "
                        f"commission and raises a corps of "
                        f"{summary['corps']:,} at {summary['location']} — "
                        f"{summary['cost']}g.{seed_note}"),
            "events": [{
                "type": "marshal_commissioned",
                "marshal": summary["marshal"],
                "location": summary["location"],
                "gold_cost": int(summary["cost"]),
                "corps": int(summary["corps"]),
            }],
            "new_state": game_state,
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
        self._executor._auto_break_square(marshal, "garrison")

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
                          if m.location == region_name and m.nation != marshal.nation and m.strength > 0
                          and world.is_at_war(marshal.nation, m.nation)]
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

        # Validation: nation garrison cap (includes capital garrisons).
        # Golden Rule 8: count over the cached region index (Slice 8 audit).
        nation_garrisons = sum(
            1 for r_name in world.get_nation_regions(marshal.nation)
            if world.regions[r_name].garrison_strength > 0
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

    # ════════════════════════════════════════════════════════════════════════════
    # ES-7 ESTATE ENDOWMENT (Economy Revisit S7): grant_dotation
    # ════════════════════════════════════════════════════════════════════════════

    def _execute_grant_dotation(self, command: Dict, game_state: Dict,
                                raw_text: str = "") -> Dict:
        """Endow a marshal with an estate in a conquered province (ES-7).

        Player-facing surface: "Endow {marshal} with the Duchy of {province}".
        Internal action id stays grant_dotation. The province's FULL effective
        income is redirected to the marshal's household each turn (§0.6.7
        amendment 1) and it is exempt from the ES-2 occupation cost
        (amendment 4). Eligibility (amendment 4): player-held, non-capital,
        non-vassal, un-dotated, NON-HOMELAND provinces only.

        Costs 1 ADMIN AP (routing layer) + the investiture fee deducted HERE
        in-executor (GR5 — the AI grants through this same method and its
        admin phase applies leftover-AP gold directly, so a bonus-path fee
        would double-count). NO trust bump on grant — the endowment is a
        promise, not a purchase (the reframe's falsifiable core).

        Used by both player and AI (Building Blocks): the AI rung lives in
        enemy_ai._pick_admin_action.
        """
        from backend.game_logic.dotation import (
            check_estate_eligibility, compute_investiture_fee, derive_title,
            get_expectation, get_satisfaction, is_dotation_world,
            list_eligible_estates, strip_dead_estate_claims,
        )

        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state available"}

        if not is_dotation_world(world):
            return {
                "success": False,
                "message": "Estate endowments are not available in this campaign."
            }

        marshal_name = (command.get("marshal") or "").strip()
        if not marshal_name:
            return {
                "success": False,
                "message": "Berthier raises an eyebrow. 'Which marshal shall "
                           "the Emperor honor, Sire? Example: endow Ney with "
                           "a conquered province.'"
            }

        marshal, error = self._executor._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        acting_nation = command.get("_acting_nation") or marshal.nation
        if marshal.nation != acting_nation:
            return {
                "success": False,
                "message": f"Marshal {marshal.name} serves {marshal.nation} — "
                           f"we cannot endow another crown's marshal."
            }

        region_name = command.get("target")
        # W6-1 (BUG-CA-3): a target the player never NAMED is a parser guess
        # (live audit: "Endow Ney with an estate" arrived with the first
        # region of the world dict as target and refused with "We do not
        # hold White Russia"). When the raw text is available and does not
        # mention the region (raw or humanized form), treat the target as
        # missing — ask with the eligible list, never default-scan.
        if region_name and raw_text:
            from backend.display_names import humanize_entity_name
            raw_lower = raw_text.lower()
            if (str(region_name).lower() not in raw_lower
                    and humanize_entity_name(str(region_name)).lower()
                    not in raw_lower):
                region_name = None
        if not region_name:
            eligible = list_eligible_estates(world, acting_nation)
            if eligible:
                sample = ", ".join(eligible[:4])
                return {
                    "success": False,
                    "message": f"Which province, Sire? Eligible estates: {sample}. "
                               f"Example: 'endow {marshal.name} with {eligible[0]}'."
                }
            return {
                "success": False,
                "message": "We hold no eligible province, Sire. An estate must "
                           "stand on conquered soil — non-capital, outside the "
                           "homeland, and not already endowed."
            }

        eligible_ok, reason = check_estate_eligibility(world, acting_nation,
                                                       region_name)
        if not eligible_ok:
            return {"success": False, "message": reason}

        region = world.regions[region_name]

        # Investiture fee — deducted IN-executor (see docstring). Creating
        # the title (first estate) costs the fee; adding land to an
        # existing title is 1 AP only.
        fee = compute_investiture_fee(marshal)
        treasury = world.nation_gold.get(acting_nation, 0)
        if treasury < fee:
            return {
                "success": False,
                "message": f"The treasury cannot fund the investiture, Sire. "
                           f"Need {fee} gold, have {treasury}."
            }
        if fee > 0:
            world.nation_gold[acting_nation] = int(treasury - fee)
            world.record_gold_spent(acting_nation, fee)

        # §0.6.8 item 5: a DEAD foreign claim (province gained by treaty,
        # still on an enemy marshal's rolls until the next prune) no longer
        # blocks eligibility — strip it NOW so the one-estate-per-region
        # invariant holds through the grant.
        strip_dead_estate_claims(world, region_name)

        # The endowment itself. NO trust change — paying stops the bleed,
        # never buys trust (named negative-assertion test).
        marshal.dotation_regions.append(region_name)
        title = derive_title(region_name)
        estate_income = int(region.get_effective_income())
        expectation = get_expectation(marshal)
        satisfaction = get_satisfaction(marshal, world)

        world.log_event({
            "type": "dotation_granted",
            "marshal": marshal.name,
            "nation": acting_nation,
            "region": region_name,
            "title": title,
            "estate_income": estate_income,
            "fee": int(fee),
        })

        fee_note = f" Investiture: {fee} gold." if fee > 0 else ""
        if satisfaction >= expectation:
            standing = "His expectation is met — his loyalty will bleed no further."
        else:
            standing = (f"He expects {expectation}g/turn of estates and now "
                        f"holds {satisfaction}g/turn — the endowment falls short.")
        return {
            "success": True,
            "message": (f"By Imperial decree, Marshal {marshal.name} is endowed "
                        f"with {region_name} and styled {title}. Its revenues "
                        f"({estate_income}g/turn) now sustain his household, "
                        f"not the treasury.{fee_note} {standing}"),
            "events": [{
                "type": "dotation_granted",
                "marshal": marshal.name,
                "region": region_name,
                "title": title,
                "estate_income": int(estate_income),
                "fee": int(fee),
                "expectation": int(expectation),
                "satisfaction": int(satisfaction),
            }],
            "new_state": game_state
        }

    # ════════════════════════════════════════════════════════════════════════════
    # ES-7 SECOND PASS (§0.6.8): grant_pension / revoke_pension — THE RENTE
    # ════════════════════════════════════════════════════════════════════════════

    def _execute_grant_pension(self, command: Dict, game_state: Dict) -> Dict:
        """Grant (or re-size) a marshal's rente — the treasury alternative
        to land.

        Face = expectation − estate income at grant time (one rente per
        marshal; granting again after new victories re-sizes it — the
        top-up verb). Face counts fully toward satisfaction; the treasury
        pays ceil(RENTE_PREMIUM × face) EVERY turn through the income
        phase — the recurring premium is the whole cost, so there is no
        fee here and no title ever. NO trust bump (same rule as the
        estate: a promise, not a purchase). GR5: the AI pensions through
        this same method (enemy_ai rente rung).
        """
        from backend.game_logic.dotation import (
            build_rente_offer, is_dotation_world,
        )

        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state available"}

        if not is_dotation_world(world):
            return {
                "success": False,
                "message": "Rentes are not available in this campaign."
            }

        marshal_name = (command.get("marshal") or "").strip()
        if not marshal_name:
            return {
                "success": False,
                "message": "Berthier dips his pen. 'Whose household shall the "
                           "treasury sustain, Sire? Example: grant Ney a rente.'"
            }

        marshal, error = self._executor._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        acting_nation = command.get("_acting_nation") or marshal.nation
        if marshal.nation != acting_nation:
            return {
                "success": False,
                "message": f"Marshal {marshal.name} serves {marshal.nation} — "
                           f"we cannot pension another crown's marshal."
            }

        if getattr(marshal, "captured_by", ""):
            return {
                "success": False,
                "message": f"Marshal {marshal.name} sits in a foreign capital — "
                           f"his household must wait upon his release, Sire."
            }

        offer = build_rente_offer(marshal, world)
        face, cost = int(offer["face"]), int(offer["cost"])
        if face <= 0:
            held = int(getattr(marshal, "pension", 0))
            if held > 0:
                return {
                    "success": False,
                    "message": (f"Marshal {marshal.name}'s expectation is "
                                f"already met — his rente of {held}g/turn "
                                f"stands unchanged."),
                }
            return {
                "success": False,
                "message": (f"Marshal {marshal.name}'s expectation is already "
                            f"met — no rente is needed, Sire."),
            }

        previous = int(getattr(marshal, "pension", 0))
        marshal.pension = int(face)

        world.log_event({
            "type": "rente_granted",
            "marshal": marshal.name,
            "nation": acting_nation,
            "face": int(face),
            "cost": int(cost),
            "previous": int(previous),
        })

        resize_note = (f" (his previous rente of {previous}g/turn is folded in)"
                       if previous > 0 else "")
        return {
            "success": True,
            "message": (f"By Imperial decree, Marshal {marshal.name} is granted "
                        f"a rente of {face}g/turn upon the treasury{resize_note}. "
                        f"With fees and arrears it will cost the crown "
                        f"{cost}g/turn — paper is dearer than land, Sire, and "
                        f"it buys no title. It holds his loyalty for exactly "
                        f"as long as it is paid."),
            "events": [{
                "type": "rente_granted",
                "marshal": marshal.name,
                "face": int(face),
                "cost": int(cost),
                "previous": int(previous),
            }],
            "new_state": game_state
        }

    def _execute_revoke_pension(self, command: Dict, game_state: Dict) -> Dict:
        """Withdraw a marshal's rente.

        The shortfall machinery reopens on the next reconciliation (grace
        window, then erosion) — withdrawing favor has the same teeth as
        losing an estate; no extra penalty is stacked here.
        """
        from backend.game_logic.dotation import get_rente_cost, is_dotation_world

        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state available"}

        if not is_dotation_world(world):
            return {
                "success": False,
                "message": "Rentes are not available in this campaign."
            }

        marshal_name = (command.get("marshal") or "").strip()
        if not marshal_name:
            return {
                "success": False,
                "message": "Berthier hesitates. 'Whose rente shall the "
                           "treasury withdraw, Sire?'"
            }

        marshal, error = self._executor._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        acting_nation = command.get("_acting_nation") or marshal.nation
        if marshal.nation != acting_nation:
            return {
                "success": False,
                "message": f"Marshal {marshal.name} serves {marshal.nation} — "
                           f"his rente is not ours to withdraw."
            }

        previous = int(getattr(marshal, "pension", 0))
        if previous <= 0:
            return {
                "success": False,
                "message": f"Marshal {marshal.name} holds no rente, Sire."
            }

        saved = get_rente_cost(previous)
        marshal.pension = 0

        world.log_event({
            "type": "rente_revoked",
            "marshal": marshal.name,
            "nation": acting_nation,
            "face": int(previous),
        })

        # Honest copy (review fix): after estate appreciation the estates
        # alone may cover his full expectation — revoking the now-redundant
        # rente reopens nothing, and the message must not threaten erosion
        # that cannot happen.
        from backend.game_logic.dotation import get_expectation, get_satisfaction
        if get_satisfaction(marshal, world) >= get_expectation(marshal):
            consequence = ("His estates sustain his expectation without it — "
                           "the paper was redundant, Sire.")
        else:
            consequence = ("He will remember who stopped paying, Sire: unmet "
                           "expectation frays loyalty after its grace expires.")

        return {
            "success": True,
            "message": (f"Marshal {marshal.name}'s rente of {previous}g/turn "
                        f"is withdrawn — the treasury keeps its {saved}g/turn. "
                        f"{consequence}"),
            "events": [{
                "type": "rente_revoked",
                "marshal": marshal.name,
                "face": int(previous),
            }],
            "new_state": game_state
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


# ════════════════════════════════════════════════════════════════════
# "THE LEVY IS OPEN" — the establishment as a first-class number
# (econ spec review, `docs/audits/ECON_SPEC_REVIEW_2026_08_04.md` §6)
# ════════════════════════════════════════════════════════════════════
# The played campaign's central finding: ⊕ France boots **+59,000 over**
# its own force limit, so the first ten turns teach that recruitment is
# forbidden; by turn 12 it was UNDER the limit with a full pool, and
# nothing ever said the gate had re-opened. The engine computed every
# figure and told the player none of them — the ledger rendered the force
# limit ONLY inside `if over_limit_surcharge > 0`, i.e. exactly when the
# gate was shut, and hid it the moment it opened.
#
# This is the single source every surface reads. No new serialized field:
# all of it is derived from figures that already existed.

# The pricing vehicle. `_calculate_recruit_cost` touches no instance state
# beyond class constants, so one throwaway sub-executor prices the levy
# without standing up a whole CommandExecutor (which prints, and which
# world_state cannot import at module scope anyway).
_LEVY_PRICER: Optional['EconomyExecutor'] = None


def _levy_pricer() -> 'EconomyExecutor':
    global _LEVY_PRICER
    if _LEVY_PRICER is None:
        _LEVY_PRICER = EconomyExecutor(None)
    return _LEVY_PRICER


def get_levy_status(world, nation: str = None) -> dict:
    """Establishment headroom, the live infantry price, and the pool.

    Returns int-only fields (GR2). `force_limit` 0 means "no limit" — the
    legacy world — and every consumer must treat that as "do not render",
    exactly as the existing ledger sentinel does.
    """
    nation = nation or world.player_nation
    limit = world.get_force_limit(nation) or 0
    upkeep = world.calculate_turn_upkeep(nation)
    total = int(upkeep.get("total_strength", 0))
    pool = int(world.manpower_pools.get(nation, {}).get("infantry", 0))

    price = 0
    capital = world.get_nation_capital(nation)
    region = world.get_region(capital) if capital else None
    if region is not None:
        price = int(_levy_pricer()._calculate_recruit_cost(
            region, world, base_cost=INFANTRY_RECRUIT_GOLD_COST_BASE,
            nation=nation))

    headroom = max(0, limit - total) if limit else 0
    return {
        "force_limit": int(limit),
        "army_strength": int(total),
        # Positive only on ONE side each — the two are never both non-zero,
        # so a renderer can branch on whichever it finds.
        "headroom": int(headroom),
        "over_by": int(max(0, total - limit)) if limit else 0,
        "infantry_price": int(price),
        "infantry_amount": int(INFANTRY_RECRUIT_AMOUNT),
        "infantry_pool": int(pool),
        # The gate is OPEN when there is room under the ordinance AND the
        # depots can actually fill it. Both halves matter: the played
        # campaign had headroom from turn 12 and a full pool, and was told
        # about neither.
        "open": bool(limit and headroom >= INFANTRY_RECRUIT_AMOUNT
                     and pool >= INFANTRY_RECRUIT_AMOUNT),
    }
