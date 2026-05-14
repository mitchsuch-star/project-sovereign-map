"""
Morning Dispatch — Berthier's turn-start briefing (Phase 6.5)

Builds a structured dict for Godot to render as terminal output at turn start.
All values int()-wrapped per CLAUDE.md rule: "All numbers to Godot: int()".

Fog-filtered: enemy intel uses RegionIntel visibility, never raw marshal data.
"""

from typing import Dict, List, Optional, Any

from backend.nation_config import get_player_nation
from backend.models.intel import (
    FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN,
    get_strength_band,
)
from backend.game_logic.commitments_routing import (
    COMMITMENTS_ROUTES,
    commitments_priority,
    format_commitments_notice,
)
from backend.game_logic.settlement_presentation import (
    SETTLEMENT_PRIMARY_BEAT_CAP,
    cap_settlement_dispatch_lines,
    compose_digest_oneliner,
    compose_summary_oneliner,
    is_settlement_event_type,
    is_settlement_event_visible,
    settlement_priority,
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


def build_morning_dispatch(world, tactical_events: Optional[List] = None,
                           lapsed_offers: Optional[List] = None) -> Dict[str, Any]:
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
        lapsed_offers: Optional list of lapse info dicts from turn-end.
            Each has nation, offer_type, proposal_type.

    Returns:
        Dict with turn, situation, marshals, intelligence, turn_events,
        berthier_note. All numeric values int()-wrapped.
    """
    # TODO: Post-EA — thread player_nation from world state
    player_nation = get_player_nation(world)

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

    # ════════════════════════════════════════════════════════════
    # V2-85: TURN-LIMIT WARNINGS — alert player as campaign nears end
    # ════════════════════════════════════════════════════════════
    turn_limit_warning = _build_turn_limit_warning(world, player_nation)
    if turn_limit_warning:
        dispatch["turn_limit_warning"] = turn_limit_warning

    defeat_imminent_warning = _build_defeat_imminent_warning(world, player_nation)
    if defeat_imminent_warning:
        dispatch["defeat_imminent_warning"] = defeat_imminent_warning

    # Talleyrand's Report — proactive diplomatic suggestions (Session 4)
    dispatch["talleyrand_report"] = _build_talleyrand_report(world, player_nation)

    # ════════════════════════════════════════════════════════════
    # SESSION 6: Talleyrand sabotage discovery + override notes + redemption
    # ════════════════════════════════════════════════════════════
    dispatch["talleyrand_discovery"] = None
    dispatch["talleyrand_override_note"] = None
    dispatch["talleyrand_redemption"] = None

    _check_talleyrand_session6(dispatch, world, player_nation)

    # Coalition status (Session 7)
    dispatch["coalition_status"] = _build_coalition_section(world, player_nation)

    # WPS-A: Active war objectives
    war_objective_lines = _build_war_objective_section(world, player_nation)
    if war_objective_lines:
        dispatch["war_objectives"] = war_objective_lines

    # BPH-D §11.3: Peace settlement section from previous turn's ratifications
    peace_settlements = _build_peace_settlement_section(world)
    if peace_settlements:
        dispatch["peace_settlements"] = peace_settlements

    # Diplomatic events (Session 8D)
    diplomatic_events = _build_diplomatic_events_section(world, player_nation)

    # S2: Merge significant relation change events
    relation_events = _build_relation_change_events(world, player_nation)
    if relation_events:
        diplomatic_events.extend(relation_events)

    dispatch["diplomatic_events"] = diplomatic_events

    # Lapsed offers from previous turn-end
    if lapsed_offers:
        dispatch["lapsed_offers"] = [
            {
                "nation": offer["nation"],
                "proposal_type": (offer.get("proposal_type") or "proposal").replace("_", " "),
            }
            for offer in lapsed_offers
        ]

    pending_envoys = [
        {
            "nation": item.get("source_nation", "?"),
            "proposal_type": str(item.get("proposal_type", "proposal")).replace("_", " "),
            "state": item.get("state", "WAITING"),
        }
        for item in world.dialogue_manager.get_mailbox_items()
    ]
    if pending_envoys:
        dispatch["pending_envoy_count"] = int(len(pending_envoys))
        dispatch["pending_envoys"] = pending_envoys

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

    # Trade income from diplomatic states (read-only calculation)
    from backend.game_logic.diplomacy import calculate_trade_income
    trade_income_all = calculate_trade_income(world)
    trade_income = int(trade_income_all.get(player_nation, 0))

    treasury_delta = int(income + trade_income - upkeep)

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

    # Authority — global player stat (V2b)
    authority = int(world.authority_tracker.authority) if hasattr(world, 'authority_tracker') else 100
    if authority >= 80:
        authority_label = "Strong"
    elif authority >= 50:
        authority_label = "Normal"
    else:
        authority_label = "Weak"

    return {
        "player_regions": int(player_regions),
        "enemy_regions": int(enemy_regions),
        "treasury": treasury,
        "treasury_delta": treasury_delta,
        "trade_income": trade_income,
        "bankrupt": bankrupt,
        "strength_ratio_pct": strength_ratio_pct,
        "authority": int(authority),
        "authority_label": authority_label,
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
                # Frozen STALE snapshot — use band midpoint estimate
                band = get_strength_band(int(km["strength"]))
                total += BAND_MIDPOINTS.get(band, 0)
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
                # Frozen STALE snapshot — use band, not exact number
                strength_display = get_strength_band(int(km["strength"]))
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
        if not event_nation:
            continue  # Skip events with no nation (safety net)
        if event_nation != player_nation:
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


# ============================================================================
# V2-85: TURN-LIMIT WARNINGS
# ============================================================================

def _build_turn_limit_warning(world, player_nation: str) -> Optional[Dict[str, Any]]:
    """Build turn-limit warning for the Morning Dispatch.

    Fires at 5/2/1 turns remaining (post-advance: remaining == 4/1/0).
    Also creates a notification for the notification bar.

    Returns warning dict or None.
    """
    from backend.models.world_state import VICTORY_REGION_FRACTION

    current = int(world.current_turn)
    max_turns = int(world.max_turns)
    remaining = max_turns - current

    # 4C-2: Thresholds adjusted for post-advance_turn timing.
    # When dispatch builds, current_turn is already the NEW turn.
    # "5 turns remain" means 5 playable turns left → remaining == 4 after advance.
    if remaining > 4:
        return None

    total_regions = len(world.regions)
    threshold = max(1, int(total_regions * VICTORY_REGION_FRACTION))
    player_regions = len(world.get_player_regions())

    if remaining == 4:
        message = "The campaign enters its final phase — 5 turns remain."
        severity = "warning"
    elif remaining == 1:
        message = (
            f"Only 2 turns remain. France must control {threshold} regions for victory. "
            f"Current: {player_regions}/{threshold}."
        )
        severity = "warning"
    elif remaining == 0:
        message = (
            f"FINAL TURN. France must control {threshold} regions for victory. "
            f"Current: {player_regions}/{threshold}."
        )
        severity = "critical"
    elif remaining < 0:
        message = (
            f"The campaign has reached its conclusion. "
            f"France controls {player_regions}/{threshold} required regions."
        )
        severity = "critical"
    else:
        # remaining is 2 or 3 — no warning at these turns
        return None

    # Fire notification
    from backend.notifications import (
        create_notification, NotificationPriority, TURN_LIMIT_WARNING,
    )
    # remaining is post-advance; actual playable turns = remaining + 1 (includes current)
    actual_turns = remaining + 1 if remaining > 0 else 0
    world.notifications.add(create_notification(
        TURN_LIMIT_WARNING,
        NotificationPriority.HIGH,
        f"{actual_turns} turns remain" if actual_turns > 0 else "Final turn",
        message,
        current,
    ))

    return {
        "message": message,
        "severity": severity,
        "turns_remaining": int(remaining),
        "player_regions": int(player_regions),
        "victory_threshold": int(threshold),
    }


def _build_defeat_imminent_warning(world, player_nation: str) -> Optional[Dict[str, Any]]:
    """Build deterministic near-defeat warning aligned with live loss rules."""
    from backend.game_logic.turn_manager import get_defeat_imminent_state
    from backend.notifications import (
        create_notification, NotificationPriority, DEFEAT_IMMINENT_WARNING,
    )

    world.notifications.dismiss_by_type(DEFEAT_IMMINENT_WARNING)

    if getattr(world, "player_nation", player_nation) != player_nation:
        return None

    warning = get_defeat_imminent_state(world)
    if not warning:
        return None

    priority = (
        NotificationPriority.CRITICAL
        if warning["severity"] == "critical"
        else NotificationPriority.HIGH
    )
    world.notifications.add(create_notification(
        DEFEAT_IMMINENT_WARNING,
        priority,
        warning["notification_title"],
        warning["message"],
        int(world.current_turn),
        details={
            "living_marshal_count": int(warning["living_marshal_count"]),
            "living_marshals": list(warning["living_marshals"]),
            "controlled_region_count": int(warning["controlled_region_count"]),
            "controlled_regions": list(warning["controlled_regions"]),
        },
    ))

    return {
        "message": warning["message"],
        "severity": warning["severity"],
        "living_marshal_count": int(warning["living_marshal_count"]),
        "living_marshals": list(warning["living_marshals"]),
        "controlled_region_count": int(warning["controlled_region_count"]),
        "controlled_regions": list(warning["controlled_regions"]),
    }


# ============================================================================
# TALLEYRAND'S REPORT — Proactive diplomatic suggestions (Phase 8 Session 4)
# ============================================================================

# Trigger priority levels
_PROACTIVE_TRIGGERS = [
    # (trigger_type, priority, cooldown_turns, checker_function)
    # Priority: lower = higher priority. Max 2 suggestions per dispatch.
]


def _build_talleyrand_report(world, player_nation: str) -> List[Dict[str, str]]:
    """
    Build Talleyrand's Report section for the Morning Dispatch.

    Returns list of 0-2 observation dicts with 'message' and 'trigger_type'.
    Suppressed entirely if an incoming AI proposal is pending this turn.

    Trigger conditions (from CONV_DESIGN §5d):
    1. Acceptance crossed 50 threshold for a nation
    2. War score shifted ≥15 in one turn
    3. Vassal loyalty warnings (Phase 8 Session 5)
    4. Relation threshold crossed (-40, -20, 0, +20, +40)
    5. No diplomatic action for 3+ turns
    """
    # Suppression: if incoming AI proposal pending, Talleyrand is busy
    pending = getattr(world, 'pending_diplomatic_dialogue', None)
    if pending and pending.get("type") == "incoming_proposal":
        return []

    observations = []
    cooldowns = getattr(world, 'proactive_suggestion_cooldowns', {})

    # Helper: check if a trigger is on cooldown
    def _on_cooldown(nation: str, trigger_type: str) -> bool:
        key = f"{nation}|{trigger_type}"
        return cooldowns.get(key, 0) > 0

    def _set_cooldown(nation: str, trigger_type: str, turns: int) -> None:
        key = f"{nation}|{trigger_type}"
        cooldowns[key] = turns

    # R91: Map current diplomatic state to the next upgrade proposal type
    UPGRADE_MAP = {
        "WAR": "peace",
        "ARMISTICE": "peace",
        "PEACE": "open_borders",
        "OPEN_BORDERS": "non_aggression",
        "NON_AGGRESSION": "defensive_alliance",
        "DEFENSIVE_ALLIANCE": "alliance",
    }

    from backend.game_logic.diplomatic_dialogue import get_known_nations
    active = set(world.get_active_nations())  # DLF-11
    known_nations = sorted(n for n in get_known_nations(world) if n in active)

    for nation in known_nations:
        if len(observations) >= 2:
            break

        diplo_key = world._make_diplo_key(player_nation, nation)
        state = world.get_diplomatic_state(player_nation, nation)
        relation = world.nation_relations.get(diplo_key, 0)

        # ── Trigger 1: Acceptance crossed 50 (diplomatic opportunity) ──
        if not _on_cooldown(nation, "acceptance_crossed") and state != "WAR":
            try:
                from backend.game_logic.diplomacy import calculate_acceptance
                upgrade_type = UPGRADE_MAP.get(state, "non_aggression")
                hypothetical = {
                    "type": upgrade_type,
                    "proposer_nation": player_nation,
                    "target_nation": nation,
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                }
                result = calculate_acceptance(hypothetical, world)
                if result["score"] >= 50:
                    observations.append({
                        "message": (
                            f"Sire, I believe {nation} may be ready to discuss "
                            f"improved relations. The diplomatic winds favor us."
                        ),
                        "trigger_type": "acceptance_crossed",
                        "target_nation": nation,
                        "priority": 2,
                        "elaborate_type": "proposal_options",
                    })
                    _set_cooldown(nation, "acceptance_crossed", 10)
            except Exception:
                import logging
                logging.getLogger(__name__).exception("Error in acceptance trigger for %s", nation)

        # ── Trigger 2: War score shift ≥15 (per-turn delta) ──
        if not _on_cooldown(nation, "war_score_shift") and state == "WAR":
            raw_score = world.war_scores.get(diplo_key, 0)
            prev_raw = getattr(world, 'previous_war_scores', {}).get(diplo_key, 0)
            # Sign adjust for France perspective
            parts = diplo_key.split("|")
            if len(parts) == 2 and parts[0] == nation:
                war_score = -raw_score
                prev_score = -prev_raw
            else:
                war_score = raw_score
                prev_score = prev_raw
            delta = war_score - prev_score
            if abs(delta) >= 15:
                direction = "in our favor" if delta > 0 else "against us"
                observations.append({
                    "message": (
                        f"The war with {nation} has shifted dramatically {direction}. "
                        f"War score stands at {int(war_score)}. "
                        f"This changes our diplomatic options significantly."
                    ),
                    "trigger_type": "war_score_shift",
                    "target_nation": nation,
                    "priority": 1,
                    "elaborate_type": "advisory",
                })
                _set_cooldown(nation, "war_score_shift", 3)

        # ── Trigger 3: Vassal loyalty warnings (Phase 8 Session 5) ──
        if (nation in getattr(world, 'vassals', {})
                and not _on_cooldown(nation, "vassal_loyalty")):
            vassal_state = world.vassals[nation]
            if vassal_state.get("lord") == player_nation:
                loyalty = vassal_state.get("loyalty", 100)
                if loyalty < 20:
                    observations.append({
                        "message": (
                            f"Sire, our vassal {nation} grows dangerously restless. "
                            f"Loyalty stands at {int(loyalty)}. "
                            f"{'Rebellion is imminent!' if loyalty < 10 else 'Urgent intervention may be required.'}"
                        ),
                        "trigger_type": "vassal_loyalty",
                        "target_nation": nation,
                        "priority": 1 if loyalty < 10 else 2,
                        "elaborate_type": "advisory",
                    })
                    _set_cooldown(nation, "vassal_loyalty", 3)
                elif loyalty < 35:
                    observations.append({
                        "message": (
                            f"Sire, Talleyrand notes growing discontent in {nation}. "
                            f"Loyalty stands at {int(loyalty)}."
                        ),
                        "trigger_type": "vassal_loyalty",
                        "target_nation": nation,
                        "priority": 4,
                        "elaborate_type": "advisory",
                    })
                    _set_cooldown(nation, "vassal_loyalty", 3)

        # ── Trigger 4: Relation threshold CROSSED ──
        thresholds = [-40, -20, 0, 20, 40]
        if not _on_cooldown(nation, "relation_threshold"):
            previous = world.previous_nation_relations.get(diplo_key, relation)
            for threshold in thresholds:
                crossed_up = previous < threshold <= relation
                crossed_down = previous >= threshold > relation
                if crossed_up or crossed_down:
                    direction_word = "improved" if crossed_up else "deteriorated"
                    observations.append({
                        "message": (
                            f"Relations with {nation} have {direction_word} "
                            f"past {threshold} to {int(relation)}. "
                            f"{'This opens new diplomatic possibilities.' if crossed_up else 'Caution may be warranted.'}"
                        ),
                        "trigger_type": "relation_threshold",
                        "target_nation": nation,
                        "priority": 3,
                        "elaborate_type": "advisory" if crossed_down else "proposal_options",
                    })
                    _set_cooldown(nation, "relation_threshold", 5)
                    break  # One threshold per nation per dispatch

    # ── Trigger 5: No diplomatic action for 3+ turns ──
    if len(observations) < 2 and not _on_cooldown("global", "idle_nudge"):
        mission = getattr(world, 'active_diplomatic_mission', None)
        transit = getattr(world, 'proposal_in_transit', None)
        talleyrand_state = getattr(world, 'talleyrand_state', 'IDLE')

        if talleyrand_state == "IDLE" and not mission and not transit:
            # Check if player has taken any diplomatic action recently
            # (Simple heuristic: Talleyrand is idle = no recent action)
            if world.current_turn >= 4:  # Don't nag on early turns
                observations.append({
                    "message": (
                        "Sire, the diplomatic front has been quiet. Perhaps too quiet. "
                        "Shall I assess our options?"
                    ),
                    "trigger_type": "idle_nudge",
                    "target_nation": "",
                    "priority": 5,
                    "elaborate_type": "proposal_options",
                })
                _set_cooldown("global", "idle_nudge", 5)

    # Sort by priority (lower = more important), cap at 2
    observations.sort(key=lambda o: o.get("priority", 99))
    result = observations[:2]

    # Store cooldowns back
    world.proactive_suggestion_cooldowns = cooldowns

    return result


# ============================================================================
# SESSION 6: Talleyrand Defiance Discovery + Override Notes + Redemption
# ============================================================================

def _check_talleyrand_session6(dispatch: Dict, world, player_nation: str) -> None:
    """Check for Talleyrand sabotage discovery, override notes, and redemption.

    Modifies dispatch dict in place. Sets fields:
    - talleyrand_discovery: confrontation dialogue dict if discovery fires
    - talleyrand_override_note: string if recent override outcome

    Args:
        dispatch: The dispatch dict being built
        world: WorldState
        player_nation: The active player nation
    """
    diplomats = getattr(world, 'diplomats', {})
    talleyrand = diplomats.get(player_nation)
    if not talleyrand:
        return

    # ── 1. Sabotage Discovery Check ──
    sabotage = getattr(world, 'pending_talleyrand_sabotage', None)
    if sabotage and not sabotage.get("discovered"):
        from backend.commands.diplomatic_defiance import (
            check_sabotage_discovery, build_confrontation_dialogue,
        )
        if check_sabotage_discovery(sabotage, world):
            sabotage["discovered"] = True
            world.pending_talleyrand_sabotage = sabotage

            # Build confrontation dialogue and set it as pending
            confrontation = build_confrontation_dialogue(sabotage, talleyrand)
            confrontation["turn_created"] = int(world.current_turn)
            dispatch["talleyrand_discovery"] = confrontation

            # Also set on world for the dialogue system to pick up
            world.dialogue_manager.push(confrontation)

            # Notification: sabotage discovered (Session 8C)
            from backend.notifications import (
                create_notification, NotificationPriority, SABOTAGE_DISCOVERED,
            )
            target = sabotage.get("target_nation", "unknown")
            defiance_type = sabotage.get("defiance_type", "unknown")
            # BUGFIX: Translate raw defiance_type keys to human-readable strings.
            # Raw keys like "ap_downgrade" and "stalled" must not reach the player.
            # See BUGFIX_PLAN_PROPOSAL_FLOW.md.
            _DEFIANCE_TYPE_DISPLAY = {
                "stalled": "Delayed Delivery",
                "ap_downgrade": "Reduced Concessions",
                "unit_overpay": "Inflated Demands",
                "softened": "Softened Terms",
                "hardened": "Hardened Terms",
                "unknown": "Modified Terms",
            }
            display_type = _DEFIANCE_TYPE_DISPLAY.get(defiance_type, "Modified Terms")
            world.notifications.add(create_notification(
                SABOTAGE_DISCOVERED,
                NotificationPriority.HIGH,
                "Sabotage Discovered!",
                f"Talleyrand altered your proposal to {target} ({display_type}).",
                int(world.current_turn),
            ))

            # Set popup data for Godot (Session 8C)
            original = sabotage.get("original_proposal", {})
            modified = sabotage.get("modified_proposal", {})
            world.diplomatic_sabotage_popup = {
                "target_nation": target,
                "defiance_type": defiance_type,
                "ordered_summary": sabotage.get("original_summary", str(original)),
                "delivered_summary": sabotage.get("modified_summary", str(modified)),
                "authority_bonus_if_confronted": int(5),
                "authority_penalty_if_overlooked": int(3),
            }

            # Dispatch event (Session 8D) — use translated display_type
            queue_dispatch_event(world, "diplomatic_sabotage_discovered",
                                {"nation": target, "change_description": display_type},
                                "always")

            # Campaign log entry
            world.log_event({
                "type": "diplomatic_discrepancy",
                "message": f"Talleyrand altered your proposal to {target}.",
                "turn": int(world.current_turn),
                "nation": player_nation,
            })

    # ── 2. Override History Note ──
    from backend.commands.diplomatic_defiance import get_override_dispatch_note
    override_note = get_override_dispatch_note(world)
    if override_note:
        dispatch["talleyrand_override_note"] = override_note

    # ── 3. Redemption Event — REMOVED (PL-23: trust system deleted) ──


def _build_war_objective_section(world, player_nation: str) -> List[Dict]:
    """WPS-A: Build war objective status lines for the Morning Dispatch."""
    from backend.game_logic.diplomacy import (
        OBJECTIVE_TYPE_DISPLAY, SETTLEMENT_TIER_DISPLAY,
        TICKING_RATES, get_settlement_tier, get_war_score_for,
    )

    lines = []
    war_objectives = getattr(world, 'war_objectives', {})

    for diplo_key, nation_objs in war_objectives.items():
        player_obj = nation_objs.get(player_nation)
        if not player_obj or player_obj.get("concluded_turn") is not None:
            continue

        obj_type = player_obj.get("type", "")
        target_nation = player_obj.get("target_nation", "Unknown")
        target_regions = player_obj.get("target_regions", [])
        accumulated = int(player_obj.get("accumulated_ticking", 0))
        rate = int(TICKING_RATES.get(obj_type, 0))
        type_display = OBJECTIVE_TYPE_DISPLAY.get(obj_type, obj_type)

        held_regions = []
        for rname in target_regions:
            if rname in world.regions:
                if world.regions[rname].controller == player_nation:
                    held_regions.append(rname)

        region_str = ", ".join(target_regions) if target_regions else "unknown"
        held_str = "HELD" if held_regions else "not held"
        tick_str = f"+{rate}/turn" if rate > 0 else ""

        line_text = f"War Purpose: {type_display} vs {target_nation} — {region_str} [{held_str}]"
        if accumulated > 0:
            line_text += f" (ticking: +{accumulated}{', ' + tick_str if tick_str else ''})"

        score = int(get_war_score_for(world, player_nation, target_nation))
        tier = get_settlement_tier(score)
        tier_display = SETTLEMENT_TIER_DISPLAY.get(tier, tier)
        line_text += f"  |  Settlement: {tier_display} ({score:+d})"

        lines.append({
            "text": line_text,
            "target_nation": target_nation,
            "objective_type": obj_type,
        })

    return lines


def _build_peace_settlement_section(world) -> List[Dict]:
    """BPH-D §11.3: Build peace settlement summaries for the Morning Dispatch.

    Returns entries from the ratification log that were signed the previous turn.
    """
    from backend.models.region import NATION_CAPITALS

    previous_turn = int(world.current_turn) - 1
    settlements = []
    for entry in getattr(world, 'peace_ratification_log', []):
        if int(entry.get("turn", 0)) != previous_turn:
            continue
        if entry.get("new_state", "PEACE") != "PEACE":
            continue
        dur = entry.get("war_duration_turns", 0)
        target = entry.get("target_nation", "Unknown")
        target_capital = entry.get("target_capital") or NATION_CAPITALS.get(target, target)
        outcome = entry.get("war_outcome", "")
        gained = entry.get("territory_gained", [])
        score = entry.get("final_war_score", 0)

        headline = f"The Treaty of {target_capital}"
        if entry.get("previous_state") == "ARMISTICE":
            detail_parts = [
                f"{world.player_nation} and {target} have converted the armistice into peace",
            ]
        else:
            detail_parts = [
                f"{world.player_nation} and {target} have concluded peace"
                f" after {dur} turn{'s' if dur != 1 else ''} of war",
            ]
        if gained:
            detail_parts.append(f"{world.player_nation} gained {', '.join(gained)}")
        detail_parts.append(f"Final war score: {'+' if score > 0 else ''}{score}")

        # WPS-D §14.5: Surface forced alliance and liberation in dispatch
        terms_ratified = entry.get("terms_ratified", [])
        for term_label in terms_ratified:
            term_lower = term_label.lower()
            if "forced alliance" in term_lower or "enters alliance" in term_lower:
                detail_parts.append(f"{target} enters forced alliance with {world.player_nation}")
            elif "liberated" in term_lower:
                detail_parts.append(term_label)

        settlements.append({
            "headline": headline,
            "detail": ". ".join(detail_parts) + ".",
            "war_outcome": outcome,
            "target_nation": target,
        })
    return settlements


def _build_coalition_section(world, player_nation: str) -> Optional[Dict]:
    """Build coalition status section for Morning Dispatch (COALITION_SPEC §9c).

    Returns None if threat < 30 (nothing to show).
    """
    from backend.game_logic.coalition import (
        get_threat_tier, get_qualifying_nations, is_coalition_active,
        THREAT_TENSION_MIN,
    )

    threat = int(world.threat_level)
    if threat < THREAT_TENSION_MIN:
        return None

    tier = get_threat_tier(threat)
    section = {
        "threat_level": threat,
        "tier": tier,
        "sources": [s.copy() for s in world.threat_sources_this_turn],
    }

    # Brewing status
    if world.coalition_brewing:
        brewing = world.coalition_brewing
        section["brewing"] = {
            "qualifying_nations": brewing.get("qualifying_nations", []),
            "turns_remaining": int(brewing.get("turns_remaining", 0)),
        }

    # Active coalition details
    if is_coalition_active(world):
        from backend.game_logic.diplomatic_ledger import _get_nation_visibility, _format_army_strength
        coalition = world.active_coalition
        members_info = []
        for member in coalition.get("members", []):
            member_strength = sum(
                m.strength for m in world.marshals.values()
                if m.nation == member and m.strength > 0
            )
            vis = _get_nation_visibility(member, world)
            strength_display = _format_army_strength(member_strength, vis)
            partial_vis = vis in (FULL, PARTIAL)
            members_info.append({
                "nation": member,
                "war_exhaustion": int(world.war_exhaustion.get(member, 0)) if partial_vis else 0,
                "strength_display": strength_display,
                "strength": int(member_strength) if vis == FULL else 0,
                "gold": int(world.nation_gold.get(member, 0)) if vis == FULL else 0,
            })

        section["active_coalition"] = {
            "name": coalition.get("name", ""),
            "leader": coalition.get("leader", ""),
            "posture": coalition.get("strategic_posture", "defensive"),
            "formed_turn": int(coalition.get("formed_turn", 0)),
            "members": members_info,
        }

    # Qualifying nations (if not brewing/active, show who would join)
    if not world.coalition_brewing and not is_coalition_active(world):
        qualifying = get_qualifying_nations(world)
        if qualifying:
            section["qualifying_nations"] = qualifying

    return section


# ============================================================================
# SESSION 8D: DIPLOMATIC EVENTS DISPATCH SECTION
# ============================================================================

# Event text templates — keyed by event type
_DIPLOMATIC_EVENT_TEMPLATES = {
    "diplomatic_proposal_sent": "Talleyrand has departed for the {nation} court.",
    "diplomatic_proposal_returned": "Talleyrand returns from {nation} with a response.",
    "diplomatic_sabotage_discovered": "Talleyrand altered your proposal to {nation}. He {change_description}.",
    "diplomatic_treaty_signed": "{nation_a} and {nation_b} have signed a {treaty_type}.",
    "diplomatic_treaty_broken": "{nation} has broken the {treaty_type}.",
    "diplomatic_war_declared": "{nation} has declared war on {target}.",
    "diplomatic_vassal_unrest": "Talleyrand reports unrest in {nation}.",
    "diplomatic_vassal_rebellion_imminent": "{nation} is on the verge of rebellion!",
    "diplomatic_vassal_rebellion": "{nation} has rebelled!",
    "diplomatic_ai_proposal": "A {nation} envoy has arrived with a proposal.",
    "diplomatic_mission_progress": "Talleyrand's efforts in {nation} continue. Relations now at {value}.",
    "diplomatic_mission_completed": "Talleyrand has completed his mission in {nation}.",
    "diplomatic_mission_paused": "Talleyrand's diplomatic efforts curtailed — insufficient resources.",
    "diplomatic_mission_cancelled": "Talleyrand's efforts in {nation} have collapsed.",
    "diplomatic_feasibility_report": "Talleyrand assesses: {difficulty_tier}. {hint}",
    "diplomatic_alliance_cascade": "{nation} enters the war via alliance with {ally}.",
    "diplomatic_offensive_cascade": "{nation} has joined {aggressor}'s war against {target}, honoring their alliance.",
    "diplomatic_vassal_courting": "Talleyrand reports {enemy} agents in {vassal_capital}.",
    "diplomatic_continental_system": "{nation} has {action} the Continental System.",
    "diplomatic_carved_vassal_created": "The {carved_name} has been established under French protection.",
    "diplomatic_carved_vassal_dissolved": "The {carved_name} has ceased to exist.",
    "diplomatic_defection_cascade": "The empire trembles — multiple vassals are wavering!",
    "diplomatic_ai_ai_treaty": "Talleyrand reports: {nation_a} and {nation_b} have signed a {treaty_type}.",
    "diplomatic_treaty_payment_failed": "{from_nation} cannot meet treaty obligations to {to_nation} ({amount_paid}/{amount_due} gold paid).",
    "diplomatic_auto_downgrade": "Relations between {nation_a} and {nation_b} have collapsed: {from_state} → {to_state}.",
    "diplomatic_coalition_formed": "A coalition has formed against France! Members: {member_list}.",
    "diplomatic_coalition_dissolved": "The coalition against France has dissolved.",
    "diplomatic_coalition_brewing": "Talleyrand warns: a coalition may be forming against France.",
    "balance_of_europe_shifted": "The balance of Europe shifts around {label}.",
    "diplomatic_dp_regen": "Talleyrand reports: {dp} diplomatic points available ({breakdown}).",
    "diplomatic_we_threshold": "War exhaustion grows — {nation} nears breaking point (exhaustion: {we}).",
    "diplomatic_relation_shift": "Relations with {nation} have {direction} significantly ({delta} this turn).",
    "diplomatic_armistice_expired_peace": "The armistice between {nation_a} and {nation_b} has concluded. Peace declared.",
    "diplomatic_armistice_expired_war": "The armistice between {nation_a} and {nation_b} has collapsed. War resumes!",
    "hard_reject_posture_triggered": "{victim_nation} has closed the chancery to {perpetrator_nation}.",
    "hard_reject_posture_cleared": "{victim_nation} has reopened deeper diplomacy with {perpetrator_nation}.",
    # Memory and Pressure v2.4.3 — Make Amends. Commitments routing owns the
    # final notice copy; this template is the dispatch fallback.
    "amends_offered": "{actor_nation} has offered amends to {target_nation}.",
    # DG-4 §8.8 — defender-side refusal of a legal, non-impossible call.
    # Commitments routing owns the rail copy; this template is the dispatch
    # fallback.
    "call_to_arms_refused_defensive": (
        "{breaker} has refused the defensive call from {victim}."
    ),
    "call_to_arms_refused_offensive": (
        "{breaker} has refused the offensive call from {victim}."
    ),
    "call_to_arms_honored_costly": (
        "{honorer} has honored a costly defensive call from {victim}."
    ),
    "oathbreaker_posture_triggered": (
        "{nation} is marked as an oathbreaker after repeated refusals."
    ),
    "oathbreaker_posture_cleared": (
        "{nation}'s oathbreaker posture has cleared."
    ),
    "commitment_paradox_resolved": (
        "In a crisis of commitments, {player_nation} chose {chosen_nation} over {spurned_nation}."
    ),
    "nation_eliminated": "{nation} has been eliminated from the war.",
    # Peace Deals BPH-A + BPH-D
    "peace_ratified": "Peace ratified between {proposer_nation} and {target_nation}.",
    # WB-B — war bargain lifecycle
    "bargain_ratified": "{promiser} and {beneficiary} ratified a bargain against {target_enemy}: French priority claim on {claim_region}.",
    "bargain_triggered": "{beneficiary} joins against {target_enemy}; the bargain over {claim_region} is now active.",
    "bargain_fulfilled": "{promiser} honored the bargain: {claim_region} secured.",
    "bargain_breached": "{fault_nation} broke the bargain with {beneficiary} over {claim_region}.",
    "bargain_voided": "Bargain with {beneficiary} over {claim_region} lapsed ({end_reason}).",
    "bargain_dormant_notice": "Bargain with {beneficiary} over {claim_region} has been idle for {turns_active} turns.",
    # SC-33 / G2-Slice-9 - recurring settlement gold payment events.
    "settlement_recurring_gold_paid": (
        "{from_nation} paid {amount_paid} gold to {to_nation} on the "
        "settlement of {war_label} ({turns_remaining} turns remaining)."
    ),
    "settlement_recurring_gold_partial": (
        "{from_nation} could only pay {amount_paid}/{amount_due} gold to "
        "{to_nation} on the settlement of {war_label}."
    ),
    "settlement_recurring_gold_completed": (
        "The settlement obligation of {total_amount} gold from "
        "{from_nation} to {to_nation} (for {war_label}) is fulfilled."
    ),
    "settlement_recurring_gold_cancelled": (
        "The recurring settlement payment from {from_nation} to "
        "{to_nation} (for {war_label}) has been cancelled ({reason})."
    ),
}

# Priority mapping: LOW for progress/sent/feasibility; MEDIUM for treaty/system; HIGH for rest
_DIPLOMATIC_EVENT_PRIORITY = {
    "diplomatic_proposal_sent": "LOW",
    "diplomatic_proposal_returned": "HIGH",
    "diplomatic_sabotage_discovered": "HIGH",
    "diplomatic_treaty_signed": "MEDIUM",
    "diplomatic_treaty_broken": "HIGH",
    "diplomatic_war_declared": "HIGH",
    "diplomatic_vassal_unrest": "MEDIUM",
    "diplomatic_vassal_rebellion_imminent": "HIGH",
    "diplomatic_vassal_rebellion": "HIGH",
    "diplomatic_ai_proposal": "HIGH",
    "diplomatic_mission_progress": "LOW",
    "diplomatic_mission_completed": "MEDIUM",
    "diplomatic_mission_paused": "MEDIUM",
    "diplomatic_mission_cancelled": "HIGH",
    "diplomatic_feasibility_report": "LOW",
    "diplomatic_alliance_cascade": "HIGH",
    "diplomatic_offensive_cascade": "HIGH",
    "diplomatic_vassal_courting": "MEDIUM",
    "diplomatic_continental_system": "MEDIUM",
    "diplomatic_carved_vassal_created": "MEDIUM",
    "diplomatic_carved_vassal_dissolved": "HIGH",
    "diplomatic_defection_cascade": "HIGH",
    "diplomatic_ai_ai_treaty": "MEDIUM",
    "diplomatic_treaty_payment_failed": "MEDIUM",
    "settlement_recurring_gold_paid": "LOW",
    "settlement_recurring_gold_partial": "MEDIUM",
    "settlement_recurring_gold_completed": "MEDIUM",
    "settlement_recurring_gold_cancelled": "MEDIUM",
    "diplomatic_auto_downgrade": "MEDIUM",
    "diplomatic_coalition_formed": "HIGH",
    "diplomatic_coalition_dissolved": "MEDIUM",
    "diplomatic_coalition_brewing": "MEDIUM",
    "balance_of_europe_shifted": "NORMAL",
    "diplomatic_dp_regen": "LOW",
    "diplomatic_we_threshold": "MEDIUM",
    "diplomatic_relation_shift": "MEDIUM",
    "diplomatic_armistice_expired_peace": "HIGH",
    "diplomatic_armistice_expired_war": "HIGH",
    "hard_reject_posture_triggered": "HIGH",
    "hard_reject_posture_cleared": "MEDIUM",
    # Make Amends — NORMAL/MEDIUM per COMMITMENTS_PRESENTATION_SPEC §10.3.
    "amends_offered": "MEDIUM",
    # DG-4 refusal notices are CRITICAL per spec §8.8.10.
    "call_to_arms_refused_defensive": "CRITICAL",
    "call_to_arms_refused_offensive": "CRITICAL",
    "call_to_arms_honored_costly": "CRITICAL",
    "oathbreaker_posture_triggered": "HIGH",
    "oathbreaker_posture_cleared": "MEDIUM",
    "commitment_paradox_resolved": "MEDIUM",
    "nation_eliminated": "HIGH",
    "peace_ratified": "HIGH",
    # WB-B — war bargain lifecycle
    "bargain_ratified": "MEDIUM",
    "bargain_triggered": "HIGH",
    "bargain_fulfilled": "HIGH",
    "bargain_breached": "HIGH",
    "bargain_voided": "MEDIUM",
    "bargain_dormant_notice": "LOW",
}


def queue_dispatch_event(world, event_type: str, template_vars: dict, fog_rule: str) -> None:
    """Append a diplomatic event to the pending dispatch queue.

    Called by backend systems as events fire. The Morning Dispatch builder
    consumes and fog-filters these events when building the dispatch.

    Args:
        world: WorldState instance
        event_type: One of the _DIPLOMATIC_EVENT_TEMPLATES keys
        template_vars: Dict of template variable values (e.g. {"nation": "Prussia"})
        fog_rule: "always" | "partial_on_nation" | "player_vassal" |
                  "player_mission" | "detection_60pct"
    """
    world.pending_dispatch_events.append({
        "type": event_type,
        "template_vars": template_vars,
        "fog_rule": fog_rule,
    })


def _is_dispatch_event_visible(event: dict, world, player_nation: str) -> bool:
    """Apply fog rules to determine if a diplomatic dispatch event is visible.

    Fog rules (from DIPLOMACY_SPEC §11):
    - "always": Always shown to player
    - "partial_on_nation": Visible if PARTIAL+ on any relevant nation
    - "player_vassal": Visible if nation is player's vassal
    - "player_mission": Visible if Talleyrand's mission targets that nation
    - "detection_60pct": Already resolved at queue time (always show if queued)
    """
    from backend.game_logic.diplomatic_ledger import _get_nation_visibility

    # Settlement events (spec §11.6 line 1287) own their own fog rule
    # and never carry the legacy `template_vars` / `fog_rule` shape.
    event_type = event.get("type", "")
    if is_settlement_event_type(event_type):
        return is_settlement_event_visible(event, world, player_nation)

    fog_rule = event.get("fog_rule", "always")
    template_vars = event.get("template_vars", {})

    if fog_rule == "always":
        return True

    if fog_rule == "detection_60pct":
        # Already passed the roll at queue time
        return True

    if fog_rule == "partial_on_nation":
        # Check PARTIAL+ on any nation mentioned in template_vars.
        # `actor_nation` / `target_nation` keys added for B-B7 `amends_offered`
        # and any future events that prefer the explicit semantic names.
        # `breaker` / `victim` keys added for B-B4
        # `call_to_arms_refused_defensive`.
        nations_to_check = []
        for key in ("nation", "nation_a", "nation_b", "target", "aggressor", "ally", "enemy",
                   "vassal_capital", "witness_nation", "perpetrator_nation", "victim_nation",
                   "actor_nation", "target_nation", "breaker", "victim", "honorer"):
            val = template_vars.get(key)
            if val:
                nations_to_check.append(val)
        # Player nation events always visible
        for nation in nations_to_check:
            if nation == player_nation:
                return True
            vis = _get_nation_visibility(nation, world)
            if vis in (FULL, PARTIAL):
                return True
        return False

    if fog_rule == "player_vassal":
        nation = template_vars.get("nation", "")
        vassals = getattr(world, 'vassals', {})
        vassal_state = vassals.get(nation)
        if vassal_state and vassal_state.get("lord") == player_nation:
            return True
        return False

    if fog_rule == "player_mission":
        mission = getattr(world, 'active_diplomatic_mission', None)
        if mission:
            target = mission.get("target", "")
            if target == template_vars.get("nation", ""):
                return True
        return False

    # Unknown fog rule — default show
    return True


def _format_dispatch_event_text(event_type: str, template_vars: dict) -> str:
    """Format event text from template + variables."""
    if event_type in COMMITMENTS_ROUTES and event_type != "witness_strike_recorded":
        return format_commitments_notice(event_type, template_vars)

    if event_type == "settlement_summary":
        # Settlement events ship the full payload (no `template_vars`
        # wrapper). The dispatch consumer passes the event dict in via
        # `template_vars` so the existing call sites stay uniform.
        return compose_summary_oneliner(template_vars)
    if event_type == "settlement_digest":
        return compose_digest_oneliner(template_vars)

    if event_type == "diplomatic_treaty_broken":
        nation = template_vars.get("nation", "Unknown")
        target = template_vars.get("target", "")
        treaty_type = template_vars.get("treaty_type", "treaty")
        reason_phrase = template_vars.get("reason_phrase", "")
        end_reason_family = template_vars.get("end_reason_family", "")
        # Classify forced / opportunistic ruptures distinctly so presentation
        # can tell "France abandoned Prussia" from "Prussia was dragged into war."
        if end_reason_family == "obsolescence_or_external" and target:
            return f"{nation} was forced to break the {treaty_type} with {target} {reason_phrase}.".strip()
        if end_reason_family == "counterparty_reversal" and target:
            return f"{target} broke the {treaty_type} with {nation} first."
        if target and reason_phrase:
            return f"{nation} has broken the {treaty_type} with {target} {reason_phrase}."
        if target:
            return f"{nation} has broken the {treaty_type} with {target}."

    if event_type == "diplomatic_war_declared":
        nation = template_vars.get("nation", "Unknown")
        target = template_vars.get("target", "Unknown")
        breached_treaty = template_vars.get("breached_treaty", "")
        defensive_joiners = int(template_vars.get("defensive_joiner_count", 0) or 0)
        offensive_joiners = int(template_vars.get("offensive_joiner_count", 0) or 0)
        extra_parts = []
        if breached_treaty:
            extra_parts.append(f"shattering the {breached_treaty}")
        total_joiners = defensive_joiners + offensive_joiners
        if total_joiners > 0:
            extra_parts.append(f"with {total_joiners} allied court{'s' if total_joiners != 1 else ''} poised to follow")
        if extra_parts:
            return f"{nation} has declared war on {target}, " + ", ".join(extra_parts) + "."
        return f"{nation} has declared war on {target}."

    if event_type == "witness_strike_recorded":
        witness = template_vars.get("witness_nation", "Unknown")
        perpetrator = template_vars.get("perpetrator_nation", "Unknown")
        victim = template_vars.get("victim_nation", "Unknown")
        scope_reason = template_vars.get("scope_reason", "")
        scope_phrase = {
            "ally": f"as an ally of {victim}",
            "rival": f"as a rival of {perpetrator}",
            "treaty_partner_of_breaker": f"as a treaty partner of {perpetrator}",
            "treaty_partner_of_honorer": f"as a treaty partner of {perpetrator}",
            "shared_enemy": "as a fellow belligerent",
            "region_observer": "from the sidelines",
        }.get(scope_reason, "")
        if scope_phrase:
            return f"{witness} has taken note of {perpetrator}'s breach against {victim} {scope_phrase}."
        return f"{witness} has taken note of {perpetrator}'s breach against {victim}."

    if event_type == "hard_reject_posture_triggered":
        victim = template_vars.get("victim_nation", "Unknown")
        perpetrator = template_vars.get("perpetrator_nation", "Unknown")
        return (
            f"{victim} has shut the chancery to {perpetrator} after repeated betrayals."
        )

    if event_type == "hard_reject_posture_cleared":
        victim = template_vars.get("victim_nation", "Unknown")
        perpetrator = template_vars.get("perpetrator_nation", "Unknown")
        return (
            f"{victim} has reopened deeper diplomacy with {perpetrator}."
        )

    template = _DIPLOMATIC_EVENT_TEMPLATES.get(event_type, "")
    if not template:
        return f"Diplomatic event: {event_type}"
    try:
        return template.format(**template_vars)
    except (KeyError, IndexError):
        # Graceful fallback if template vars missing
        return template


def _build_relation_change_events(world, player_nation: str) -> list:
    """S2: Fire dispatch events for significant relation changes this turn."""
    deltas = getattr(world, '_relation_deltas_this_turn', {})
    events = []
    for nation, delta in deltas.items():
        if abs(delta) >= 10:
            direction = "improved" if delta > 0 else "worsened"
            events.append({
                "type": "diplomatic_relation_shift",
                "text": f"Relations with {nation} have {direction} significantly ({delta:+d} this turn).",
                "priority": "MEDIUM",
            })
    return events


def _build_diplomatic_events_section(world, player_nation: str) -> list:
    """Build the DIPLOMATIC EVENTS section from pending dispatch events.

    Pulls world.pending_dispatch_events, applies fog filter, formats text,
    returns list of {"type", "text", "priority"} dicts.
    """
    events = getattr(world, 'pending_dispatch_events', [])
    if not events:
        return []

    result = []
    witness_group_indexes = {}
    settlement_indexes: List[int] = []
    for event in events:
        if not _is_dispatch_event_visible(event, world, player_nation):
            continue

        event_type = event.get("type", "")
        # Settlement events carry the full payload directly (no
        # `template_vars` wrapper); the formatter accepts that shape.
        if is_settlement_event_type(event_type):
            text = _format_dispatch_event_text(event_type, event)
            priority = settlement_priority(event_type, event)
            entry = {
                "type": event_type,
                "text": text,
                "priority": priority,
                "event_family": "settlement",
                "war_id": str(event.get("war_id", "") or ""),
                "route_id": str(
                    (event.get("route") or {}).get("route_id", "") or ""
                ),
            }
            if event.get("awe_tags"):
                entry["awe_tags"] = list(event.get("awe_tags") or [])
            result.append(entry)
            settlement_indexes.append(len(result) - 1)
            continue

        template_vars = event.get("template_vars", {})
        if event_type == "witness_strike_recorded":
            episode_id = str(template_vars.get("episode_id", "") or "")
            key = episode_id or f"unkeyed_{len(result)}"
            witness = template_vars.get("witness_nation", "Unknown")
            if key not in witness_group_indexes:
                witness_group_indexes[key] = {
                    "index": len(result),
                    "vars": dict(template_vars),
                    "witnesses": [],
                }
                result.append({})
            group = witness_group_indexes[key]
            if witness not in group["witnesses"]:
                group["witnesses"].append(witness)
            result[group["index"]] = _format_witness_grouped_dispatch_event(group)
            continue

        text = _format_dispatch_event_text(event_type, template_vars)
        if event_type in COMMITMENTS_ROUTES:
            priority = commitments_priority(event_type, template_vars)
        else:
            priority = _DIPLOMATIC_EVENT_PRIORITY.get(event_type, "MEDIUM")

        result.append({
            "type": event_type,
            "text": text,
            "priority": priority,
        })

    # Spec §11.6 line 1279 — cap settlement-family dispatch lines at the
    # primary-beat threshold per ratification (`war_id:turn`). Overflow
    # rolls into a digest event so the rail does not blow up on
    # full-Europe ratifications. Only the primary `settlement_summary`
    # is capped; `settlement_digest` always renders because it IS the
    # overflow line.
    if settlement_indexes:
        result = _enforce_settlement_primary_beat_cap(result, settlement_indexes)
    return result


def _enforce_settlement_primary_beat_cap(
    rendered: List[Dict[str, Any]],
    settlement_indexes: List[int],
) -> List[Dict[str, Any]]:
    """Apply the spec §11.6 line 1279 top-four cap per ratification.

    Groups settlement summary lines by `war_id:turn`; keeps the first
    `SETTLEMENT_PRIMARY_BEAT_CAP` summaries per ratification and drops
    overflow. Digest lines are always preserved because they are the
    overflow signal.
    """
    if not settlement_indexes:
        return rendered
    keep_indexes: set = set(range(len(rendered)))
    summaries_per_ratification: Dict[str, List[int]] = {}
    for idx in settlement_indexes:
        entry = rendered[idx]
        if entry.get("type") != "settlement_summary":
            continue
        route_id = str(entry.get("route_id", "") or "")
        war_id = str(entry.get("war_id", "") or "")
        # Group on the route_id when present (carries `war_id:turn`),
        # else fall back to war_id.
        key = route_id or war_id or "unknown"
        # Strip the `settlement_summary:` prefix so summaries and any
        # future spotlight events from the same ratification land in the
        # same bucket.
        if key.startswith("settlement_summary:"):
            key = key.split("settlement_summary:", 1)[1]
        summaries_per_ratification.setdefault(key, []).append(idx)
    overflow_drops = 0
    for key, indexes in summaries_per_ratification.items():
        if len(indexes) <= SETTLEMENT_PRIMARY_BEAT_CAP:
            continue
        # Keep first N, drop the rest.
        for idx in indexes[SETTLEMENT_PRIMARY_BEAT_CAP:]:
            keep_indexes.discard(idx)
            overflow_drops += 1
    if overflow_drops == 0:
        return rendered
    return [entry for idx, entry in enumerate(rendered) if idx in keep_indexes]


def _format_witness_grouped_dispatch_event(group: dict) -> dict:
    vars_ = group.get("vars", {})
    witnesses = list(group.get("witnesses", []) or [])
    count = len(witnesses)
    perpetrator = vars_.get("perpetrator_nation", "Unknown")
    victim = vars_.get("victim_nation", "Unknown")
    if count <= 1:
        text = _format_dispatch_event_text("witness_strike_recorded", vars_)
    else:
        sample = ", ".join(str(w) for w in witnesses[:3])
        extra = count - 3
        if extra > 0:
            sample = f"{sample}, and {extra} more"
        text = (
            f"{count} courts have taken note of {perpetrator}'s conduct "
            f"toward {victim}: {sample}."
        )
    return {
        "type": "witness_strike_recorded",
        "text": text,
        "priority": commitments_priority("witness_strike_recorded", vars_),
        "episode_id": vars_.get("episode_id", ""),
        "witness_count": int(count),
        "witness_nations": witnesses,
    }
