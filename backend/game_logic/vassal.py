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
# VS-R (docs/VASSAL_DEEPENING_SPEC.md §2): imperial-grip -> vassal-loyalty
# coupling. authority.py is the leaf "one grip = one module" home, so this is a
# clean downward import (no circular risk).
from backend.models.authority import (
    AUTHORITY_ACCELERATE_BELOW,
    authority_vassal_drift,
    courting_effectiveness_scale,
    courting_unlock_bonus,
    get_authority_lever_multiplier,
    get_imperial_grip,
)

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
                        {"carved_name": vassal, "protector": lord}, "always")

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
                        {"carved_name": vassal, "protector": lord}, "always")

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

def recovery_hint_for_grip(grip: int) -> str:
    """VS-1/VS-R one-line reminder of the levers that actually ARREST a
    satellite's drift, grip-aware. Single source for every recovery surface
    (the per-event dispatch line AND Talleyrand's <35 advisory).

    Names ONLY working levers (playtest F1/F1c): the old copy recommended a
    dead "garrison their capital" lever, the autonomy lever that VS-R itself
    blunts in the spiral band, and a nonexistent "large subsidy" action.
      grip >= 30 (healthy): invest and autonomy-up both pay full loyalty.
      grip <  30 (spiral):  coin (invest) and concessions (autonomy-up) are
        blunted to 40%; only winning a decisive battle (which restores grip)
        or releasing the vassal actually holds.
    """
    if grip < AUTHORITY_ACCELERATE_BELOW:
        return ("The Emperor's grip is slipping - coin and concessions no "
                "longer hold them. Win a decisive battle to restore your grip, "
                "or release them before they break away.")
    return "Invest in them or grant them autonomy to steady them."


def process_vassal_loyalty(world) -> List[dict]:
    """
    Process all vassal loyalty modifiers per turn.

    Modifiers:
    - Autonomy drift: PUPPET -4, SATELLITE -2, AUTONOMOUS +1
    - Garrison in vassal capital: +5 base + min(garrison_troops//5000, 3), cap 8
      (NOTE: unwired in production — reads `garrison_troops`, a field nothing
      assigns; kept + tested as the intended formula. Wire-or-remove is a
      DESIGN_REFINEMENT decision; VS-1's hint no longer advertises it — F1c.)
    - Gold investment treaty: +1 per 100g/turn from active treaty clause
    - Shared enemy: +2 per shared war (lord and vassal both at WAR with same)
    - Lord winning battles: +1 per battle won this turn (max +3)
    - Lord losing battles: -2 per battle lost this turn (max -6)
    - Relation modifier: nation_relation(vassal, lord) // 20
    - (VS-R) Emperor's faltering grip: -2 when the lord's imperial grip < 30

    Returns list of event dicts for dispatch.
    """
    events = []
    # VS-R: imperial grip is per-LORD; memoize so multiple satellites of the
    # same lord don't recompute it (GR8 — no repeated per-region scans).
    grip_by_lord: dict = {}

    for vassal_name, state in list(world.vassals.items()):
        lord = state["lord"]
        old_loyalty = state["loyalty"]
        delta = 0
        # W6-3 §5.4 (R132's 80/20): track each modifier's contribution so
        # the event can NAME its dominant causes ("puppet resentment, the
        # lord's defeats") instead of a bare delta.
        contributions: dict = {}

        def _contribute(label: str, value: int):
            nonlocal delta
            if value:
                delta += value
                contributions[label] = contributions.get(label, 0) + value

        # 1. Autonomy drift
        autonomy = state.get("autonomy", AUTONOMY_SATELLITE)
        drift = AUTONOMY_DRIFT.get(autonomy, 0)
        drift_label = ("puppet resentment" if autonomy == AUTONOMY_PUPPET
                       else "satellite drift" if autonomy == AUTONOMY_SATELLITE
                       else "autonomous confidence")
        _contribute(drift_label, drift)

        # 2. Garrison in vassal capital. NOTE (playtest F1c): this reads
        # `region.garrison_troops`, a field NOTHING in production assigns
        # (Region has garrison_strength / garrison_detachment), and gates on
        # `controller == lord` (false for a satellite that owns its own
        # capital) — so it contributes 0 in real play. Kept + unit-tested as
        # the intended formula; VS-1's recovery hint no longer advertises it.
        # Wire-or-remove is a DESIGN_REFINEMENT decision (needs a real way for
        # the lord to garrison a foreign-controlled vassal capital).
        vassal_capital = world.get_nation_capital(vassal_name)
        if vassal_capital:
            region = world.regions.get(vassal_capital)
            if region:
                garrison_troops = getattr(region, 'garrison_troops', 0) or 0
                if garrison_troops > 0 and getattr(region, 'controller', '') == lord:
                    garrison_bonus = min(8, 5 + min(garrison_troops // 5000, 3))
                    _contribute("the garrison's presence", garrison_bonus)

        # 3. Gold investment from treaty clauses
        for pair_key, treaty in getattr(world, 'active_treaties', {}).items():
            for clause in treaty.get("clauses", []):
                if (clause.get("type") == "gold_per_turn"
                        and clause.get("from") == lord
                        and clause.get("to") == vassal_name):
                    gold_amount = clause.get("amount", 0)
                    _contribute("subsidies", int(gold_amount) // 100)

        # 4. Shared enemy bonus
        all_nations = world.get_active_nations()  # DLF-11
        shared_wars = 0
        for other_nation in all_nations:
            if other_nation == lord or other_nation == vassal_name:
                continue
            lord_state = world.get_diplomatic_state(lord, other_nation)
            vassal_state_diplo = world.get_diplomatic_state(vassal_name, other_nation)
            if lord_state == "WAR" and vassal_state_diplo == "WAR":
                shared_wars += 1
        _contribute("a common enemy", shared_wars * 2)

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
        _contribute("the lord's victories", min(wins, 3))       # +1 per win, max +3
        _contribute("the lord's defeats", -min(losses, 3) * 2)  # -2 per loss, max -6

        # 6. Relation modifier
        diplo_key = world._make_diplo_key(vassal_name, lord)
        relation = world.nation_relations.get(diplo_key, 0)
        _contribute("relations with the lord", relation // 20)

        # 7. (VS-R) The Emperor's imperial grip. When the lord's grip spirals
        # (< 30), the whole satellite web loosens and only major concessions —
        # or winning battles — arrest it. Boot-dormant: grip >= 30 contributes
        # 0 (byte-identical — _contribute skips zero). Keys off the LORD's grip,
        # not the vassal's loyalty, so it fires symmetrically for enemy lords
        # (GR5). Read-only on authority (one-way coupling; memo Q4).
        if lord not in grip_by_lord:
            grip_by_lord[lord] = get_imperial_grip(world, lord)
        lord_grip = grip_by_lord[lord]
        _contribute("the Emperor's faltering grip", authority_vassal_drift(lord_grip))

        # (VS-2, Combat Overhaul Phase 5) The old "war weariness" offset read
        # get_coalition_loyalty_penalty(vassal_name) — but a lord's own satellite
        # is never a member of a coalition AGAINST that lord, so the term was
        # always 0 (dead code). Deleted: coalition membership is a
        # diplomatic-acceptance concept, not a loyalty-drift one.

        # Apply delta
        new_loyalty = max(LOYALTY_MIN, min(LOYALTY_MAX, old_loyalty + delta))
        state["loyalty"] = int(new_loyalty)

        # Generate event if significant change.
        # VS-1 (Combat Overhaul Phase 5): the gate was abs(delta) >= 3, which
        # HID the steady satellite bleed (-2/turn) until it crossed 20 — the
        # player never saw a healthy-band vassal slipping, nor learned the
        # levers to arrest it. Lowered to >= 2 so a bare satellite's drift
        # surfaces every turn, and a recovery hint teaches the fix.
        if abs(delta) >= 2 or new_loyalty <= 20:
            # W6-3 §5.4: name the top same-sign contributors (max 2) so the
            # dispatch/log line reads "Switzerland 84 (−8): puppet
            # resentment, the lord's defeats".
            sign = 1 if delta >= 0 else -1
            dominant = sorted(
                ((label, value) for label, value in contributions.items()
                 if value * sign > 0),
                key=lambda kv: abs(kv[1]), reverse=True,
            )[:2]
            reason = ", ".join(label for label, _ in dominant)
            delta_str = f"+{delta}" if delta >= 0 else str(delta)

            # VS-1 "teach it": a vassal slipping while still in the healthy
            # band (>= 40) gets a one-line reminder of the arresting levers, so
            # the recovery loop is discoverable BEFORE the crisis popup at <=
            # 10. Grip-aware via the single-source helper (playtest F1: the old
            # copy named a blunted lever + a nonexistent "subsidy" + the dead
            # "garrison their capital"). Land grants join once VS-3 lands.
            recovery_hint = ""
            if delta < 0 and new_loyalty >= 40:
                recovery_hint = recovery_hint_for_grip(lord_grip)

            events.append({
                "type": "vassal_loyalty",
                "vassal": vassal_name,
                "lord": lord,
                # `nation` keys the dispatch relevance filter: the LORD's
                # dispatch is the one that cares about this vassal's drift.
                "nation": lord,
                "old_loyalty": int(old_loyalty),
                "new_loyalty": int(new_loyalty),
                "delta": int(delta),
                "reason": reason,
                "recovery_hint": recovery_hint,
                "message": (
                    f"{vassal_name} loyalty {int(new_loyalty)} ({delta_str})"
                    + (f": {reason}" if reason else "")
                    + (f" — {recovery_hint}" if recovery_hint else "")
                ),
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
                # F8b (playtest): the vassal was already removed from
                # world.vassals (above), so simply `continue`-ing here left the
                # France|vassal diplomatic_state stuck at VASSAL — a permanent
                # orphan (unattackable, never at war, never loyalty-processed).
                # Reproduced live: a co-belligerent satellite (KoI, sharing
                # France's war vs Austria) hit a war-instance side-conflict and
                # orphaned while still holding all its territory. Resolve it as
                # GRACEFUL INDEPENDENCE — the satellite breaks free as a neutral
                # rather than declaring war (the "switch sides / join the
                # coalition" outcome is the deferred GR9 slice). Clearing the
                # VASSAL relation to PEACE removes the desync AND sidesteps the
                # war-instance conflict entirely (no new war pair needed).
                set_diplomatic_state(
                    world, vassal_name, lord, "PEACE",
                    "vassal_rebellion_independent",
                )
                events.append({
                    "type": "vassal_rebellion_independent",
                    "vassal": vassal_name,
                    "lord": lord,
                    "detail": war_instance_result.get("error"),
                    "message": (
                        f"{vassal_name} breaks free of {lord} and stands alone "
                        f"- an independent power, though no war is declared."
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

        # Calculate vassal's base income (respects stability and war damage).
        # Golden Rule 8: per-vassal per-turn — use the cached region index
        # instead of a raw O(R) controller scan (Slice 8 audit).
        vassal_income = 0
        for region_name in world.get_nation_regions(vassal_name):
            vassal_income += world.regions[region_name].get_effective_income()

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

    # Apply investment. VS-R "no cheap recovery": in the spiral band (lord grip
    # < 30) the +10 loyalty is BLUNTED — you still pay full cost, which is the
    # point (a token gesture no longer holds a wavering satellite). At healthy
    # grip the multiplier is exactly 1.0, so the gain and message are byte-
    # identical to pre-VS-R.
    mult = get_authority_lever_multiplier(world, lord)
    gain = int(INVEST_LOYALTY_GAIN * mult)
    world.diplomatic_points = int(dp - INVEST_DP_COST)
    world.nation_gold[lord] = int(gold - INVEST_GOLD_COST)
    old_loyalty = state["loyalty"]
    state["loyalty"] = int(min(LOYALTY_MAX, old_loyalty + gain))
    cooldowns[vassal_name] = INVEST_COOLDOWN
    world.vassal_investment_cooldowns = cooldowns

    blunted = "" if gain >= INVEST_LOYALTY_GAIN else (
        " — the Emperor's faltering grip blunts the gesture"
    )
    return {
        "success": True,
        "message": (
            f"Invested in {vassal_name}: +{gain} loyalty "
            f"({old_loyalty} → {state['loyalty']}){blunted}. "
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
    lord = state.get("lord", getattr(world, 'player_nation', 'France'))
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
        # More autonomy = vassal is happier. VS-R: the +10 is a CHEAP one-shot,
        # blunted in the lord's spiral band (byte-identical at healthy grip).
        mult = get_authority_lever_multiplier(world, lord)
        gain = int(10 * mult)
        state["loyalty"] = int(min(LOYALTY_MAX, state["loyalty"] + gain))
        # C2 (playtest): name the cause when the gesture is blunted, matching
        # invest_in_vassal — otherwise the player who followed the "grant
        # autonomy" hint hits an unexplained reduced value.
        blunted = "" if gain >= 10 else (
            " - the Emperor's faltering grip blunts the gesture"
        )
        loyalty_msg = f"+{gain} loyalty (increased autonomy){blunted}"
    else:
        # Less autonomy = vassal is unhappy. NEVER softened — low grip must not
        # cushion a downgrade (VS-R Q3).
        state["loyalty"] = int(max(LOYALTY_MIN, state["loyalty"] - 15))
        loyalty_msg = "-15 loyalty (decreased autonomy)"

    # VP-D5 (Sweep 4): surface the tribute TRADE-OFF, not just the new rate.
    # Granting autonomy is a PERMANENT income cut (Satellite 75% -> Autonomous
    # 50%); a player following the "grant autonomy" recovery hint was buying a
    # one-shot loyalty bump without being told the recurring cost. Show the
    # delta directionally so the cost/benefit is explicit at the decision point.
    old_tribute = TRIBUTE_RATES[old_level] * 100
    new_tribute = TRIBUTE_RATES[new_level] * 100
    if new_tribute < old_tribute:
        tribute_msg = (f"Tribute rate: {old_tribute:.0f}% → {new_tribute:.0f}% "
                       f"(a permanent income cut)")
    elif new_tribute > old_tribute:
        tribute_msg = (f"Tribute rate: {old_tribute:.0f}% → {new_tribute:.0f}% "
                       f"(you collect more of their income)")
    else:
        tribute_msg = f"Tribute rate: {new_tribute:.0f}%"

    return {
        "success": True,
        "message": (
            f"{vassal_name} autonomy changed: "
            f"{AUTONOMY_NAMES[old_level]} → {AUTONOMY_NAMES[new_level]}. "
            f"{loyalty_msg}. {tribute_msg}."
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

    # VS-R: the Allies peel satellites precisely when Napoleon looks weak. As the
    # player's imperial grip falls the courting unlock reaches DEEPER (threshold
    # 50 -> 50 + bonus) and each success bites HARDER (loyalty_reduction x1.0 ->
    # x1.5). Both are 0 / x1.0 at healthy grip, so boot behaviour is byte-
    # identical. Bounded by the existing 3-turn cooldown + one-vassal-per-turn cap.
    player_grip = get_imperial_grip(world, player)
    unlock_bonus = courting_unlock_bonus(player_grip)
    eff_scale = courting_effectiveness_scale(player_grip)

    for vassal_name, state in world.vassals.items():
        if state["lord"] != player:
            continue
        if state["loyalty"] >= 50 + unlock_bonus:
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

        # Calculate loyalty reduction (VS-R: scaled by the player's grip)
        diplo_key = world._make_diplo_key(vassal_name, nation)
        relation = world.nation_relations.get(diplo_key, 0)
        base_reduction = 15 if relation > 0 else 5
        loyalty_reduction = int(round(base_reduction * eff_scale))

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
            vassal_capital = world.get_nation_capital(vassal_name) or vassal_name
            queue_dispatch_event(world, "diplomatic_vassal_courting",
                                {"enemy": nation, "vassal_capital": vassal_capital},
                                "detection_60pct")

        # Only court one vassal per nation per turn
        break

    return events
