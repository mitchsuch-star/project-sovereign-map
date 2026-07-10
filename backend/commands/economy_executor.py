"""
Economy Executor — Economy, recruitment, garrison, building, and repair commands (R13A)

Extracted from executor.py: _execute_economy, _execute_recruit, _execute_garrison,
_execute_build, _execute_build_watchtower, _execute_repair.
Also includes _calculate_recruit_cost, _extract_building_type, and garrison constants.
"""
from typing import Dict
from backend.models.world_state import (
    WorldState,
    INFANTRY_RECRUIT_AMOUNT, CAVALRY_RECRUIT_AMOUNT, ARTILLERY_RECRUIT_AMOUNT,
    INFANTRY_RECRUIT_GOLD_COST_BASE, CAVALRY_RECRUIT_GOLD_COST_BASE, ARTILLERY_RECRUIT_GOLD_COST_BASE,
    INFANTRY_BASE_REGEN,
)


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
        # ES-7 (S7): estate redirect is a separate Net component too
        dotation_skim = int(income_data.get("dotation_skim", 0))
        net = (income_data["income"] - occupation - dotation_skim
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

        # ES-7 (S7): estate endowments — full income redirected to marshals
        if dotation_skim > 0:
            estates = [rd for rd in region_details if rd.get("estate_of")]
            lines.append(f"\n  Dotations: -{dotation_skim}g  ({len(estates)} endowed estates)")
            for rd in estates:
                lines.append(
                    f"    {rd['region']}: -{rd['dotation_cost']}g "
                    f"(estate of Marshal {rd['estate_of']})"
                )

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
                "dotation_skim": int(dotation_skim),
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

    def _execute_grant_dotation(self, command: Dict, game_state: Dict) -> Dict:
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
            list_eligible_estates,
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
