"""
Campaign Log — Fog-filtered event log for player review (Phase 6.5)

Filters world.event_log to narrative-relevant events and applies fog of war
rules so the player only sees what they should know about.

Design decisions:
- 14 event types shown (combat, territory, economy, command categories)
- Fog filtering uses current visibility (consistent with _filter_tactical_events_by_visibility)
- One-liner formatting with safe .get() defaults throughout
"""

from backend.models.intel import FULL, PARTIAL


# Action display names — single source in display_names.py (R7)
from backend.display_names import OBJECTION_DISPLAY as _OBJECTION_DISPLAY
from backend.display_names import DEFIANCE_DISPLAY as _DEFIANCE_DISPLAY
from backend.display_names import diplomatic_decision_reason_display


def _display_action(action: str) -> str:
    """Translate raw action name for objection context (gerund form)."""
    if not action:
        return action
    return _OBJECTION_DISPLAY.get(action, action.replace("_", " "))


def _display_defiance_action(action: str) -> str:
    """Translate raw action name for defiance context (past tense)."""
    if not action:
        return action
    return _DEFIANCE_DISPLAY.get(action, action.replace("_", " "))


def _decision_reason_suffix(event: dict) -> str:
    reason = str(event.get("decision_reason", "") or "")
    if not reason:
        return ""
    return f" ({diplomatic_decision_reason_display(reason)})"


# ============================================================================
# EVENT TYPE WHITELIST — only these 14 types appear in the Campaign Log
# ============================================================================

CAMPAIGN_LOG_TYPES = {
    # Combat
    "battle",
    "bombardment",
    "retreat",
    "marshal_broken",
    "marshal_recovered",
    # Territory
    "region_captured",
    # Economy
    "recruitment",
    "building_started",
    "building_completed",
    "building_damaged",
    "bankruptcy",
    "desertion",
    # Command
    "objection",
    "strategic_order",
    "defiance",
    # Diplomacy (Session 8D)
    "diplomatic_treaty_signed",
    "diplomatic_war_declared",
    "diplomatic_vassal_rebellion",
    "diplomatic_treaty_broken",
    "diplomatic_alliance_cascade",
    "diplomatic_ai_ai_treaty",
    "commitment_paradox_resolved",
    # Deep audit fix: missing event types
    "war_declaration",
    "defensive_cascade",
    "offensive_cascade",
    "coalition_declared",
    "coalition_dissolved",
    # V3 Session 8: missing event types
    "nation_eliminated",
    "vassal_auto_join_war",
    "coalition_member_left",
    # R8 Session 6: 16 previously-silent event types
    "ai_proposal_accepted",
    "ai_proposal_counter_failed",
    "ai_proposal_rejected",
    "auto_downgrade",
    "coalition_brewing_cancelled",
    "coalition_brewing_started",
    "counter_offer_accepted",
    "counter_offer_rejected",
    "diplomatic_discrepancy",
    "diplomatic_downgrade",
    "diplomatic_mission_cancelled_eliminated",
    "diplomatic_mission_started",
    "diplomatic_proposal_sent",
    "garrison_placed",
    "proposal_voided_by_coalition",
    "relationship_change",
    # PL-14: Ultimatum events
    "ultimatum_issued",
    "ultimatum_accepted",
    "ultimatum_rejected",
    # PL-27/PL-34: Proposal queue visibility events
    "proposal_arrived",
    "proposal_expired_unseen",
    "proposal_dropped_overflow",
    # Offer lifetime: lapsed at end of turn
    "offer_lapsed",
    "hard_reject_posture_triggered",
    "hard_reject_posture_cleared",
}

# ============================================================================
# CATEGORY MAP — maps event type to display category
# ============================================================================

CATEGORY_MAP = {
    "battle": "combat",
    "bombardment": "combat",
    "retreat": "combat",
    "marshal_broken": "combat",
    "marshal_recovered": "combat",
    "region_captured": "territory",
    "recruitment": "economy",
    "building_started": "economy",
    "building_completed": "economy",
    "building_damaged": "economy",
    "bankruptcy": "economy",
    "desertion": "economy",
    "objection": "command",
    "strategic_order": "command",
    "defiance": "command",
    # Diplomacy (Session 8D)
    "diplomatic_treaty_signed": "diplomacy",
    "diplomatic_war_declared": "diplomacy",
    "diplomatic_vassal_rebellion": "diplomacy",
    "diplomatic_treaty_broken": "diplomacy",
    "diplomatic_alliance_cascade": "diplomacy",
    "diplomatic_ai_ai_treaty": "diplomacy",
    "commitment_paradox_resolved": "diplomacy",
    # Deep audit fix: missing event types
    "war_declaration": "diplomacy",
    "defensive_cascade": "diplomacy",
    "offensive_cascade": "diplomacy",
    "coalition_declared": "diplomacy",
    "coalition_dissolved": "diplomacy",
    # V3 Session 8: missing event types
    "nation_eliminated": "diplomacy",
    "vassal_auto_join_war": "diplomacy",
    "coalition_member_left": "diplomacy",
    # R8 Session 6: 16 previously-silent event types
    "ai_proposal_accepted": "diplomacy",
    "ai_proposal_counter_failed": "diplomacy",
    "ai_proposal_rejected": "diplomacy",
    "auto_downgrade": "diplomacy",
    "coalition_brewing_cancelled": "diplomacy",
    "coalition_brewing_started": "diplomacy",
    "counter_offer_accepted": "diplomacy",
    "counter_offer_rejected": "diplomacy",
    "diplomatic_discrepancy": "diplomacy",
    "diplomatic_downgrade": "diplomacy",
    "diplomatic_mission_cancelled_eliminated": "diplomacy",
    "diplomatic_mission_started": "diplomacy",
    "diplomatic_proposal_sent": "diplomacy",
    "garrison_placed": "territory",
    "proposal_voided_by_coalition": "diplomacy",
    "relationship_change": "command",
    # PL-14: Ultimatum events
    "ultimatum_issued": "diplomacy",
    "ultimatum_accepted": "diplomacy",
    "ultimatum_rejected": "diplomacy",
    # PL-27/PL-34: Proposal queue visibility events
    "proposal_arrived": "diplomacy",
    "proposal_expired_unseen": "diplomacy",
    "proposal_dropped_overflow": "diplomacy",
    # Offer lifetime: lapsed at end of turn
    "offer_lapsed": "diplomacy",
    "hard_reject_posture_triggered": "diplomacy",
    "hard_reject_posture_cleared": "diplomacy",
}


def _is_player_event(event: dict, player_nation: str) -> bool:
    """Check if an event belongs to the player (always shown regardless of fog)."""
    # Direct nation match
    if event.get("nation") == player_nation:
        return True
    if event.get("attacker_nation") == player_nation:
        return True
    if event.get("defender_nation") == player_nation:
        return True
    # captured_by for region_captured
    if event.get("captured_by") == player_nation:
        return True
    return False


def _get_event_region(event: dict) -> str:
    """Extract region name from an event dict (various field names used)."""
    return (event.get("location") or event.get("region")
            or event.get("from") or event.get("defender_location")
            or event.get("attacker_location") or "")


def _player_marshal_involved(event: dict, world_state) -> bool:
    """Check if a player marshal is involved in a combat event."""
    player_nation = world_state.player_nation
    for field in ("attacker", "defender", "marshal"):
        name = event.get(field, "")
        if name:
            m = world_state.get_marshal(name)
            if m and m.nation == player_nation:
                return True
    return False


def filter_campaign_log(event_log: list, world_state) -> list:
    """
    Filter the full event log for the Campaign Log overlay.

    Rules:
    1. Only CAMPAIGN_LOG_TYPES are included
    2. Player-generated events (objection, strategic_order) always shown
    3. Player-nation events always shown
    4. Battle/bombardment: shown if player marshal involved OR region FULL
    5. Retreat/marshal_broken/marshal_recovered: player marshal OR region PARTIAL+
    6. Region_captured: player captures always; enemy if region PARTIAL+
    7. Enemy economy events: region PARTIAL+

    Args:
        event_log: Full world.event_log list
        world_state: WorldState for fog checks

    Returns:
        Filtered list of event dicts (originals, not copies)
    """
    if not event_log:
        return []

    player_nation = world_state.player_nation
    filtered = []

    for event in event_log:
        if not isinstance(event, dict):
            continue

        event_type = event.get("type", "")
        if event_type not in CAMPAIGN_LOG_TYPES:
            continue

        # Command events (player-generated) — always show
        if event_type in ("objection", "strategic_order", "defiance"):
            filtered.append(event)
            continue

        # Player-nation events — always show
        if _is_player_event(event, player_nation):
            filtered.append(event)
            continue

        if event_type == "commitment_paradox_resolved":
            filtered.append(event)
            continue

        # From here: enemy events — need fog checks
        region = _get_event_region(event)

        # Battle / bombardment: player marshal involved OR region FULL
        if event_type in ("battle", "bombardment"):
            if _player_marshal_involved(event, world_state):
                filtered.append(event)
                continue
            if region:
                intel = world_state.get_region_intel(region)
                if intel.visibility == FULL:
                    filtered.append(event)
            continue

        # Retreat / marshal_broken / marshal_recovered: player marshal OR PARTIAL+
        if event_type in ("retreat", "marshal_broken", "marshal_recovered"):
            if _player_marshal_involved(event, world_state):
                filtered.append(event)
                continue
            if region:
                intel = world_state.get_region_intel(region)
                if intel.visibility in (FULL, PARTIAL):
                    # FINAL-16: Strip retreat destination if destination region is fogged
                    if event_type == "retreat" and event.get("to"):
                        to_region = event.get("to")
                        to_intel = world_state.get_region_intel(to_region)
                        if to_intel.visibility not in (FULL, PARTIAL):
                            event = dict(event)  # Copy to avoid mutating original
                            del event["to"]
                    filtered.append(event)
            continue

        # Region captured: enemy captures if region PARTIAL+
        if event_type == "region_captured":
            if region:
                intel = world_state.get_region_intel(region)
                if intel.visibility in (FULL, PARTIAL):
                    filtered.append(event)
            continue

        # Bankruptcy: public knowledge — always show
        if event_type == "bankruptcy":
            filtered.append(event)
            continue

        # Economy events (enemy): region PARTIAL+
        if event_type in ("recruitment", "building_started", "building_completed",
                          "building_damaged", "desertion"):
            # Try to get a region for the event
            econ_region = event.get("region") or event.get("location") or ""
            if econ_region:
                intel = world_state.get_region_intel(econ_region)
                if intel.visibility in (FULL, PARTIAL):
                    filtered.append(event)
            # Bankruptcy/desertion may lack region — check nation match
            # (already handled above by _is_player_event for player nation)
            continue

        # Diplomacy events (Session 8D): PARTIAL+ on any relevant nation
        if event_type in ("diplomatic_treaty_signed", "diplomatic_war_declared",
                          "diplomatic_treaty_broken", "diplomatic_alliance_cascade",
                          "diplomatic_ai_ai_treaty"):
            # Check PARTIAL+ on any nation mentioned
            from backend.game_logic.diplomatic_ledger import _get_nation_visibility
            nations_to_check = []
            for key in ("nation", "nation_a", "nation_b", "target", "aggressor"):
                val = event.get(key)
                if val:
                    nations_to_check.append(val)
            visible = False
            for nation in nations_to_check:
                if nation == player_nation:
                    visible = True
                    break
                vis = _get_nation_visibility(nation, world_state)
                if vis in (FULL, PARTIAL):
                    visible = True
                    break
            if visible:
                filtered.append(event)
            continue

        # War/cascade events: player-involved or PARTIAL+ on any nation
        if event_type in ("war_declaration", "defensive_cascade", "offensive_cascade"):
            from backend.game_logic.diplomatic_ledger import _get_nation_visibility
            nations_to_check = []
            for key in ("aggressor", "target", "defender", "ally", "against", "attacker_ally"):
                val = event.get(key)
                if val:
                    nations_to_check.append(val)
            visible = False
            for nation in nations_to_check:
                if nation == player_nation:
                    visible = True
                    break
                vis = _get_nation_visibility(nation, world_state)
                if vis in (FULL, PARTIAL):
                    visible = True
                    break
            if visible:
                filtered.append(event)
            continue

        # Coalition events: always show (they target France)
        if event_type in ("coalition_declared", "coalition_dissolved", "coalition_member_left"):
            filtered.append(event)
            continue

        # Vassal rebellion: player vassal always shown
        if event_type == "diplomatic_vassal_rebellion":
            filtered.append(event)
            continue

        # Nation eliminated: public knowledge
        if event_type == "nation_eliminated":
            filtered.append(event)
            continue

        # Vassal auto-joining war: show if player involved or PARTIAL+
        if event_type == "vassal_auto_join_war":
            from backend.game_logic.diplomatic_ledger import _get_nation_visibility
            vassal = event.get("vassal") or event.get("nation", "")
            overlord = event.get("overlord", "")
            visible = False
            for nation in (vassal, overlord):
                if nation == player_nation:
                    visible = True
                    break
                if nation:
                    vis = _get_nation_visibility(nation, world_state)
                    if vis in (FULL, PARTIAL):
                        visible = True
                        break
            if visible:
                filtered.append(event)
            continue

        # ── R8 Session 6: fog rules for 16 previously-silent types ──

        # Player-generated diplomacy events: always show
        if event_type in ("diplomatic_proposal_sent", "diplomatic_mission_started",
                          "diplomatic_discrepancy", "counter_offer_accepted",
                          "counter_offer_rejected"):
            filtered.append(event)
            continue

        # AI proposal responses to player: always show (player is target)
        if event_type in ("ai_proposal_accepted", "ai_proposal_rejected",
                          "ai_proposal_counter_failed"):
            filtered.append(event)
            continue

        # PL-27/PL-34: Proposal queue events + lapse — always show (player-facing)
        if event_type in ("proposal_arrived", "proposal_expired_unseen",
                          "proposal_dropped_overflow", "offer_lapsed",
                          "hard_reject_posture_triggered", "hard_reject_posture_cleared"):
            filtered.append(event)
            continue

        # Coalition brewing: always show (targets France)
        if event_type in ("coalition_brewing_started", "coalition_brewing_cancelled",
                          "proposal_voided_by_coalition"):
            filtered.append(event)
            continue

        # Garrison placed: show if player or region PARTIAL+
        if event_type == "garrison_placed":
            garrison_region = event.get("region", "")
            if garrison_region:
                intel = world_state.get_region_intel(garrison_region)
                if intel.visibility in (FULL, PARTIAL):
                    filtered.append(event)
            continue

        # Relationship change: always show (player marshals only)
        if event_type == "relationship_change":
            filtered.append(event)
            continue

        # Diplomatic downgrade / auto_downgrade: PARTIAL+ on either nation
        if event_type in ("diplomatic_downgrade", "auto_downgrade"):
            from backend.game_logic.diplomatic_ledger import _get_nation_visibility
            nations_to_check = []
            for key in ("nation_a", "nation_b"):
                val = event.get(key)
                if val:
                    nations_to_check.append(val)
            visible = False
            for nation in nations_to_check:
                if nation == player_nation:
                    visible = True
                    break
                vis = _get_nation_visibility(nation, world_state)
                if vis in (FULL, PARTIAL):
                    visible = True
                    break
            if visible:
                filtered.append(event)
            continue

        # Mission cancelled (eliminated nation): always show
        if event_type == "diplomatic_mission_cancelled_eliminated":
            filtered.append(event)
            continue

    return filtered


def _name_tag(name: str, nation: str) -> str:
    """Format 'Name (Nation)' when nation is available, else just 'Name'."""
    if nation:
        return f"{name} ({nation})"
    return name


def format_event_oneliner(event: dict) -> str:
    """
    Produce a human-readable one-liner for a campaign log event.

    Uses .get() with safe defaults throughout — missing fields produce
    graceful degradation rather than crashes.  Nation tags are appended
    to marshal names so the player can identify friend/foe at a glance.

    Args:
        event: A single event dict from the event log

    Returns:
        Human-readable one-liner string
    """
    event_type = event.get("type", "")

    if event_type in ("diplomatic_war_declared", "war_declaration") and event.get("breached_treaty"):
        aggressor = event.get("aggressor") or event.get("nation", "Unknown")
        target = event.get("target", "Unknown")
        return f"War declared: {aggressor} -> {target} (shattering {event.get('breached_treaty')})"

    if event_type == "diplomatic_treaty_broken":
        nation = event.get("breaker") or event.get("nation", "Unknown")
        treaty_type = (event.get("treaty_type") or "treaty").replace("_", " ")
        target = event.get("other") or event.get("target") or "Unknown"
        reason_phrase = event.get("reason_phrase", "")
        family = event.get("end_reason_family", "")
        # Distinguish forced / counterparty-led ruptures from voluntary breach
        # so the log one-liner carries the fault classification.
        if family == "obsolescence_or_external":
            return f"Treaty dragged apart: {nation} - {treaty_type} with {target} (cascade)"
        if family == "counterparty_reversal":
            return f"Treaty broken by counterparty: {target} - {treaty_type} with {nation}"
        if reason_phrase:
            return f"Treaty broken: {nation} - {treaty_type} with {target} {reason_phrase}"
        return f"Treaty broken: {nation} - {treaty_type} with {target}"

    if event_type == "commitment_paradox_resolved":
        chosen = event.get("chosen_nation", "Unknown")
        spurned = event.get("spurned_nation", "Unknown")
        reliability_before = event.get("reliability_before")
        reliability_after = event.get("reliability_after")
        if reliability_before is not None and reliability_after is not None:
            return (
                f"Commitment paradox resolved: chose {chosen} over {spurned} "
                f"({reliability_before} -> {reliability_after} reliability)"
            )
        return f"Commitment paradox resolved: chose {chosen} over {spurned}"

    if event_type == "battle":
        attacker = event.get("attacker", "Unknown")
        atk_nation = event.get("attacker_nation", "")
        defender = event.get("defender", "Unknown")
        def_nation = event.get("defender_nation", "")
        location = event.get("location", "unknown location")
        outcome = event.get("outcome", "")
        atk_cas = event.get("attacker_casualties", 0)
        def_cas = event.get("defender_casualties", 0)
        if outcome == "attacker_wins":
            result = f"{attacker} victory"
        elif outcome == "defender_wins":
            result = f"{defender} victory"
        else:
            result = "draw"
        return (f"{_name_tag(attacker, atk_nation)} attacked "
                f"{_name_tag(defender, def_nation)} at {location} — "
                f"{result} ({atk_cas:,} / {def_cas:,} casualties)")

    if event_type == "bombardment":
        attacker = event.get("attacker", "Unknown")
        atk_nation = event.get("attacker_nation", "")
        location = (event.get("defender_location")
                    or event.get("attacker_location")
                    or "unknown location")
        defender_casualties = event.get("defender_casualties", 0)
        return (f"{_name_tag(attacker, atk_nation)} bombarded {location} — "
                f"{defender_casualties:,} casualties")

    if event_type == "retreat":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        from_loc = event.get("from", "unknown")
        to_loc = event.get("to", "")
        tag = _name_tag(marshal, nation)
        if to_loc:
            return f"{tag} retreated from {from_loc} to {to_loc}"
        return f"{tag} retreated from {from_loc}"

    if event_type == "marshal_broken":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        location = event.get("location", "unknown location")
        return f"{_name_tag(marshal, nation)} was broken at {location}"

    if event_type == "marshal_recovered":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        location = event.get("location", "")
        tag = _name_tag(marshal, nation)
        if location:
            return f"{tag} recovered at {location}"
        return f"{tag} recovered"

    if event_type == "region_captured":
        captured_by = event.get("captured_by", "Unknown")
        region = event.get("region", "unknown region")
        method = event.get("method", "")
        if method:
            return f"{region} captured by {captured_by} ({method})"
        return f"{region} captured by {captured_by}"

    if event_type == "recruitment":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        amount = event.get("amount", 0)
        recruit_type = event.get("recruit_type", "infantry")
        return f"{_name_tag(marshal, nation)} recruited {amount:,} {recruit_type}"

    if event_type == "building_started":
        building = (event.get("building") or "building").replace("_", " ").title()
        region = event.get("region", "unknown region")
        return f"Construction started: {building} in {region}"

    if event_type == "building_completed":
        building = (event.get("building") or "building").replace("_", " ").title()
        region = event.get("region", "unknown region")
        return f"Construction complete: {building} in {region}"

    if event_type == "building_damaged":
        building = (event.get("building") or "building").replace("_", " ").title()
        region = event.get("region", "unknown region")
        return f"Building damaged: {building} in {region}"

    if event_type == "bankruptcy":
        nation = event.get("nation", "Unknown")
        return f"{nation} treasury bankrupt — desertion imminent"

    if event_type == "desertion":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        amount = event.get("amount", 0)
        return f"Desertion: {_name_tag(marshal, nation)} lost {amount:,} troops"

    if event_type == "objection":
        marshal = event.get("marshal", "Unknown")
        action = _display_action(event.get("action", ""))
        resolution = event.get("resolution", "")
        if action and resolution:
            return f"{marshal} objected to {action} ({resolution})"
        if action:
            return f"{marshal} objected to {action}"
        return f"{marshal} objected to order"

    if event_type == "strategic_order":
        marshal = event.get("marshal", "Unknown")
        order_type = event.get("order_type", "UNKNOWN")
        # Human-readable order type (MOVE_TO → "move to", HOLD → "hold", etc.)
        display_order = {
            "MOVE_TO": "move to", "HOLD": "hold",
            "SUPPORT": "support", "PURSUE": "pursue",
        }.get(order_type, order_type.lower().replace("_", " "))
        destination = event.get("destination", "")
        if destination:
            return f"{marshal} ordered to {display_order} {destination}"
        return f"{marshal} ordered to {display_order}"

    if event_type == "defiance":
        marshal = event.get("marshal", "Unknown")
        defiance_action = _display_defiance_action(event.get("defiance_action", "acted independently"))
        return f"{marshal} defied orders and {defiance_action} instead"

    # ── Diplomacy events (Session 8D) ──
    if event_type == "diplomatic_treaty_signed":
        nation_a = event.get("nation_a") or (event.get("nations", [None, None])[0] or "Unknown")
        nation_b = event.get("nation_b") or (event.get("nations", [None, None])[1] if len(event.get("nations", [])) > 1 else "Unknown")
        treaty_type = (event.get("treaty_type") or "treaty").replace("_", " ")
        return f"Treaty signed: {nation_a} and {nation_b} ({treaty_type})"

    if event_type == "diplomatic_war_declared":
        aggressor = event.get("aggressor") or event.get("nation", "Unknown")
        target = event.get("target", "Unknown")
        breached_treaty = event.get("breached_treaty", "")
        if breached_treaty:
            return f"War declared: {aggressor} → {target} (shattering {breached_treaty})"
        return f"War declared: {aggressor} → {target}"

    if event_type == "diplomatic_vassal_rebellion":
        nation = event.get("nation") or event.get("vassal", "Unknown")
        return f"Vassal rebellion: {nation} has broken free!"


    if event_type == "diplomatic_alliance_cascade":
        nation = event.get("defender") or event.get("nation", "Unknown")
        ally = event.get("ally", "Unknown")
        return f"Alliance cascade: {nation} enters war via {ally}"

    if event_type == "diplomatic_ai_ai_treaty":
        nation_a = event.get("nation_a", "Unknown")
        nation_b = event.get("nation_b", "Unknown")
        treaty_type = (event.get("treaty_type") or "treaty").replace("_", " ")
        return f"AI-AI treaty: {nation_a} and {nation_b} ({treaty_type})"

    # Deep audit fix: new event types
    if event_type == "war_declaration":
        aggressor = event.get("aggressor") or event.get("nation", "Unknown")
        target = event.get("target", "Unknown")
        return f"War declared: {aggressor} → {target}"

    if event_type == "defensive_cascade":
        nation = event.get("nation", "Unknown")
        ally = event.get("ally", "Unknown")
        return f"Defensive cascade: {nation} joins war via {ally}"

    if event_type == "offensive_cascade":
        nation = event.get("nation", "Unknown")
        aggressor = event.get("aggressor", "Unknown")
        return f"Offensive cascade: {nation} joins {aggressor}'s war"

    if event_type == "coalition_declared":
        members = event.get("members", [])
        return f"Coalition formed against France! Members: {', '.join(members) if members else 'Unknown'}"

    if event_type == "coalition_dissolved":
        return "Coalition against France has dissolved."

    # V3 Session 8: new event types
    if event_type == "nation_eliminated":
        nation = event.get("nation", "Unknown")
        return f"{nation} has been eliminated from the war."

    if event_type == "vassal_auto_join_war":
        vassal = event.get("vassal") or event.get("nation", "Unknown")
        overlord = event.get("overlord", "Unknown")
        return f"Vassal {vassal} joined {overlord}'s war."

    if event_type == "coalition_member_left":
        nation = event.get("nation", "Unknown")
        return f"{nation} has left the coalition."

    # ── R8 Session 6: format strings for 16 previously-silent types ──

    if event_type == "ai_proposal_accepted":
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"{source} accepted our {proposal_type} proposal{_decision_reason_suffix(event)}"

    if event_type == "ai_proposal_rejected":
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"{source} rejected our {proposal_type} proposal{_decision_reason_suffix(event)}"

    if event_type == "ai_proposal_counter_failed":
        source = event.get("source", "Unknown")
        return f"{source} rejected our counter-offer{_decision_reason_suffix(event)}"

    if event_type == "auto_downgrade":
        nation_a = event.get("nation_a", "Unknown")
        nation_b = event.get("nation_b", "Unknown")
        from_state = (event.get("from_state") or "treaty").replace("_", " ")
        to_state = (event.get("to_state") or "peace").replace("_", " ")
        return f"Relations auto-downgraded: {nation_a}–{nation_b} ({from_state} → {to_state})"

    if event_type == "coalition_brewing_started":
        threat = event.get("threat_level", 0)
        qualifying = event.get("qualifying_nations", [])
        nations_str = ", ".join(qualifying) if qualifying else "several nations"
        return f"Coalition brewing — {nations_str} alarmed (threat: {threat})"

    if event_type == "coalition_brewing_cancelled":
        return "Coalition threat has subsided"

    if event_type == "counter_offer_accepted":
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"{source} accepted our counter-offer ({proposal_type}){_decision_reason_suffix(event)}"

    if event_type == "counter_offer_rejected":
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"{source} rejected our counter-offer ({proposal_type}){_decision_reason_suffix(event)}"

    if event_type == "diplomatic_discrepancy":
        message = event.get("message", "Talleyrand altered your proposal")
        return message

    if event_type == "diplomatic_downgrade":
        nation_a = event.get("nation_a", "Unknown")
        nation_b = event.get("nation_b", "Unknown")
        from_state = (event.get("from_state") or "treaty").replace("_", " ")
        to_state = (event.get("to_state") or "peace").replace("_", " ")
        return f"Relations downgraded: {nation_a}–{nation_b} ({from_state} → {to_state})"

    if event_type == "diplomatic_mission_cancelled_eliminated":
        target = event.get("target", "Unknown")
        return f"Diplomatic mission to {target} cancelled — nation eliminated"

    if event_type == "diplomatic_mission_started":
        target = event.get("target", "Unknown")
        mission_type = (event.get("mission_type") or "diplomatic mission").replace("_", " ")
        return f"Talleyrand dispatched on {mission_type} to {target}"

    if event_type == "diplomatic_proposal_sent":
        target = event.get("target", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"Proposal sent to {target} ({proposal_type})"

    # PL-27/PL-34: Proposal queue visibility events
    if event_type == "proposal_arrived":
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"An envoy from {source} has arrived with a {proposal_type} proposal{_decision_reason_suffix(event)}"

    if event_type == "hard_reject_posture_triggered":
        victim = event.get("victim_nation", "Unknown")
        perpetrator = event.get("perpetrator_nation", "France")
        return f"{victim} has shut the chancery to {perpetrator} after repeated betrayals"

    if event_type == "hard_reject_posture_cleared":
        victim = event.get("victim_nation", "Unknown")
        perpetrator = event.get("perpetrator_nation", "France")
        return f"{victim} has reopened deeper diplomacy with {perpetrator}"

    if event_type == "proposal_expired_unseen":
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"{source}'s {proposal_type} envoy departed — proposal expired unanswered"

    if event_type == "proposal_dropped_overflow":
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"{source}'s {proposal_type} envoy turned away — too many waiting"

    if event_type == "offer_lapsed":
        nation = event.get("nation", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"{nation}'s {proposal_type} offer lapsed unanswered"

    if event_type == "garrison_placed":
        marshal = event.get("marshal", "Unknown")
        region = event.get("region", "unknown region")
        troops = event.get("troops", 0)
        return f"{marshal} garrisoned {region} ({troops:,} troops)"

    if event_type == "proposal_voided_by_coalition":
        target = event.get("target", "Unknown")
        return f"Envoy to {target} recalled — they joined the coalition"

    if event_type == "relationship_change":
        marshal = event.get("marshal", "Unknown")
        toward = event.get("toward", "Unknown")
        change = event.get("change", 0)
        new_label = event.get("new_label", "")
        sign = "+" if change > 0 else ""
        label_str = f" ({new_label})" if new_label else ""
        return f"{marshal} → {toward}: {sign}{change}{label_str}"

    # PL-14: Ultimatum events
    if event_type == "ultimatum_issued":
        target = event.get("target", "Unknown")
        return f"Ultimatum delivered to {target}"

    if event_type == "ultimatum_accepted":
        target = event.get("target", "Unknown")
        return f"{target} accepted our ultimatum — concessions extracted"

    if event_type == "ultimatum_rejected":
        target = event.get("target", "Unknown")
        return f"{target} rejected our ultimatum — casus belli granted"

    return f"Event: {event_type}"
