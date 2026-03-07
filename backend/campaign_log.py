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


# ============================================================================
# ACTION DISPLAY NAMES — translate raw internal names for campaign log
# ============================================================================

# Objection context: "Marshal objected to [action]"
_OBJECTION_DISPLAY = {
    "attack": "attacking",
    "move": "moving",
    "defend": "defending",
    "fortify": "fortifying",
    "unfortify": "abandoning fortification",
    "form_square": "forming square",
    "break_square": "breaking square",
    "drill": "drilling",
    "stance_change": "changing stance",
    "retreat": "retreating",
    "wait": "waiting",
    "recruit": "recruiting",
    "scout": "scouting",
    "hold": "holding",
    "build": "building",
    "repair": "repairing",
    "garrison": "garrisoning",
    "bombardment": "bombarding",
}

# Defiance context: "Marshal defied orders and [action] instead"
_DEFIANCE_DISPLAY = {
    "attack": "attacked",
    "move": "moved",
    "defend": "defended",
    "fortify": "fortified",
    "unfortify": "abandoned fortification",
    "form_square": "formed square",
    "break_square": "broke square",
    "drill": "drilled",
    "stance_change": "changed stance",
    "retreat": "retreated",
    "wait": "waited",
    "recruit": "recruited",
    "scout": "scouted",
    "hold": "held position",
    "build": "built",
    "repair": "repaired",
    "garrison": "garrisoned",
    "bombardment": "bombarded",
}


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

        # Vassal rebellion: player vassal always shown
        if event_type == "diplomatic_vassal_rebellion":
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
        return f"War declared: {aggressor} → {target}"

    if event_type == "diplomatic_vassal_rebellion":
        nation = event.get("nation") or event.get("vassal", "Unknown")
        return f"Vassal rebellion: {nation} has broken free!"

    if event_type == "diplomatic_treaty_broken":
        nation = event.get("breaker") or event.get("nation", "Unknown")
        treaty_type = (event.get("treaty_type") or "treaty").replace("_", " ")
        return f"Treaty broken: {nation} — {treaty_type}"

    if event_type == "diplomatic_alliance_cascade":
        nation = event.get("defender") or event.get("nation", "Unknown")
        ally = event.get("ally", "Unknown")
        return f"Alliance cascade: {nation} enters war via {ally}"

    if event_type == "diplomatic_ai_ai_treaty":
        nation_a = event.get("nation_a", "Unknown")
        nation_b = event.get("nation_b", "Unknown")
        treaty_type = (event.get("treaty_type") or "treaty").replace("_", " ")
        return f"AI-AI treaty: {nation_a} and {nation_b} ({treaty_type})"

    return f"Event: {event_type}"
