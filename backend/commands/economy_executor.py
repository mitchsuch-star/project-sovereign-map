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


def _recruit_block_reason(world) -> str:
    """Why no marshal could take the recruits — CA8-11.

    Position 3.5's levy headline advertises `10,000 foot cost 450 gold at
    Paris`, and `recruit 10000 infantry at Paris` answered *"No marshal is
    available to receive reinforcements at Paris, Sire."* with no reason
    given, in the state a Napoleonic campaign is normally in: every marshal
    in Germany or Italy, and infantry carrying `movement_range` 1. The
    affordance built to give the treasury a use was unusable at the place
    its own headline names.

    `find_nearest_marshal_to_region` already computed the per-marshal
    reasons and discarded them. This states them, and names the rule.
    """
    blocked = list(getattr(world, "_last_nearest_marshal_block", None) or [])
    if not blocked:
        return ""
    shown = "; ".join(blocked[:3])
    more = f" (and {len(blocked) - 3} others)" if len(blocked) > 3 else ""
    return (f" Recruits join a marshal who can reach the depot: {shown}"
            f"{more}. March a corps within range, or name one directly "
            f"(\"recruit 10000 infantry with Ney\").")


def _decree_preamble(world, acting_nation: str) -> str:
    """Who is issuing this reward, and in what register.

    CA8-21 (creative audit, Aug 4 2026): the reward decrees were one
    f-string with no actor branch, while `acting_nation` sat in scope four
    lines above and was ignored — so Bavaria, an electorate, issued an
    *Imperial* decree, and the Austrian court addressed Napoleon as "Sire".
    Latent until now only because the client does not render the enemy
    phase's `message` field (CA8-6); it goes live the moment that is fixed,
    which is why the two land together.

    France's own council keeps its exact wording, byte-for-byte.
    """
    player = getattr(world, "player_nation", "France")
    if acting_nation == player:
        return "By Imperial decree"
    from backend.display_names import humanize_entity_name
    return f"By decree of the court of {humanize_entity_name(acting_nation)}"


class EconomyExecutor:
    """Handles economy, recruitment, garrison, building, and repair commands."""

    # Garrison constants (Phase 6.2)
    GARRISON_DETACHMENT_SIZE = 3000
    GARRISON_MIN_MARSHAL_STRENGTH = 8000
    GARRISON_MAX_PER_NATION = 3  # Cap includes capital garrisons

    # Watchtower cost constants (Phase 6 Fog - Session 35)
    WATCHTOWER_GOLD_COST = 250
    WATCHTOWER_BUILD_TIME = 2

    # WO slice 8: promoted from function-locals so the region panel's
    # build chips can quote the SAME numbers the executors apply
    # (`_execute_recruit` / `_execute_repair` read these — no copies).
    RECRUIT_MORALE_BASE = 40      # Green conscripts base morale
    RECRUIT_MORALE_TRAINED = 70   # with a training_ground in the province
    REPAIR_COST = 150
    # WO slice 8 in-game pass: how much war damage one repair clears.
    # Promoted so the war-damage repair chip can quote what this executor
    # actually applies (the chip is new — before it, war damage had no
    # button at all and the only route was knowing to type `repair <region>`).
    WAR_DAMAGE_REPAIR_FRACTION = 0.15

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
        # EB-5a: requisitions from disrupted enemy provinces (positive)
        requisitions = int(income_data.get("requisitions", 0))
        # EB-2: the overseas/colonial pool (positive)
        overseas = int(income_data.get("overseas", 0))
        # EB-1: the Charges of Empire (absorbs EC-W2's War Effort)
        state_charges = int(income_data.get("state_charges", 0))
        # ES-7 (S7): estate redirect is a separate Net component too
        dotation_skim = int(income_data.get("dotation_skim", 0))
        # ES-7 second pass (§0.6.8): the rente bill
        rente_cost = int(income_data.get("rente_cost", 0))
        # EC-W5b: infrastructure maintenance was MISSING from this report's
        # net (the applied net in process_income_phase subtracts it), so the
        # projection lied whenever structures existed.
        infrastructure = int(income_data.get("infrastructure", 0))
        # ════════════════════════════════════════════════════════════════
        # CA8-10 (creative audit, Aug 4 2026): the two screens that report
        # France's income disagreed by 124% — on turn 1 the treasury report
        # projected `+926g` while the end-turn line for the same turn read
        # `Net: +2073g`, with a different upkeep, a different surcharge, a
        # Grande Armée line the report did not carry and an `Other: +1320g`
        # it had never heard of. A new player literally cannot answer "how
        # much money do I make."
        #
        # Cause: this net was hand-assembled from a subset of the streams.
        # It omitted `admiralty` — which sits in the SAME `income_data`
        # dict it was already reading and IS subtracted by the applied net —
        # and omitted blockade, trade income, treaty gold and vassal
        # tribute entirely. EC-W5b had fixed exactly this defect for
        # infrastructure three lines above, one stream at a time.
        #
        # The fix is to stop hand-assembling. `ledger._build_economy` is the
        # surface whose Net is pinned to equal the signed sum of its
        # declared components (`NET_GOLD_COMPONENTS`, the reconciliation
        # guard), so this report now reads its figures from there. Adding a
        # future gold stream can no longer desynchronise the two screens,
        # because there is only one place left that knows the answer.
        # ════════════════════════════════════════════════════════════════
        from backend.game_logic.ledger import _build_economy
        econ = _build_economy(world, nation)
        net = int(econ["net"])
        trade_income = int(econ.get("trade_income", 0))
        blockade = int(econ.get("blockade", 0))
        admiralty = int(econ.get("admiralty", 0))
        vassal_tribute = int(econ.get("vassal_tribute", 0))
        treaty_gold = int(econ.get("treaty_gold", 0))
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

        # EB-5a: what our own armies requisition from provinces they disrupt
        if requisitions > 0:
            lines.append(f"\n  Requisitions: +{requisitions}g  "
                         f"(our armies live off the enemy's provinces)")

        # CA8-10: trade, and the blockade eating it. Both were absent, and
        # trade is one of the largest single streams a naval power moves.
        if trade_income:
            lines.append(f"\n  Trade: +{trade_income}g  (treaty trade income)")
        if blockade:
            lines.append(f"  Blockade: -{blockade}g  "
                         f"(enemy fleets close our ports)")
        # EB-2: the overseas/colonial pool, sea-power-modulated
        if overseas > 0:
            lines.append(f"\n  Overseas trade: +{overseas}g  "
                         f"(the colonies and the sea lanes)")
        if vassal_tribute:
            lines.append(f"\n  Vassal tribute: +{vassal_tribute}g")
        if treaty_gold:
            sign = "+" if treaty_gold >= 0 else ""
            lines.append(f"\n  Treaty gold: {sign}{treaty_gold}g/turn")

        # EB-1: the Charges of Empire — condition-priced draw on the chest
        # (absorbs EC-W2's War Effort; the WE term rides inside the rate).
        #
        # CA8-10's rule carries over: a zero is not a reason to withhold the
        # mechanic; it is the cheapest moment to teach it. The named terms
        # explain the rate the charge applies (shown = applied).
        charges_rate = world.get_state_charges_rate(nation)
        rate_terms = charges_rate.get("terms", [])
        term_str = "; ".join(f"{t['label']} +{t['amount']}" for t in rate_terms)
        if state_charges > 0:
            lines.append(f"\n  Charges of Empire: -{state_charges}g  "
                         f"(rate {charges_rate['rate']}: {term_str})")
        elif rate_terms:
            lines.append(f"\n  Charges of Empire: -0g  (the chest sits at its "
                         f"working floor; above it the rate is "
                         f"{charges_rate['rate']}: {term_str})")

        # CA8-10: the fleet's own bill, which sits in the same income dict
        # this report was already reading and was simply never subtracted.
        if admiralty:
            lines.append(f"\n  Admiralty: -{admiralty}g  (fleet upkeep)")

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
                "requisitions": int(requisitions),
                "overseas": int(overseas),
                "state_charges": int(state_charges),
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
        # WO slice 8: the digits live on the class so the build chips
        # quote what this function applies.
        RECRUIT_MORALE = self.RECRUIT_MORALE_BASE

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
                    "message": (
                        f"Berthier scans the dispatches. 'No marshal is "
                        f"available to receive reinforcements at "
                        f"{location_specified}, Sire.'"
                        f"{_recruit_block_reason(world)}")
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
                    "message": ("Berthier scans the dispatches. 'No marshal "
                                "is available to receive reinforcements, "
                                "Sire.'" + _recruit_block_reason(world))
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
            RECRUIT_MORALE = self.RECRUIT_MORALE_TRAINED

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
                f"Shorncliffe System (morale {RECRUIT_MORALE}, not "
                f"{self.RECRUIT_MORALE_BASE})."
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

    @classmethod
    def garrison_refusal_probe(cls, world, marshal):
        """The garrison gates as a PURE read — the reason a garrison would
        be refused HERE, right now, or None if it would be allowed.

        WO slice 6 review round, the PF-4 `move_refusal_probe` pattern.
        `naval.over_lift_refusal` advises detaching a garrison to bring an
        over-lift corps under the transports' cap, and its first cut read
        the nation-wide count ALONE — so it promised the remedy on soil we
        do not control (the §4.3 beachhead, the one place an over-lift
        refusal is reachable from foreign ground) and on a province that
        already holds a garrison. Measured: Bernadotte at Flanders was told
        a detachment "would bring him under the lift" and the executor
        answered "A garrison already holds Flanders".

        Advisory copy must consult the gate, never a copy of it — that is
        the CA9 through-line this project keeps paying for. Extracted
        verbatim from `_execute_garrison`'s prologue, which now calls it.
        """
        marshal_name = marshal.name
        region_name = marshal.location
        region = world.regions.get(region_name)
        if not region:
            return f"{marshal_name} is in an unknown region, Your Majesty."
        if region.controller != marshal.nation:
            return (f"We do not control {region_name}, Your Majesty. "
                    f"We cannot garrison enemy territory.")
        enemies_present = [
            m for m in world.marshals.values()
            if m.location == region_name and m.nation != marshal.nation
            and m.strength > 0 and world.is_at_war(marshal.nation, m.nation)]
        if enemies_present:
            return (f"Enemy forces contest {region_name}. We cannot "
                    f"garrison while under threat, Your Majesty.")
        if region.garrison_strength > 0:
            return f"A garrison already holds {region_name}, Your Majesty."
        # Golden Rule 8: count over the cached region index.
        nation_garrisons = sum(
            1 for r_name in world.get_nation_regions(marshal.nation)
            if world.regions[r_name].garrison_strength > 0)
        if nation_garrisons >= cls.GARRISON_MAX_PER_NATION:
            return (f"Berthier shakes his head. 'We already maintain "
                    f"{nation_garrisons} garrisons, Your Majesty. Our supply "
                    f"lines cannot support another. Maximum "
                    f"{cls.GARRISON_MAX_PER_NATION} garrisons per nation.'")
        if marshal.strength < cls.GARRISON_MIN_MARSHAL_STRENGTH:
            return (f"{marshal_name}'s forces are too depleted to spare a "
                    f"garrison, Your Majesty. We need at least "
                    f"{cls.GARRISON_MIN_MARSHAL_STRENGTH:,} men to leave "
                    f"troops behind.")
        return None

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
        refusal = self.garrison_refusal_probe(world, marshal)
        if refusal is not None:
            return {"success": False, "message": refusal}

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
            dismiss_reward_notices, estate_yield, get_expectation,
            restate_reward_notice,
            get_satisfaction, get_shortfall, is_dotation_world,
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

        # NP-0: the sovereign is never endowed — he grants, he does not
        # receive (NAPOLEON_SPEC §6.1, in-character refusal).
        if getattr(marshal, "is_sovereign", False):
            return {
                "success": False,
                "message": f"{marshal.name} needs no estate, Sire — "
                           f"the Empire is his estate."
            }

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
        # CA8 sweep 4 review: this figure went into the confirmation
        # sentence AND both `dotation_granted` payloads while omitting the
        # disruption term, so the message contradicted itself in one
        # paragraph — "its revenues (200g/turn) now sustain his household"
        # beside "now holds 0g/turn".
        estate_income = estate_yield(world, region_name)
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

        # Aug 23, 2026 (user: "when you pay them it doesn't dismiss their
        # popup of wanting"): the reward rail was reconciled ONLY by the
        # once-per-turn `process_dotation_state`, so this very response
        # shipped "his expectation is met" alongside a standing tray row
        # reading "holds 0g". Retire it here. Deliberately dismiss-only, not
        # re-post: `create_notification` mints a fresh uuid every time and
        # the client's chime dedupes on that id, so re-stating a still-short
        # row would ring the grievance bell AT THE MOMENT OF PAYMENT. If a
        # shortfall remains, the next turn's pass re-posts it honestly.
        # Gated on the debt actually being SETTLED (review round, 4b09e59):
        # the first cut dismissed on any success, so endowing a 0g war-torn
        # province — or REVOKING a rente — retired a HIGH "his loyalty is
        # fraying" row that was still true, and trust went on falling 3/turn
        # with nothing on screen. Paying in part leaves the row standing; its
        # figures are refreshed in place, keeping the row's id so the desk
        # bell does not ring at the moment of payment (UX23-R2, LANDED —
        # `restate_reward_notice` is the superset of the old
        # dismiss-if-settled call: it retires on the same `shortfall <= 0`
        # gate, and otherwise re-quotes the live price the rail's own button
        # now spends an administrative action on).
        restate_reward_notice(world, marshal)

        fee_note = f" Investiture: {fee} gold." if fee > 0 else ""
        decree = _decree_preamble(world, acting_nation)
        if satisfaction >= expectation:
            standing = "His expectation is met — his loyalty will bleed no further."
        else:
            standing = (f"He expects {expectation}g/turn of estates and now "
                        f"holds {satisfaction}g/turn — the endowment falls short.")
        # XR-4 (Econ Balance gate EB-3, + review [4]): a 0g estate is a
        # legal and honest grant, but the copy must name the TRUE recovery
        # mechanism — a DISRUPTED estate pays nothing until the hostile
        # army is driven off (its stability is falling under it), while a
        # war-torn one recovers as the province's stability does.
        recovery_note = ""
        if estate_income <= 0:
            if region_name in world.get_disrupted_regions():
                recovery_note = (" The estate lies under enemy occupation "
                                 "and yields nothing — its revenues return "
                                 "when the invader is driven off.")
            else:
                recovery_note = (" The estate lies war-torn and yields nothing "
                                 "today — its revenues will recover as the "
                                 "province's stability does.")
        return {
            "success": True,
            "message": (f"{decree}, Marshal {marshal.name} is endowed "
                        f"with {region_name} and styled {title}. Its revenues "
                        f"({estate_income}g/turn) now sustain his household, "
                        f"not the treasury.{fee_note}{recovery_note} {standing}"),
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
            build_rente_offer, dismiss_reward_notices, get_shortfall,
            restate_reward_notice,
            is_dotation_world, rente_would_change,
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

        # NP-0: the sovereign draws no rente — the treasury is already his
        # (NAPOLEON_SPEC §6.1, in-character refusal).
        if getattr(marshal, "is_sovereign", False):
            return {
                "success": False,
                "message": f"{marshal.name} draws no rente, Sire — "
                           f"the treasury is already his."
            }

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
        held = int(getattr(marshal, "pension", 0))
        shortfall = get_shortfall(marshal, world)
        # Aug 23, 2026 — the no-op re-size. `compute_rente_face` is
        # `expectation − ESTATE income` and deliberately ignores the rente
        # already held, so a marshal who is fully paid BY HIS RENTE still
        # reports a positive face. This guard only ever asked `face <= 0`, so
        # Ney at expectation 80 / pension 80 / estates 0 reached the success
        # path, re-wrote `pension = 80`, announced "his previous rente is
        # folded in", and spent 1 of the turn's 2 admin actions achieving
        # exactly nothing. Measured live on the user's turn-3 board.
        #
        # `rente_would_change` is the ONE predicate (GR1) — the first cut here
        # was `face <= held`, which the review round showed refuses a marshal
        # whose estate has been disrupted out from under him, and blocks a
        # legitimate re-size DOWN. The card and the AI rung read the same
        # function, so the button can no longer offer what the executor
        # refuses.
        if not rente_would_change(marshal, world):
            # UX23-A review round: the "already met" sentence was the ONLY
            # refusal here, and it is a lie in the disrupted-estate case — he
            # is emphatically not met, the treasury simply cannot help him by
            # re-writing paper downward. Name the real obstacle.
            from backend.game_logic.dotation import (
                get_estate_income, rente_grant_would_not_help,
            )
            if rente_grant_would_not_help(marshal, world) and shortfall > 0:
                occupied = [r for r in getattr(marshal, "dotation_regions", [])
                            if r in world.get_disrupted_regions()]
                if occupied:
                    from backend.display_names import humanize_entity_name
                    where = humanize_entity_name(occupied[0])
                    return {
                        "success": False,
                        "message": (
                            f"A rente cannot mend this, Sire. Marshal "
                            f"{marshal.name} is short {shortfall}g/turn only "
                            f"because an enemy army stands on {where} and his "
                            f"estate pays nothing — the treasury would be "
                            f"writing down the paper he already holds. Drive "
                            f"them off, or endow him elsewhere."),
                    }
                return {
                    "success": False,
                    "message": (
                        f"There is nothing to grant, Sire. Marshal "
                        f"{marshal.name}'s estates are entered against his "
                        f"expectation in full; what he lacks, gold cannot "
                        f"supply."),
                }
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

        previous = held      # read above, before anything mutated it
        marshal.pension = int(face)

        world.log_event({
            "type": "rente_granted",
            "marshal": marshal.name,
            "nation": acting_nation,
            "face": int(face),
            "cost": int(cost),
            "previous": int(previous),
        })

        # Aug 23, 2026: the tray must not go on asking for what was just
        # paid — same seam and same dismiss-only reasoning as grant_dotation.
        # Gated on the debt actually being SETTLED (review round, 4b09e59):
        # the first cut dismissed on any success, so endowing a 0g war-torn
        # province — or REVOKING a rente — retired a HIGH "his loyalty is
        # fraying" row that was still true, and trust went on falling 3/turn
        # with nothing on screen. Paying in part leaves the row standing; its
        # figures are refreshed in place, keeping the row's id so the desk
        # bell does not ring at the moment of payment (UX23-R2, LANDED —
        # `restate_reward_notice` is the superset of the old
        # dismiss-if-settled call: it retires on the same `shortfall <= 0`
        # gate, and otherwise re-quotes the live price the rail's own button
        # now spends an administrative action on).
        restate_reward_notice(world, marshal)

        resize_note = (f" (his previous rente of {previous}g/turn is folded in)"
                       if previous > 0 else "")
        decree = _decree_preamble(world, acting_nation)
        # CA8-21: Talleyrand's aphorism, and the address to the Emperor, are
        # France's own council speaking. A foreign court gets the same facts
        # without either.
        if acting_nation == getattr(world, "player_nation", "France"):
            gloss = (f"{cost}g/turn — paper is dearer than land, Sire, and "
                     f"it buys no title. It holds his loyalty for exactly "
                     f"as long as it is paid.")
        else:
            gloss = f"{cost}g/turn. It buys no title, and it holds only while paid."
        return {
            "success": True,
            "message": (f"{decree}, Marshal {marshal.name} is granted "
                        f"a rente of {face}g/turn upon the treasury{resize_note}. "
                        f"With fees and arrears it will cost the crown "
                        f"{gloss}"),
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
        from backend.game_logic.dotation import (
            dismiss_reward_notices, get_rente_cost, is_dotation_world,
            restate_reward_notice,
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
        # Aug 23, 2026: a revoke changes his satisfaction too, so the standing
        # rows are stale either way — whether the estates now cover him (both
        # rows are simply false) or a shortfall has just reopened (the numbers
        # are last turn's). Retire them; the next turn's pass re-posts the
        # honest row with a fresh grace clock if one is owed.
        if get_satisfaction(marshal, world) >= get_expectation(marshal):
            # Only when the estates genuinely cover him without the paper.
            # Revoking into an OPEN shortfall must not silence the warning
            # the same sentence is about to give (review round, 4b09e59).
            dismiss_reward_notices(world, marshal)
            consequence = ("His estates sustain his expectation without it — "
                           "the paper was redundant, Sire.")
        else:
            # UX23-A: the shortfall this re-opens is one the standing row is
            # already describing — re-quote it rather than leave the button
            # offering the pre-revocation price.
            restate_reward_notice(world, marshal)
            # WO slice 14 review round: WO-18 freezes the grace clock while a
            # load-bearing rente covers a marshal who was ALREADY owed, so
            # revoking then resumes erosion AT ONCE — the "after its grace
            # expires" line over-promised a fresh window it no longer gets.
            # A −1 clock (the rente met him from a clean slate) does open a
            # grace window; a frozen-open clock does not. Say which.
            if int(getattr(marshal, "expectation_grace_turn", -1)) >= 0:
                consequence = ("He will remember who stopped paying, Sire — "
                               "the debt the rente only masked frays his "
                               "loyalty at once.")
            else:
                consequence = ("He will remember who stopped paying, Sire: "
                               "unmet expectation frays loyalty after its "
                               "grace expires.")

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
        # CA9-F10: the eight preconditions live in ONE predicate
        # (`region.can_build`) so the `supply_strain` briefing can consult
        # the same gate instead of modelling two of them. Every refusal
        # string below is produced there, verbatim.
        from backend.models.region import can_build
        ok, refusal, _remedy = can_build(
            world, region, building_type, build_acting_nation)
        if not ok:
            return {"success": False, "message": refusal}

        btype_info = BUILDING_TYPES[building_type]
        gold_cost = btype_info["gold_cost"]
        build_treasury = world.nation_gold.get(build_acting_nation, 0)

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
        # WO slice 8: promoted to the class so the repair chip quotes it.
        REPAIR_COST = self.REPAIR_COST

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

        # ══════════════════════════════════════════════════════════════
        # WO slice 8 in-game pass [V-2]: the region panel's Repair chip
        # sends "repair buildings in <region>" — the U6 stem — and NO
        # keyword in `_extract_building_type` matches the bare plural, so
        # the order fell straight through to the WAR-DAMAGE arm below.
        # The chip renders when a BUILDING (or the watchtower) is
        # damaged, so the ordinary case is a province with a ruined work
        # and no war damage at all: the player pressed a chip reading
        # "restore damaged works" and was answered "No war damage to
        # repair in Paris". Slice 8 made that promise louder (it added
        # the price and "— and their upkeep"), so it is this slice's to
        # close.
        #
        # Scoped to the EXPLICIT plural: a bare "repair Lyon" keeps its
        # war-damage meaning exactly as before. First damaged work in
        # build order, then the watchtower — the same order the panel
        # lists them in.
        # ══════════════════════════════════════════════════════════════
        if not building_type:
            _raw = (command.get("raw_command") or "").lower()
            if "building" in _raw or "works" in _raw:
                _damaged = next((b["type"] for b in region.buildings
                                 if b.get("damaged", False)), None)
                if _damaged:
                    building_type = _damaged
                elif getattr(region, "watchtower", "none") == "damaged":
                    building_type = "watchtower"

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

        region.recover_war_damage(self.WAR_DAMAGE_REPAIR_FRACTION)
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
    # ══════════════════════════════════════════════════════════════════
    # PT-H4: the gate must include the executor's DECISIVE gate.
    #
    # `open` checked headroom and pool and never asked the question
    # `_execute_recruit` asks FIRST: is there a marshal who can reach the
    # depot? `find_nearest_marshal_to_region` filters on strength >= 1000
    # AND `distance > movement_range` — infantry range is 1 — so in the
    # state a Napoleonic campaign is normally in, every marshal in Germany
    # or Italy, the answer is no.
    #
    # This is CA8-11's own measured failure: the headline advertised
    # "10,000 foot cost 450 gold at Paris" and `recruit 10000 infantry at
    # Paris` answered "No marshal is available…". The base template was
    # fixed to name the condition; the PREDICATE never was, so the
    # headline still fired.
    # ══════════════════════════════════════════════════════════════════
    # `find_nearest_marshal_to_region` takes the REGION only and is
    # player-scoped, so the recipient term applies to the player's own
    # levy — which is the only levy this status renders.
    recipient = None
    if capital and nation == world.player_nation:
        recipient = world.find_nearest_marshal_to_region(capital)
    return {
        "recipient_in_range": bool(recipient),
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
                     and pool >= INFANTRY_RECRUIT_AMOUNT
                     and recipient),
    }
