"""
Vassal System — Phase 8 Session 5

Single source of truth for vassal mechanics:
  - Vassalage creation (treaty/conquest paths)
  - Loyalty processing (drift, garrison, shared enemy, battles, relations)
  - Rebellion (loyalty=0 → WAR + marshal transfer + cascade)
  - Defection cascade (war_score < -30 + loyalty < 50)
  - Tribute collection (gold per tribute_rate)
  - Investment (1 DP + 200g → +10 loyalty)
  - Autonomy changes (puppet/satellite/autonomous)
  - Marshal assimilation (vassal marshals → player pool)
  - Continental System enforcement
"""

import random
from typing import List
from backend.models.trust import Trust

# ═══════ AUTONOMY LEVELS ═══════
AUTONOMY_PUPPET = 0       # -4 drift/turn
AUTONOMY_SATELLITE = 1    # -2 drift/turn
AUTONOMY_AUTONOMOUS = 2   # +1 drift/turn

AUTONOMY_DRIFT = {0: -4, 1: -2, 2: 1}

AUTONOMY_NAMES = {0: "Puppet", 1: "Satellite", 2: "Autonomous"}

# ═══════ TRIBUTE RATES ═══════
TRIBUTE_RATES = {0: 1.0, 1: 0.75, 2: 0.5}  # % of vassal income

# ═══════ INVESTMENT COSTS ═══════
INVEST_DP_COST = 1
INVEST_GOLD_COST = 200
INVEST_LOYALTY_GAIN = 10
INVEST_COOLDOWN = 3

# ═══════ LOYALTY BOUNDS ═══════
LOYALTY_MIN = 0
LOYALTY_MAX = 100

# ═══════ MARSHAL ASSIMILATION ═══════
ASSIMILATION_TRUST = 40  # Starting trust for assimilated marshals


# ═══════════════════════════════════════════════════════
# VASSAL CREATION
# ═══════════════════════════════════════════════════════

def create_vassal_treaty(
    world, lord: str, vassal: str, generosity_bonus: int = 0,
    terms: list = None,
) -> dict:
    """
    Create a vassal via treaty path.

    Requires OPEN_BORDERS+ diplomatic state.
    Loyalty = 60 + (generosity_bonus * 10), capped at 100.
    Threat += 5.

    Returns result dict with success/message.
    """
    # Validate diplomatic state
    current_state = world.get_diplomatic_state(lord, vassal)
    from backend.game_logic.diplomacy import VASSAL_MIN_STATES
    if current_state not in VASSAL_MIN_STATES:
        return {
            "success": False,
            "message": f"Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: {current_state})."
        }

    # Check not already a vassal
    if vassal in world.vassals:
        return {
            "success": False,
            "message": f"{vassal} is already a vassal of {world.vassals[vassal]['lord']}."
        }

    # R14: Check release cooldown (blocks treaty-cycle exploit)
    cooldowns = getattr(world, 'vassal_release_cooldowns', {})
    if cooldowns.get(vassal, 0) > 0:
        return {
            "success": False,
            "message": f"Cannot vassalize {vassal}: recently released ({cooldowns[vassal]} turns remaining)."
        }

    # WPS-B: Power cap gate
    from backend.game_logic.diplomacy import check_vassalage_power_cap
    cap = check_vassalage_power_cap(world, lord, vassal, terms=terms)
    if not cap["allowed"]:
        return {
            "success": False,
            "message": f"Cannot vassalize {vassal}: {cap['reason']}.",
        }

    # Calculate loyalty
    loyalty = min(LOYALTY_MAX, 60 + (generosity_bonus * 10))

    # Create vassal state
    world.vassals[vassal] = {
        "lord": lord,
        "loyalty": int(loyalty),
        "autonomy": AUTONOMY_SATELLITE,  # Treaty defaults to SATELLITE
        "path": "treaty",
        "created_turn": int(world.current_turn),
        "tribute_rate": TRIBUTE_RATES[AUTONOMY_SATELLITE],
        "carved_from": None,
        "regions": None,
    }
    # Vassalage changes both bloc geometry and the active-nation roster
    # (vassals remain active even at 0 regions).
    world.invalidate_active_nations_cache()

    # Set diplomatic state to VASSAL (R2: centralized setter)
    from backend.game_logic.diplomacy import set_diplomatic_state
    set_diplomatic_state(world, lord, vassal, "VASSAL", "treaty_vassalization")

    # Coalition threat: +5 for treaty vassalization (§2a)
    from backend.game_logic.coalition import add_threat
    add_threat(world, 5, "treaty_vassalization")

    # R48: Reconcile diplomatic conflicts
    _reconcile_vassal_diplomacy(world, lord, vassal)

    # Dispatch event (Session 8D)
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_carved_vassal_created",
                        {"carved_name": vassal}, "always")

    return {
        "success": True,
        "message": f"{vassal} has become a {AUTONOMY_NAMES[AUTONOMY_SATELLITE]} vassal of {lord} (loyalty: {int(loyalty)}).",
        "vassal_state": world.vassals[vassal].copy(),
    }


def create_vassal_conquest(world, lord: str, vassal: str, garrison_size: int = 0) -> dict:
    """
    Create a vassal via conquest path.

    Loyalty = 20 + (garrison_size // 5000), capped at 100.
    Threat += 25.
    Autonomy defaults to PUPPET.

    Returns result dict with success/message.
    """
    if vassal in world.vassals:
        return {
            "success": False,
            "message": f"{vassal} is already a vassal of {world.vassals[vassal]['lord']}."
        }

    # Check release cooldown (blocks re-vassalization exploit)
    cooldowns = getattr(world, 'vassal_release_cooldowns', {})
    if cooldowns.get(vassal, 0) > 0:
        return {
            "success": False,
            "message": f"Cannot vassalize {vassal}: recently released ({cooldowns[vassal]} turns remaining)."
        }

    # Require WAR state for conquest vassalization
    current_state = world.get_diplomatic_state(lord, vassal)
    if current_state != "WAR":
        return {
            "success": False,
            "message": f"Cannot conquer {vassal}: must be at WAR (current: {current_state})."
        }

    # WPS-B: Power cap gate
    from backend.game_logic.diplomacy import check_vassalage_power_cap
    cap = check_vassalage_power_cap(world, lord, vassal)
    if not cap["allowed"]:
        return {
            "success": False,
            "message": (f"{vassal} submits, but {lord} cannot impose vassalage on so large "
                        f"a nation. Demand terms at the peace table instead."),
        }

    loyalty = min(LOYALTY_MAX, 20 + (garrison_size // 5000))

    world.vassals[vassal] = {
        "lord": lord,
        "loyalty": int(loyalty),
        "autonomy": AUTONOMY_PUPPET,
        "path": "conquest",
        "created_turn": int(world.current_turn),
        "tribute_rate": TRIBUTE_RATES[AUTONOMY_PUPPET],
        "carved_from": None,
        "regions": None,
    }
    # Vassalage changes both bloc geometry and the active-nation roster
    # (vassals remain active even at 0 regions).
    world.invalidate_active_nations_cache()

    # Set diplomatic state to VASSAL (R2: centralized setter)
    from backend.game_logic.diplomacy import set_diplomatic_state
    set_diplomatic_state(world, lord, vassal, "VASSAL", "conquest_vassalization")

    # Coalition threat: +25 for conquest vassalization (§2a)
    from backend.game_logic.coalition import add_threat
    add_threat(world, 25, "conquest_vassalization")

    # R48: Reconcile diplomatic conflicts
    _reconcile_vassal_diplomacy(world, lord, vassal)

    # Dispatch event (Session 8D)
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_carved_vassal_created",
                        {"carved_name": vassal}, "always")

    return {
        "success": True,
        "message": f"{vassal} has been subjugated as a {AUTONOMY_NAMES[AUTONOMY_PUPPET]} vassal of {lord} (loyalty: {int(loyalty)}).",
        "vassal_state": world.vassals[vassal].copy(),
    }


def _reconcile_vassal_diplomacy(world, lord: str, vassal: str) -> None:
    """R48: Reconcile diplomatic conflicts after vassalization.

    - If vassal is at WAR with lord's allies → auto-armistice
    - If vassal is allied with lord's enemies → auto-break to PEACE
    """
    all_nations = world.get_active_nations()  # DLF-11

    for other in all_nations:
        if other == lord or other == vassal:
            continue

        lord_state = world.get_diplomatic_state(lord, other)
        vassal_state = world.get_diplomatic_state(vassal, other)

        # Vassal at WAR with lord's ally → force ARMISTICE
        if vassal_state == "WAR" and lord_state in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
            from backend.game_logic.diplomacy import set_diplomatic_state
            set_diplomatic_state(world, vassal, other, "ARMISTICE", "vassal_reconcile")

        # Vassal allied with lord's enemy → break to PEACE
        if vassal_state in ("DEFENSIVE_ALLIANCE", "ALLIANCE") and lord_state == "WAR":
            from backend.game_logic.diplomacy import set_diplomatic_state
            set_diplomatic_state(world, vassal, other, "PEACE", "vassal_reconcile")


# ═══════════════════════════════════════════════════════
# LOYALTY PROCESSING (advance_turn Step 6)
# ═══════════════════════════════════════════════════════

def process_vassal_loyalty(world) -> List[dict]:
    """
    Process all vassal loyalty modifiers per turn.

    Modifiers:
    - Autonomy drift: PUPPET -4, SATELLITE -2, AUTONOMOUS +1
    - Garrison in vassal capital: +2 base + min(garrison_troops//5000, 3), capped at 4
    - Gold investment treaty: +1 per 100g/turn from active treaty clause
    - Shared enemy: +2 per shared war (lord and vassal both at WAR with same)
    - Lord winning battles: +1 per battle won this turn (max +3)
    - Lord losing battles: -2 per battle lost this turn (max -6)
    - Relation modifier: nation_relation(vassal, lord) // 20

    Returns list of event dicts for dispatch.
    """
    events = []

    for vassal_name, state in list(world.vassals.items()):
        lord = state["lord"]
        old_loyalty = state["loyalty"]
        delta = 0

        # 1. Autonomy drift
        autonomy = state.get("autonomy", AUTONOMY_SATELLITE)
        drift = AUTONOMY_DRIFT.get(autonomy, 0)
        delta += drift

        # 2. Garrison in vassal capital
        from backend.models.region import NATION_CAPITALS
        vassal_capital = NATION_CAPITALS.get(vassal_name)
        if vassal_capital:
            region = world.regions.get(vassal_capital)
            if region:
                garrison_troops = getattr(region, 'garrison_troops', 0) or 0
                if garrison_troops > 0 and getattr(region, 'controller', '') == lord:
                    garrison_bonus = min(8, 5 + min(garrison_troops // 5000, 3))
                    delta += garrison_bonus

        # 3. Gold investment from treaty clauses
        for pair_key, treaty in getattr(world, 'active_treaties', {}).items():
            for clause in treaty.get("clauses", []):
                if (clause.get("type") == "gold_per_turn"
                        and clause.get("from") == lord
                        and clause.get("to") == vassal_name):
                    gold_amount = clause.get("amount", 0)
                    delta += int(gold_amount) // 100

        # 4. Shared enemy bonus
        all_nations = world.get_active_nations()  # DLF-11
        for other_nation in all_nations:
            if other_nation == lord or other_nation == vassal_name:
                continue
            lord_state = world.get_diplomatic_state(lord, other_nation)
            vassal_state_diplo = world.get_diplomatic_state(vassal_name, other_nation)
            if lord_state == "WAR" and vassal_state_diplo == "WAR":
                delta += 2

        # 5. Lord winning/losing battles this turn
        battles = getattr(world, 'battles_this_turn', [])
        wins = 0
        losses = 0
        for battle in battles:
            attacker_name = battle.get("attacker", "")
            defender_name = battle.get("defender", "")
            result = battle.get("result", "")
            attacker_marshal = world.get_marshal(attacker_name)
            defender_marshal = world.get_marshal(defender_name)
            atk_nation = getattr(attacker_marshal, 'nation', '') if attacker_marshal else ''
            def_nation = getattr(defender_marshal, 'nation', '') if defender_marshal else ''
            # Lord involved?
            if atk_nation != lord and def_nation != lord:
                continue
            # Lord won?
            if "attacker" in result.lower() and "victory" in result.lower():
                winner_nation = atk_nation
            elif "defender" in result.lower() and "victory" in result.lower():
                winner_nation = def_nation
            else:
                continue
            if winner_nation == lord:
                wins += 1
            else:
                losses += 1
        delta += min(wins, 3)       # +1 per win, max +3
        delta -= min(losses, 3) * 2  # -2 per loss, max -6

        # 6. Relation modifier
        diplo_key = world._make_diplo_key(vassal_name, lord)
        relation = world.nation_relations.get(diplo_key, 0)
        delta += relation // 20

        # 7. Coalition loyalty penalty
        from backend.game_logic.coalition import get_coalition_loyalty_penalty
        coalition_penalty = get_coalition_loyalty_penalty(vassal_name, world)
        delta += coalition_penalty

        # Apply delta
        new_loyalty = max(LOYALTY_MIN, min(LOYALTY_MAX, old_loyalty + delta))
        state["loyalty"] = int(new_loyalty)

        # Generate event if significant change
        if abs(delta) >= 3 or new_loyalty <= 20:
            events.append({
                "type": "vassal_loyalty",
                "vassal": vassal_name,
                "lord": lord,
                "old_loyalty": int(old_loyalty),
                "new_loyalty": int(new_loyalty),
                "delta": int(delta),
            })

        # Dispatch events for vassal unrest (Session 8D)
        if lord == getattr(world, 'player_nation', 'France'):
            from backend.game_logic.dispatch import queue_dispatch_event
            if new_loyalty < 40 and new_loyalty > 10:
                queue_dispatch_event(world, "diplomatic_vassal_unrest",
                                    {"nation": vassal_name}, "player_vassal")

        # Notification + popup: rebellion imminent (Session 8C)
        if new_loyalty <= 10 and lord == getattr(world, 'player_nation', 'France'):
            from backend.notifications import (
                create_notification, NotificationPriority, VASSAL_REBELLION_IMMINENT,
            )
            world.notifications.add(create_notification(
                VASSAL_REBELLION_IMMINENT,
                NotificationPriority.HIGH,
                f"{vassal_name} Critical!",
                f"{vassal_name} loyalty critical ({int(new_loyalty)}) — rebellion imminent.",
                int(world.current_turn),
            ))
            # V2-90: Append to popup list instead of overwriting (multiple vassals)
            world.vassal_rebellion_imminent_popups.append({
                "nation": vassal_name,
                "loyalty": int(new_loyalty),
                "loyalty_max": int(100),
                "invest_cost_dp": int(1),
                "garrison_ap_cost": int(2),
                "invest_effect": "Loyalty +10",
                "garrison_effect": "Loyalty +10, AP -2 this turn",
                "accept_effect": "Rebellion proceeds next turn if loyalty reaches 0",
            })
            # V2-89 → R12C: push() auto-queues if another dialogue is active
            world.dialogue_manager.push({
                "type": "vassal_rebellion_imminent",
                "target_nation": vassal_name,
                "talleyrand_text": (
                    f"Sire, {vassal_name} teeters on the brink of rebellion! "
                    f"Their loyalty stands at {int(new_loyalty)} — action is required."
                ),
                "options": [
                    {
                        "label": "Invest",
                        "description": "1 DP + 200g → Loyalty +10.",
                        "action": "invest_vassal_rebellion",
                    },
                    {
                        "label": "Garrison",
                        "description": "2 AP → Loyalty +10.",
                        "action": "garrison_vassal_rebellion",
                    },
                    {
                        "label": "Accept Risk",
                        "description": "Let events unfold. Rebellion if loyalty reaches 0.",
                        "action": "accept_vassal_rebellion",
                    },
                ],
                "context": {"vassal_name": vassal_name, "loyalty": int(new_loyalty)},
                "turn_created": int(world.current_turn),
                "blocking": True,
            })
            # Dispatch event (Session 8D)
            from backend.game_logic.dispatch import queue_dispatch_event as _qde_vassal
            _qde_vassal(world, "diplomatic_vassal_rebellion_imminent",
                        {"nation": vassal_name}, "player_vassal")

    # Notification: defection cascade — multiple vassals low (Session 8C)
    low_vassals = [
        v for v, s in world.vassals.items()
        if s.get("loyalty", 100) < 25
        and s.get("lord") == getattr(world, 'player_nation', 'France')
    ]
    if len(low_vassals) >= 2:
        from backend.notifications import (
            create_notification, NotificationPriority, DEFECTION_CASCADE,
        )
        world.notifications.add(create_notification(
            DEFECTION_CASCADE,
            NotificationPriority.HIGH,
            "Empire Trembles",
            "Multiple vassals are wavering — the empire trembles.",
            int(world.current_turn),
        ))
        # Dispatch event (Session 8D)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_defection_cascade", {}, "always")

    return events


# ═══════════════════════════════════════════════════════
# REBELLION CHECK (advance_turn Step 7)
# ═══════════════════════════════════════════════════════

def check_vassal_rebellion(world) -> List[dict]:
    """
    Check for vassal rebellions. Loyalty=0 triggers rebellion.

    Effects:
    - Set diplomatic state to WAR
    - Transfer vassal marshals back to vassal nation
    - Cascade: all other vassals -10 loyalty
    - Threat -10, relation -50

    Returns list of event dicts.
    """
    events = []
    rebellions = []

    for vassal_name, state in list(world.vassals.items()):
        if state["loyalty"] <= 0:
            rebellions.append(vassal_name)

    for vassal_name in rebellions:
        lord = world.vassals[vassal_name]["lord"]

        # Dispatch event: vassal dissolved (Session 8D)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_carved_vassal_dissolved",
                            {"carved_name": vassal_name}, "always")

        # Remove vassal state
        del world.vassals[vassal_name]
        world.invalidate_active_nations_cache()

        # Set diplomatic state to WAR (FINAL-2: respect armistice — skip if in ceasefire)
        diplo_key = world._make_diplo_key(lord, vassal_name)
        current_state = world.diplomatic_states.get(diplo_key, "PEACE")
        if current_state == "ARMISTICE":
            # Vassal becomes independent but armistice is respected — no war declaration
            events.append({
                "type": "vassal_rebellion_armistice",
                "vassal": vassal_name,
                "lord": lord,
                "message": f"{vassal_name} breaks free but the armistice holds — no war declared."
            })
        else:
            from backend.game_logic.diplomacy import (
                _process_war_cascade,
                set_diplomatic_state,
            )
            from backend.game_logic.settlement_helpers import (
                CascadeContext,
                ensure_war_instance_for_pair,
            )

            # Slice A2 §7.2 "Direct WAR-entry rule": the vassal-rebellion
            # seam must allocate / reuse a war_instance BEFORE mutating
            # diplomatic_states, then thread the allocated war_id through
            # the cascade so allied joins attach to the same political
            # conflict as the rebellion.
            war_instance_result = ensure_war_instance_for_pair(
                world,
                vassal_name,
                lord,
                entry_path="vassal_rebellion",
                reason="check_vassal_rebellion",
            )
            if war_instance_result.get("ok"):
                set_diplomatic_state(world, vassal_name, lord, "WAR", "vassal_rebellion")

                cascade_ctx = CascadeContext(
                    war_id=war_instance_result["war_id"],
                    root_aggressor=vassal_name,
                    war_entry_entries=[],
                )
                cascade_events = _process_war_cascade(
                    world,
                    vassal_name,
                    lord,
                    ctx=cascade_ctx,
                )
                events.extend(cascade_events)
            else:
                # Hard-stop diagnostics — surface as an event so playtest
                # logs catch a misbehaving rebellion seam. A3 will resolve
                # `war_instance_merge_required` with the merge transaction.
                events.append({
                    "type": "vassal_rebellion_blocked",
                    "vassal": vassal_name,
                    "lord": lord,
                    "error": war_instance_result.get("error"),
                    "details": war_instance_result.get("details", {}),
                    "message": (
                        f"{vassal_name} cannot rebel against {lord}: "
                        f"{war_instance_result.get('error')}"
                    ),
                })
                continue

        # Transfer vassal marshals back and clean up stale state
        for marshal in list(world.marshals.values()):
            if (getattr(marshal, 'original_nation', None) == vassal_name
                    and getattr(marshal, 'nation', '') == lord):
                marshal.nation = vassal_name
                marshal.original_nation = None  # Clear stale pre-vassalage marker
                marshal.trust = Trust()  # Reset trust for transferred marshal
                if hasattr(marshal, 'relationship_with_lord'):
                    delattr(marshal, 'relationship_with_lord')

        # Cascade: all other vassals -10 loyalty
        for other_vassal, other_state in world.vassals.items():
            if other_state["lord"] == lord:
                other_state["loyalty"] = max(LOYALTY_MIN, other_state["loyalty"] - 10)

        # Coalition threat reduction from rebellion
        from backend.game_logic.coalition import reduce_threat
        reduce_threat(world, 10, "vassal_rebellion")

        # Relation -50
        world.modify_nation_relation(lord, vassal_name, -50)

        # Notification: vassal rebellion (Session 8C)
        from backend.notifications import (
            create_notification as _cr_notif, NotificationPriority as _NP,
        )
        from backend.notifications import VASSAL_REBELLION as _VR_CONST
        world.notifications.add(_cr_notif(
            _VR_CONST,
            _NP.CRITICAL,
            f"{vassal_name} REBELLED!",
            f"{vassal_name} has rebelled against {lord}! War declared.",
            int(world.current_turn),
        ))

        events.append({
            "type": "vassal_rebellion",
            "vassal": vassal_name,
            "lord": lord,
            "message": f"{vassal_name} has REBELLED! All vassal marshals have returned to {vassal_name}. War declared.",
        })
        # Dispatch event (Session 8D)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_vassal_rebellion",
                            {"nation": vassal_name}, "player_vassal")

    return events


# ═══════════════════════════════════════════════════════
# DEFECTION CASCADE (advance_turn Step 5)
# ═══════════════════════════════════════════════════════

def check_defection_cascade(world) -> List[dict]:
    """
    Check for defection cascade: war_score < -30 + loyalty < 50.

    Random roll: random() < (50 - loyalty) / 100
    Fires AT MOST once per war (tracked in world.cascade_triggered).

    Returns list of event dicts.
    """
    events = []
    lord = getattr(world, 'player_nation', 'France')
    cascade_triggered = getattr(world, 'cascade_triggered', set())

    for vassal_name, state in list(world.vassals.items()):
        if state["lord"] != lord:
            continue

        loyalty = state["loyalty"]
        if loyalty >= 50:
            continue

        # Check if lord is in a war with war_score < -30
        all_nations = world.get_active_nations()  # DLF-11
        for enemy_nation in all_nations:
            if enemy_nation == lord or enemy_nation == vassal_name:
                continue

            war_state = world.get_diplomatic_state(lord, enemy_nation)
            if war_state != "WAR":
                continue

            from backend.game_logic.diplomacy import get_war_score_for
            war_score = get_war_score_for(world, lord, enemy_nation)

            if war_score >= -30:
                continue

            # Check if cascade already triggered for this war
            diplo_key = world._make_diplo_key(lord, enemy_nation)
            cascade_key = f"{vassal_name}|{diplo_key}"
            if cascade_key in cascade_triggered:
                continue

            # Roll for defection
            roll_chance = (50 - loyalty) / 100
            if random.random() < roll_chance:
                cascade_triggered.add(cascade_key)

                # Vassal defects — immediate rebellion (set to 0, triggers rebellion check)
                state["loyalty"] = LOYALTY_MIN

                events.append({
                    "type": "vassal_defection_cascade",
                    "vassal": vassal_name,
                    "lord": lord,
                    "war_against": enemy_nation,
                    "loyalty_before": int(loyalty),
                    "loyalty_after": int(state["loyalty"]),
                    "message": f"{vassal_name} is wavering! The war against {enemy_nation} shakes their loyalty.",
                })

    world.cascade_triggered = cascade_triggered
    # Dispatch: defection cascade summary if any events fired (Session 8D)
    if events:
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_defection_cascade", {}, "always")
    return events


# ═══════════════════════════════════════════════════════
# TRIBUTE PROCESSING
# ═══════════════════════════════════════════════════════

def process_vassal_tribute(world) -> dict:
    """
    Process vassal tribute payments during income phase.

    Each vassal pays tribute_rate * their regional income to their lord.
    """
    tribute_events = {}

    for vassal_name, state in world.vassals.items():
        lord = state["lord"]
        tribute_rate = state.get("tribute_rate", 0.5)

        # Calculate vassal's base income (respects stability and war damage)
        vassal_income = 0
        for region_name, region in world.regions.items():
            if getattr(region, 'controller', '') == vassal_name:
                vassal_income += region.get_effective_income()

        tribute_amount = int(vassal_income * tribute_rate)
        if tribute_amount <= 0:
            continue

        # Transfer gold
        vassal_gold = world.nation_gold.get(vassal_name, 0)
        actual_tribute = min(tribute_amount, max(0, vassal_gold))
        if actual_tribute > 0:
            world.nation_gold[vassal_name] = int(vassal_gold - actual_tribute)
            lord_gold = world.nation_gold.get(lord, 0)
            world.nation_gold[lord] = int(lord_gold + actual_tribute)

            tribute_events[vassal_name] = {
                "amount": int(actual_tribute),
                "lord": lord,
            }

    return tribute_events


# ═══════════════════════════════════════════════════════
# INVESTMENT
# ═══════════════════════════════════════════════════════

def invest_in_vassal(world, vassal_name: str) -> dict:
    """
    Invest in vassal: 1 DP + 200g → +10 loyalty.

    Requires:
    - Vassal exists
    - Player has DP available
    - Player has 200+ gold
    - Not on cooldown (3 turns)

    Returns result dict.
    """
    if vassal_name not in world.vassals:
        return {"success": False, "message": f"{vassal_name} is not a vassal."}

    state = world.vassals[vassal_name]
    lord = state["lord"]

    # Validate caller is the lord
    player = getattr(world, 'player_nation', 'France')
    if lord != player:
        return {"success": False, "message": f"Cannot invest in {vassal_name}: not your vassal."}

    # Check cooldown
    cooldowns = getattr(world, 'vassal_investment_cooldowns', {})
    if cooldowns.get(vassal_name, 0) > 0:
        remaining = cooldowns[vassal_name]
        return {
            "success": False,
            "message": f"Investment in {vassal_name} on cooldown ({remaining} turns remaining)."
        }

    # Check DP
    dp = getattr(world, 'diplomatic_points', 0)
    if dp < INVEST_DP_COST:
        return {
            "success": False,
            "message": f"Insufficient diplomatic points ({dp}/{INVEST_DP_COST} required)."
        }

    # Check gold
    gold = world.nation_gold.get(lord, 0)
    if gold < INVEST_GOLD_COST:
        return {
            "success": False,
            "message": f"Insufficient gold ({gold}/{INVEST_GOLD_COST} required)."
        }

    # Apply investment
    world.diplomatic_points = int(dp - INVEST_DP_COST)
    world.nation_gold[lord] = int(gold - INVEST_GOLD_COST)
    old_loyalty = state["loyalty"]
    state["loyalty"] = int(min(LOYALTY_MAX, old_loyalty + INVEST_LOYALTY_GAIN))
    cooldowns[vassal_name] = INVEST_COOLDOWN
    world.vassal_investment_cooldowns = cooldowns

    return {
        "success": True,
        "message": (
            f"Invested in {vassal_name}: +{INVEST_LOYALTY_GAIN} loyalty "
            f"({old_loyalty} → {state['loyalty']}). "
            f"Cost: {INVEST_DP_COST} DP + {INVEST_GOLD_COST}g. "
            f"Cooldown: {INVEST_COOLDOWN} turns."
        ),
    }


# ═══════════════════════════════════════════════════════
# AUTONOMY CHANGES
# ═══════════════════════════════════════════════════════

def change_vassal_autonomy(world, vassal_name: str, new_level: int) -> dict:
    """
    Change vassal autonomy level. Costs 1 DP.

    Upgrading (more autonomy): +10 loyalty
    Downgrading (less autonomy): -15 loyalty

    Returns result dict.
    """
    if vassal_name not in world.vassals:
        return {"success": False, "message": f"{vassal_name} is not a vassal."}

    if new_level not in AUTONOMY_NAMES:
        return {"success": False, "message": f"Invalid autonomy level: {new_level}. Use 0 (Puppet), 1 (Satellite), or 2 (Autonomous)."}

    state = world.vassals[vassal_name]
    old_level = state.get("autonomy", AUTONOMY_SATELLITE)

    if old_level == new_level:
        return {"success": False, "message": f"{vassal_name} is already {AUTONOMY_NAMES[new_level]}."}

    # Check DP
    dp = getattr(world, 'diplomatic_points', 0)
    if dp < 1:
        return {"success": False, "message": f"Insufficient diplomatic points ({dp}/1 required)."}

    # Apply change
    world.diplomatic_points = int(dp - 1)
    state["autonomy"] = int(new_level)
    state["tribute_rate"] = TRIBUTE_RATES[new_level]

    # Loyalty adjustment
    if new_level > old_level:
        # More autonomy = vassal is happier
        state["loyalty"] = int(min(LOYALTY_MAX, state["loyalty"] + 10))
        loyalty_msg = "+10 loyalty (increased autonomy)"
    else:
        # Less autonomy = vassal is unhappy
        state["loyalty"] = int(max(LOYALTY_MIN, state["loyalty"] - 15))
        loyalty_msg = "-15 loyalty (decreased autonomy)"

    return {
        "success": True,
        "message": (
            f"{vassal_name} autonomy changed: "
            f"{AUTONOMY_NAMES[old_level]} → {AUTONOMY_NAMES[new_level]}. "
            f"{loyalty_msg}. Tribute rate: {TRIBUTE_RATES[new_level]*100:.0f}%."
        ),
    }


# ═══════════════════════════════════════════════════════
# MARSHAL ASSIMILATION (EC-K.1)
# ═══════════════════════════════════════════════════════

def assimilate_vassal_marshals(world, vassal_name: str) -> List[str]:
    """
    Add vassal nation's marshals to the lord's control.

    PUPPET/SATELLITE: marshals become lord-controlled with trust=40.
    AUTONOMOUS: marshals stay AI-controlled (no assimilation).

    Sets marshal.original_nation for rebellion transfer-back.

    Returns list of assimilated marshal names.
    """
    if vassal_name not in world.vassals:
        return []

    state = world.vassals[vassal_name]
    lord = state["lord"]
    autonomy = state.get("autonomy", AUTONOMY_SATELLITE)

    # AUTONOMOUS vassals keep their own marshals
    if autonomy == AUTONOMY_AUTONOMOUS:
        return []

    assimilated = []
    for marshal in list(world.marshals.values()):
        if getattr(marshal, 'nation', '') == vassal_name:
            # Record original nation for rebellion transfer-back
            marshal.original_nation = vassal_name
            # Transfer to lord
            marshal.nation = lord
            # Set trust to assimilation level
            if hasattr(marshal, 'trust') and hasattr(marshal.trust, 'value'):
                marshal.trust.modify(ASSIMILATION_TRUST - marshal.trust.value)
            # Set Professional relationship baseline
            marshal.relationship_with_lord = "Professional"
            assimilated.append(marshal.name)

    return assimilated


# ═══════════════════════════════════════════════════════
# VASSAL WARNINGS
# ═══════════════════════════════════════════════════════

def get_vassal_warnings(world) -> List[dict]:
    """
    Get vassal loyalty warnings.

    <40: warning
    <20: urgent
    <10: critical notification
    """
    warnings = []
    for vassal_name, state in world.vassals.items():
        loyalty = state["loyalty"]
        if loyalty < 10:
            warnings.append({
                "vassal": vassal_name,
                "loyalty": int(loyalty),
                "level": "critical",
                "message": f"{vassal_name} CRITICAL: Loyalty at {int(loyalty)}! Rebellion imminent!",
            })
        elif loyalty < 20:
            warnings.append({
                "vassal": vassal_name,
                "loyalty": int(loyalty),
                "level": "urgent",
                "message": f"{vassal_name}: Loyalty dangerously low ({int(loyalty)}). Invest or face rebellion.",
            })
        elif loyalty < 40:
            warnings.append({
                "vassal": vassal_name,
                "loyalty": int(loyalty),
                "level": "warning",
                "message": f"{vassal_name}: Loyalty declining ({int(loyalty)}). Consider intervention.",
            })

    return warnings


# ═══════════════════════════════════════════════════════
# RELEASE VASSAL
# ═══════════════════════════════════════════════════════

def release_vassal(
    world,
    vassal_name: str,
    rebellion: bool = False,
    reduce_threat_on_release: bool = True,
) -> dict:
    """
    Release a vassal. Restores their marshals.

    If rebellion=True, this is a forced release from rebellion check.
    Otherwise it's a voluntary release.
    """
    if vassal_name not in world.vassals:
        return {"success": False, "message": f"{vassal_name} is not a vassal."}

    state = world.vassals[vassal_name]
    lord = state["lord"]

    # Restore marshals to vassal nation
    for marshal in list(world.marshals.values()):
        if getattr(marshal, 'original_nation', None) == vassal_name:
            marshal.nation = vassal_name
            if hasattr(marshal, 'original_nation'):
                delattr(marshal, 'original_nation')
            if hasattr(marshal, 'relationship_with_lord'):
                delattr(marshal, 'relationship_with_lord')

    # Remove vassal state
    del world.vassals[vassal_name]
    world.invalidate_active_nations_cache()

    # Clear stale popup/dialogue referencing this vassal
    if getattr(world, 'vassal_rebellion_imminent_popup', None):
        popup_vassal = world.vassal_rebellion_imminent_popup.get("nation", "")
        if popup_vassal == vassal_name:
            world.vassal_rebellion_imminent_popup = None
    # V2-90: Also clear from popups list
    if hasattr(world, 'vassal_rebellion_imminent_popups'):
        world.vassal_rebellion_imminent_popups = [
            p for p in world.vassal_rebellion_imminent_popups
            if p.get("nation") != vassal_name
        ]
    # R12C: Clear vassal rebellion dialogues for this vassal from current + queue
    world.dialogue_manager.remove_matching(
        lambda d: (d.get("type") == "vassal_rebellion_imminent"
                   and d.get("context", {}).get("vassal_name") == vassal_name)
    )

    # R14: Set release cooldown (blocks treaty re-vassalization for 5 turns)
    if not hasattr(world, 'vassal_release_cooldowns'):
        world.vassal_release_cooldowns = {}
    world.vassal_release_cooldowns[vassal_name] = 5

    # R50: Remove from Continental System on release
    cs_members = getattr(world, 'continental_system_members', [])
    if isinstance(cs_members, set):
        cs_members.discard(vassal_name)
    elif isinstance(cs_members, list) and vassal_name in cs_members:
        cs_members.remove(vassal_name)

    # Set diplomatic state to PEACE (or WAR if rebellion) — R2: centralized setter
    from backend.game_logic.diplomacy import set_diplomatic_state
    if rebellion:
        # Slice A2 §7.2 "Direct WAR-entry rule": vassal-release rebellion
        # must allocate / reuse a war_instance before the WAR transition.
        from backend.game_logic.settlement_helpers import (
            ensure_war_instance_for_pair,
        )
        war_instance_result = ensure_war_instance_for_pair(
            world,
            lord,
            vassal_name,
            entry_path="vassal_release_rebellion",
            reason="release_vassal rebellion",
        )
        if not war_instance_result.get("ok"):
            return {
                "success": False,
                "message": (
                    f"Vassal release rebellion blocked: "
                    f"{war_instance_result.get('error')} "
                    f"({war_instance_result.get('details', {}).get('reason', '')})"
                ),
                "error": war_instance_result.get("error"),
                "error_details": war_instance_result.get("details", {}),
            }
        set_diplomatic_state(world, lord, vassal_name, "WAR", "vassal_release_rebellion")
    else:
        set_diplomatic_state(world, lord, vassal_name, "PEACE", "vassal_release")
        # Coalition threat reduction: voluntary vassal release (COALITION_SPEC §2b)
        if reduce_threat_on_release and lord == getattr(world, 'player_nation', 'France'):
            from backend.game_logic.coalition import reduce_threat
            reduce_threat(world, 8, "voluntary_vassal_release")

    return {
        "success": True,
        "message": f"{vassal_name} has been released from vassalage.",
    }


# ═══════════════════════════════════════════════════════
# COOLDOWN MANAGEMENT
# ═══════════════════════════════════════════════════════

def decrement_vassal_cooldowns(world) -> None:
    """Decrement vassal investment and release cooldowns by 1. Remove expired."""
    cooldowns = getattr(world, 'vassal_investment_cooldowns', {})
    expired = []
    for vassal_name in cooldowns:
        cooldowns[vassal_name] -= 1
        if cooldowns[vassal_name] <= 0:
            expired.append(vassal_name)
    for vassal_name in expired:
        del cooldowns[vassal_name]
    world.vassal_investment_cooldowns = cooldowns

    # R14: Release cooldowns
    release_cds = getattr(world, 'vassal_release_cooldowns', {})
    for n in list(release_cds):
        release_cds[n] -= 1
    expired_r = [n for n in release_cds if release_cds[n] <= 0]
    for n in expired_r:
        del release_cds[n]
    world.vassal_release_cooldowns = release_cds


# ═══════════════════════════════════════════════════════
# ENEMY VASSAL COURTING
# ═══════════════════════════════════════════════════════

def attempt_vassal_courting(world, nation: str) -> List[dict]:
    """
    Enemy AI attempts to court player's vassals.

    Conditions:
    - Nation has 2+ DP
    - Player has vassals with loyalty < 50
    Cost: 2 DP
    Success: loyalty -15 (positive relation) or -5 (negative relation)
    Anti-spam: 3-turn cooldown per nation per vassal

    Returns list of event dicts.
    """
    events = []
    player = getattr(world, 'player_nation', 'France')

    dp = getattr(world, 'nation_dp', {}).get(nation, 0)
    if dp < 2:
        return events

    for vassal_name, state in world.vassals.items():
        if state["lord"] != player:
            continue
        if state["loyalty"] >= 50:
            continue

        # Anti-spam cooldown
        cooldown_key = f"court|{nation}|{vassal_name}"
        cooldown = getattr(world, 'ai_proposal_cooldowns', {}).get(cooldown_key, 0)
        if cooldown > 0:
            continue

        # Cost 2 DP
        dp_nations = getattr(world, 'nation_dp', {})
        if dp_nations.get(nation, 0) < 2:
            continue

        dp_nations[nation] = dp_nations.get(nation, 0) - 2

        # Calculate loyalty reduction
        diplo_key = world._make_diplo_key(vassal_name, nation)
        relation = world.nation_relations.get(diplo_key, 0)
        if relation > 0:
            loyalty_reduction = 15
        else:
            loyalty_reduction = 5

        state["loyalty"] = max(LOYALTY_MIN, state["loyalty"] - loyalty_reduction)

        # Set cooldown
        cooldowns_dict = getattr(world, 'ai_proposal_cooldowns', {})
        cooldowns_dict[cooldown_key] = 3
        world.ai_proposal_cooldowns = cooldowns_dict

        # Notification: courting detected (Session 8C)
        from backend.notifications import (
            create_notification, NotificationPriority, VASSAL_COURTING_DETECTED,
        )
        world.notifications.add(create_notification(
            VASSAL_COURTING_DETECTED,
            NotificationPriority.NORMAL,
            f"{nation} Courts {vassal_name}",
            f"Enemy agents from {nation} detected courting {vassal_name}.",
            int(world.current_turn),
        ))

        events.append({
            "type": "vassal_courting",
            "nation": nation,
            "vassal": vassal_name,
            "loyalty_reduction": int(loyalty_reduction),
            "new_loyalty": int(state["loyalty"]),
            "message": f"{nation} is courting {vassal_name}! Loyalty dropped by {loyalty_reduction}.",
        })

        # Dispatch event — 60% detection at queue time (Session 8D)
        import random as _rng
        if _rng.random() < 0.60:
            from backend.game_logic.dispatch import queue_dispatch_event
            from backend.models.region import NATION_CAPITALS
            vassal_capital = NATION_CAPITALS.get(vassal_name, vassal_name)
            queue_dispatch_event(world, "diplomatic_vassal_courting",
                                {"enemy": nation, "vassal_capital": vassal_capital},
                                "detection_60pct")

        # Only court one vassal per nation per turn
        break

    return events
