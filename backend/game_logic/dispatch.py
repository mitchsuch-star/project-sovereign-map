"""
Morning Dispatch — Berthier's turn-start briefing (Phase 6.5)

Builds a structured dict for Godot to render as terminal output at turn start.
All values int()-wrapped per CLAUDE.md rule: "All numbers to Godot: int()".

Fog-filtered: enemy intel uses RegionIntel visibility, never raw marshal data.
"""

from typing import Dict, List, Optional, Any

from backend.models.intel import (
    FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN,
    STRENGTH_BANDS, get_strength_band,
)


# ============================================================================
# STRENGTH BAND MIDPOINTS — for estimating enemy strength from fog intel
# ============================================================================
# Maps band string -> midpoint estimate (used for threat ratio calculation)
BAND_MIDPOINTS: Dict[str, int] = {
    "no forces": 0,
    "screening force": 2500,
    "small force": 10000,
    "substantial force": 27500,
    "large force": 55000,
    "massive force": 85000,
}


def build_morning_dispatch(world, tactical_events: Optional[List] = None) -> Dict[str, Any]:
    """
    Build the morning dispatch dict for Godot rendering.

    Called AFTER turn_manager.end_turn() completes, so world state
    reflects the start of the new turn (post enemy phase, post tactical
    processing, post income).

    Args:
        world: WorldState instance
        tactical_events: Optional list of tactical event dicts from turn
            processing (attrition, construction, etc.). Absorbed into
            the dispatch's TURN EVENTS section.

    Returns:
        Dict with turn, situation, marshals, intelligence, turn_events,
        berthier_note. All numeric values int()-wrapped.
    """
    # TODO: Post-EA — thread player_nation from world state
    player_nation = "France"

    dispatch = {
        "turn": int(world.current_turn),
        "situation": _build_situation(world, player_nation),
        "marshals": _build_marshal_status(world, player_nation),
        "intelligence": _build_intelligence(world, player_nation),
        "turn_events": _build_turn_events(tactical_events or [], player_nation),
    }

    # Berthier note depends on marshals + situation
    dispatch["berthier_note"] = _pick_berthier_note(
        world, player_nation, dispatch["marshals"], dispatch["situation"]
    )

    # Store on world for dispatch re-read screen (Session A)
    world.last_morning_dispatch = dispatch

    return dispatch


# ============================================================================
# SITUATION
# ============================================================================

def _build_situation(world, player_nation: str) -> Dict[str, Any]:
    """Build the SITUATION section of the dispatch."""
    player_regions = 0
    enemy_regions = 0
    for region in world.regions.values():
        if region.controller == player_nation:
            player_regions += 1
        elif region.controller is not None:
            enemy_regions += 1

    treasury = int(world.nation_gold.get(player_nation, 0))

    # Compute projected income/upkeep for this turn (same values the
    # executor shows in the turn header — recalculated on new-turn state)
    income_data = world.calculate_turn_income(player_nation)
    upkeep_data = world.calculate_turn_upkeep(player_nation)
    income = int(income_data["income"])
    upkeep = int(upkeep_data["total"])
    treasury_delta = int(income - upkeep)

    bankrupt = int(world.nation_bankruptcy_turns.get(player_nation, 0)) > 0

    # Fog-filtered strength ratio
    french_strength = _get_nation_total_strength(world, player_nation)
    estimated_enemy_strength = _estimate_enemy_strength_from_intel(world, player_nation)
    if french_strength > 0:
        strength_ratio_pct = int(round(
            (estimated_enemy_strength / french_strength) * 100
        ))
    else:
        strength_ratio_pct = 999  # Edge case: no French forces

    return {
        "player_regions": int(player_regions),
        "enemy_regions": int(enemy_regions),
        "treasury": treasury,
        "treasury_delta": treasury_delta,
        "bankrupt": bankrupt,
        "strength_ratio_pct": strength_ratio_pct,
    }


def _get_nation_total_strength(world, nation: str) -> int:
    """Sum strength of all non-broken marshals for a nation."""
    total = 0
    for m in world.marshals.values():
        if m.nation == nation and not m.broken:
            total += m.strength
    return int(total)


def _estimate_enemy_strength_from_intel(world, player_nation: str) -> int:
    """
    Estimate total enemy strength using fog-filtered intel only.

    FULL visibility: use exact strength from known_marshals entries.
    PARTIAL/STALE/LAST_KNOWN: use band midpoint estimates.
    UNKNOWN: contributes 0 (we don't know).

    This intentionally underestimates when visibility is low —
    that's the cost of poor intelligence.
    """
    total = 0
    # Track which marshal names we've already counted to avoid doubles
    counted_marshals: set = set()

    for region_name, intel in world.intel.items():
        if intel.visibility == UNKNOWN:
            continue

        for km in intel.known_marshals:
            if km.get("nation") == player_nation:
                continue  # Skip friendly forces
            name = km.get("name", "")
            if name in counted_marshals:
                continue
            counted_marshals.add(name)

            if intel.visibility == FULL and "strength" in km:
                total += int(km["strength"])
            elif "band" in km:
                total += BAND_MIDPOINTS.get(km["band"], 0)
            elif "strength" in km:
                # Frozen STALE snapshot that was originally FULL
                total += int(km["strength"])
            else:
                # No strength data at all — use region-level band
                total += BAND_MIDPOINTS.get(intel.strength_band, 0)

    return int(total)


# ============================================================================
# MARSHAL STATUS
# ============================================================================

def _build_marshal_status(world, player_nation: str) -> List[Dict[str, Any]]:
    """Build the MARSHAL STATUS section — one entry per friendly marshal."""
    result = []
    for marshal in world.marshals.values():
        if marshal.nation != player_nation:
            continue

        status, status_note = _derive_marshal_status(marshal, world)
        trust_val = int(marshal.trust.value) if hasattr(marshal.trust, 'value') else int(getattr(marshal, 'trust', 75))
        morale_val = int(marshal.morale)

        entry = {
            "name": marshal.name,
            "location": marshal.location,
            "strength": int(marshal.strength),
            "status": status,
            "status_note": status_note,
            "trust": trust_val,
            "trust_notable": trust_val < 55 or trust_val > 90,
            "morale": morale_val,
            "morale_warning": morale_val < 60,
        }
        result.append(entry)

    # Sort by strength descending (strongest marshal first)
    result.sort(key=lambda m: m["strength"], reverse=True)
    return result


def _derive_marshal_status(marshal, world) -> tuple:
    """
    Derive display status and note from marshal state.

    Returns (status_key: str, note: str).
    Priority order (highest wins):
    1. broken
    2. retreating
    3. strategic order active
    4. drilling / drilling_locked
    5. fortified
    6. artillery (at rest)
    7. idle_restless (aggressive personality, idle 3+ turns)
    8. awaiting (default)
    """
    if marshal.broken:
        recovery_turn = int(world.current_turn + (4 - marshal.broken_recovery))
        return "broken", f"Reforms T{recovery_turn}."

    if marshal.retreating:
        recovery_turn = int(world.current_turn + (3 - marshal.retreat_recovery))
        return "retreating", f"Recovers T{recovery_turn}."

    if marshal.in_strategic_mode:
        order = marshal.strategic_order
        cmd = order.command_type
        target = order.target
        if cmd == "MOVE_TO":
            return "en_route", f"Moving to {target}."
        elif cmd == "PURSUE":
            return "en_route", f"Pursuing {target}."
        elif cmd == "HOLD":
            return "en_route", f"Holding at {marshal.location}."
        elif cmd == "SUPPORT":
            return "en_route", f"Supporting {target}."
        else:
            return "en_route", f"{cmd} {target}."

    if marshal.drilling or marshal.drilling_locked:
        return "drilling", "Drilling."

    if marshal.fortified:
        return "fortified", f"Fortified at {marshal.location}."

    if marshal.artillery:
        return "artillery", f"Artillery at {marshal.location}."

    personality = getattr(marshal, 'personality', 'balanced')
    if isinstance(personality, str):
        personality_str = personality.lower()
    else:
        personality_str = personality.value if hasattr(personality, 'value') else str(personality).lower()

    idle = getattr(marshal, 'idle_turns', 0)
    if personality_str == "aggressive" and idle >= 3:
        return "idle_restless", f"{idle} turns idle."

    return "awaiting", "Awaiting orders."


# ============================================================================
# INTELLIGENCE
# ============================================================================

def _build_intelligence(world, player_nation: str) -> List[Dict[str, Any]]:
    """
    Build fog-filtered INTELLIGENCE section.

    Iterates over all RegionIntel, extracts enemy marshals from
    known_marshals at PARTIAL+ visibility. Deduplicates by marshal name
    (keep the best-visibility sighting).
    """
    # Collect sightings: marshal_name -> best sighting dict
    sightings: Dict[str, Dict[str, Any]] = {}

    visibility_rank = {FULL: 4, PARTIAL: 3, STALE: 2, LAST_KNOWN: 1, UNKNOWN: 0}

    for region_name, intel in world.intel.items():
        if intel.visibility == UNKNOWN:
            continue

        for km in intel.known_marshals:
            if km.get("nation") == player_nation:
                continue
            name = km.get("name", "Unknown")
            vis = intel.visibility
            rank = visibility_rank.get(vis, 0)

            existing = sightings.get(name)
            if existing and visibility_rank.get(existing["visibility"], 0) >= rank:
                continue  # Already have better intel

            # Build strength display
            if vis == FULL and "strength" in km:
                strength_display = f"{int(km['strength']):,}"
            elif "band" in km:
                strength_display = km["band"]
            elif "strength" in km:
                # Frozen STALE that was originally FULL
                strength_display = f"~{int(km['strength']):,}"
            else:
                strength_display = intel.strength_band

            sightings[name] = {
                "name": name,
                "location": region_name,
                "strength_display": strength_display,
                "visibility": vis,
                "intel_turn": int(intel.last_updated_turn),
            }

    # Sort: FULL first, then PARTIAL, etc.
    result = sorted(
        sightings.values(),
        key=lambda s: visibility_rank.get(s["visibility"], 0),
        reverse=True,
    )
    return result


# ============================================================================
# TURN EVENTS (absorbed from tactical events)
# ============================================================================

# Event types relevant to the dispatch (player-visible turn events).
# Acts as a WHITELIST: only these event types appear in the TURN EVENTS section.
_DISPATCH_EVENT_TYPES = {
    # Warning severity
    "supply_attrition", "bankruptcy_desertion",
    "occupation_abandoned", "cavalry_stance_forced",
    "cavalry_fortify_forced", "fortify_decayed",
    "fortify_collapsed", "counter_punch_expired",
    "capital_proximity_alert", "auto_glorious_charge",
    "reckless_move",
    # Good severity
    "construction_complete", "occupation_complete",
    "drill_complete", "retreat_recovery",
    "garrison_regen", "broken_recovered",
    # Info severity (no special highlight)
    "occupation_continues", "drill_locked", "drill_started",
    "fortify_strengthened", "fortify_stable",
    "broken_recovery", "reckless_no_target",
}


def _build_turn_events(
    tactical_events: List[Dict], player_nation: str
) -> List[Dict[str, str]]:
    """
    Build the TURN EVENTS section from tactical events.

    Filters to player-relevant events and produces short one-liner messages.
    Each entry has 'message' (str) and 'severity' ('info' | 'warning' | 'good').
    """
    result = []
    for event in tactical_events:
        event_type = event.get("type", "")
        msg = event.get("message", "")
        if not msg:
            continue

        # Whitelist filter: only dispatch-relevant event types
        if event_type not in _DISPATCH_EVENT_TYPES:
            continue

        # Filter: only show events relevant to player nation
        event_nation = event.get("nation")
        marshal_name = event.get("marshal", "")
        if event_nation and event_nation != player_nation:
            continue  # Skip enemy attrition etc.

        severity = "info"
        if event_type in ("supply_attrition", "bankruptcy_desertion",
                          "occupation_abandoned", "cavalry_stance_forced",
                          "cavalry_fortify_forced", "fortify_decayed",
                          "fortify_collapsed", "counter_punch_expired",
                          "capital_proximity_alert", "auto_glorious_charge",
                          "reckless_move", "reckless_no_target"):
            severity = "warning"
        elif event_type in ("construction_complete", "occupation_complete",
                            "drill_complete", "retreat_recovery",
                            "garrison_regen", "broken_recovered"):
            severity = "good"

        result.append({"message": msg, "severity": severity})

    return result


# ============================================================================
# BERTHIER'S CLOSING NOTE
# ============================================================================

def _pick_berthier_note(
    world,
    player_nation: str,
    marshals_data: List[Dict],
    situation: Dict,
) -> str:
    """
    Pick the highest-priority Berthier closing note.

    Priority (highest first):
    1. Marshal broken
    2. Bankrupt
    3. Treasury negative delta
    4. Aggressive marshal idle 4+ turns
    5. All marshals at full readiness
    6. Default
    """
    # 1. Broken marshal — pick strongest broken one
    broken = [m for m in marshals_data if m["status"] == "broken"]
    if broken:
        worst = max(broken, key=lambda m: m["strength"])
        return (
            f"Sire, {worst['name']} requires time to reform "
            f"- he cannot be counted upon."
        )

    # 2. Bankrupt
    if situation.get("bankrupt"):
        return "Our finances are dire, Sire. The treasury is exhausted."

    # 3. Treasury bleeding
    delta = situation.get("treasury_delta", 0)
    if delta < 0:
        return f"Our finances strain, Sire. The treasury bleeds {abs(delta)}g this turn."

    # 4. Aggressive marshal idle 4+ turns
    restless = [m for m in marshals_data if m["status"] == "idle_restless"]
    for m in restless:
        # idle_restless triggers at 3+, but Berthier note at 4+ (escalation)
        # We can check the note text for "4 turns" but safer to just check
        # if any restless marshal exists and note mentions 4+
        note = m.get("status_note", "")
        # Parse turns from note: "N turns idle."
        try:
            turns = int(note.split()[0])
            if turns >= 4:
                return f"{m['name']} grows impatient, Sire. He will require action soon."
        except (ValueError, IndexError):
            pass

    # 5. All marshals at full readiness (no broken, retreating, drilling)
    non_ready_statuses = {"broken", "retreating", "drilling"}
    all_ready = all(m["status"] not in non_ready_statuses for m in marshals_data)
    if all_ready and marshals_data:
        return "Your armies stand ready, Sire. The initiative is ours."

    # 6. Default
    return "Your orders, Sire."
