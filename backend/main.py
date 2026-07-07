"""
FastAPI server for Project Sovereign
Connects Godot frontend to Python game logic
"""

import os
import threading  # noqa: E402 - 3A-1: needed for state_lock
from pathlib import Path

from dotenv import load_dotenv

# Load .env BEFORE any imports that might read env vars
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field  # noqa: F401

from backend.commands.parser import CommandParser
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState
from backend.nation_config import DEFAULT_PLAYER_NATION, get_player_nation
from backend.models.intel import FULL  # noqa: E402, F811 — used by _filter_enemy_phase_by_visibility
from backend.commands.meta_executor import _filter_tactical_events_by_fog
import backend.save_manager as save_manager
from backend.save_manager import autosave, save_game, load_game, list_saves, delete_save

# ════════════════════════════════════════════════════════════
# DEBUG MODE: Set to True to enable debug endpoints
# ════════════════════════════════════════════════════════════
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# ════════════════════════════════════════════════════════════
# STARTUP: Show LLM configuration
# ════════════════════════════════════════════════════════════
print("=" * 60)
print("PROJECT SOVEREIGN - Server Starting")
print("=" * 60)
llm_mode = os.getenv("LLM_MODE", "mock")
api_key = os.getenv("ANTHROPIC_API_KEY", "")
print(f"LLM_MODE: {llm_mode}")
print(f"ANTHROPIC_API_KEY: {'SET (' + api_key[:10] + '...)' if api_key else 'NOT SET'}")
print("=" * 60)

# Initialize game
app = FastAPI(title="Project Sovereign API")
parser = CommandParser()  # Uses LLM_MODE from environment
executor = CommandExecutor()
world = None
game_state = {"world": None, "debug_mode": DEBUG_MODE}
state_lock = threading.Lock()  # 3A-1: Protects state-mutating endpoints


def _resolve_sovereign_map() -> str:
    """Resolve the SOVEREIGN_MAP flag for the game bootstrap (Map Slice 5, G1).

    The game ships the 126-province Europe map: the default is "europe".
    Rollback is a flag flip, not a code change — set SOVEREIGN_MAP=legacy to
    restore the 19-region world. Read per-call (not cached at import) so a
    running process and the test suite can exercise both paths.
    """
    value = os.getenv("SOVEREIGN_MAP", "europe").strip().lower()
    if value not in ("europe", "legacy"):
        print(f"[WARN] Unknown SOVEREIGN_MAP={value!r} -- falling back to 'europe'")
        return "europe"
    return value


# Map Slice 7 default-boot flip: the shipped campaign IS the 1805 scenario.
# Absolute (repo-root-derived) so the boot works regardless of CWD.
_DEFAULT_SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
)
# Explicit opt-out sentinel: with a scenario as the default, tests/devs need an
# env value that means "no scenario — boot the bare flag-resolved world".
SCENARIO_NONE_SENTINEL = "none"


def _resolve_scenario_path() -> str:
    """Resolve the scenario for the game bootstrap (Slice 7 default-boot flip).

    Precedence (read per-call so tests can exercise every path):
    1. SOVEREIGN_SCENARIO=<path> — explicit scenario, fails loudly downstream.
    2. SOVEREIGN_SCENARIO=none — bare flag-resolved world (opt-out sentinel).
    3. SOVEREIGN_MAP=legacy — no scenario (the G1 rollback drill stays a pure
       flag flip: legacy world, legacy marshals, no code change).
    4. SOVEREIGN_SMOKE_START set — no scenario (presets seed their own wars in
       the WorldState constructor; combining them with a scenario is untested
       by design — the never-combine rule, STATUS §Diplomacy accommodations).
    5. Default: the authored 1805 opening (europe_1805.json).
    """
    explicit = os.getenv("SOVEREIGN_SCENARIO", "").strip()
    if explicit:
        if explicit.lower() == SCENARIO_NONE_SENTINEL:
            return ""
        return explicit
    if _resolve_sovereign_map() == "legacy":
        return ""
    if os.getenv("SOVEREIGN_SMOKE_START", "").strip():
        print("[WARN] SOVEREIGN_SMOKE_START set -- skipping the default 1805 scenario boot")
        return ""
    return str(_DEFAULT_SCENARIO_PATH)


def _build_new_world(player_nation: str = DEFAULT_PLAYER_NATION) -> WorldState:
    """Create a fresh campaign world with the default start-state.

    A configured SOVEREIGN_SCENARIO fails LOUDLY (missing file / invalid
    scenario raises) — silently falling back to the default world would run
    the wrong campaign and hide scenario-authoring errors.
    """
    scenario_path = _resolve_scenario_path()
    if scenario_path:
        if os.getenv("SOVEREIGN_SMOKE_START", "").strip():
            # An EXPLICIT scenario + a smoke preset is the documented
            # never-combine pair (the preset seeds wars in the constructor,
            # the scenario seeds its own) — fail loudly rather than boot an
            # untested hybrid. (The DEFAULT scenario already yields to the
            # preset in _resolve_scenario_path.)
            raise ValueError(
                "SOVEREIGN_SCENARIO and SOVEREIGN_SMOKE_START are both set — "
                "never combine them (unset one; see docs/STATUS.md "
                "'Diplomacy accommodations')."
            )
        print(f"SOVEREIGN_SCENARIO: loading scenario from {scenario_path!r}")
        return WorldState.from_scenario(scenario_path)
    return WorldState(player_nation=player_nation, sovereign_map=_resolve_sovereign_map())


def _set_active_world(new_world: WorldState) -> WorldState:
    """Install a world instance as the active campaign state."""
    global world
    world = new_world
    game_state["world"] = new_world
    return new_world


def _reset_world_state(player_nation: str = DEFAULT_PLAYER_NATION) -> WorldState:
    """Replace the active campaign with a fresh world."""
    return _set_active_world(_build_new_world(player_nation=player_nation))


_reset_world_state()
print(f"SOVEREIGN_MAP: {world.sovereign_map} ({len(world.regions)} regions)")


def get_llm_game_state() -> dict:
    """
    Build game state dict in the format expected by prompt_builder.

    The LLM prompt builder expects:
    - marshals: {name: {location, strength, morale}}
    - enemies: {name: {location, strength, nation}}
    - map_data: {region: {controller, marshals: [{name, personality}]}}

    This is separate from get_game_state_summary() which is for the frontend.
    """
    # Build marshals dict (player marshals)
    marshals = {}
    for m in world.get_player_marshals():
        if m.strength > 0:  # Only alive marshals
            marshals[m.name] = {
                "location": m.location,
                "strength": int(m.strength),
                "morale": int(m.morale),
            }

    # Build enemies dict — fog-filtered (V2-5)
    # Only include enemies in regions with PARTIAL+ visibility.
    # PARTIAL: show "unknown" strength. FULL: show exact.
    from backend.models.intel import FULL, PARTIAL, VISIBILITY_PRIORITY
    enemies = {}
    for m in world.get_enemy_marshals():
        if m.strength > 0:  # Only alive marshals
            region_intel = world.get_region_intel(m.location)
            vis = region_intel.visibility
            if VISIBILITY_PRIORITY.get(vis, 0) >= VISIBILITY_PRIORITY[PARTIAL]:
                enemies[m.name] = {
                    "location": m.location,
                    "strength": int(m.strength) if vis == FULL else "unknown",
                    "nation": m.nation,
                }

    # Build map_data dict — R5: fog-filter enemy marshals
    map_data = {}
    for region_name, region in world.regions.items():
        marshals_here = world.get_marshals_in_region(region_name)
        region_vis = world.get_region_intel(region_name).visibility_at_least(PARTIAL)
        visible_marshals = [
            {"name": m.name, "personality": getattr(m, 'personality', 'unknown')}
            for m in marshals_here
            if m.strength > 0
            and (m.nation == world.player_nation or region_vis)
        ]
        map_data[region_name] = {
            "controller": region.controller or "Neutral",
            "marshals": visible_marshals,
        }

    return {
        "turn": int(world.current_turn),
        "gold": int(world.gold),
        "marshals": marshals,
        "enemies": enemies,
        "map_data": map_data,
        # July 2026 AI audit: the live providers read game_state["world"]
        # for the command-history repetition guardrail (anti-spam on the
        # strategic-score bonuses) — without it they silently sent empty
        # history on every parse. Never serialized: this dict only feeds
        # prompt building.
        "world": world,
    }

def _get_talleyrand_state_label(w) -> str:
    """Get Talleyrand state label for top bar (authority-based, PL-23)."""
    if not hasattr(w, 'authority_tracker'):
        return "UNKNOWN"
    return w.authority_tracker.get_authority_label()


_MISSION_TYPE_DISPLAY = {
    "IMPROVE_RELATIONS": "Improving Relations",
    "COURT_NATION": "Courting",
    "GATHER_INTEL": "Gathering Intel",
    "UNDERMINE_ALLIANCE": "Undermining Alliance",
    "REASSURE_ALLY": "Reassuring Ally",
    "CONTINENTAL_SYSTEM": "Continental System",
}


def _get_talleyrand_mission_summary(w) -> str:
    """Get Talleyrand mission summary for top bar."""
    mission = getattr(w, 'active_diplomatic_mission', None)
    if mission and not mission.get("completed"):
        raw_type = mission.get("type", "Unknown")
        m_type = _MISSION_TYPE_DISPLAY.get(raw_type, raw_type.replace("_", " ").title())
        m_target = mission.get("target", "Unknown")
        return f"{m_type} → {m_target}"
    return "None"


def build_base_response(world, success: bool = True, message: str = "",
                        events: list = None,
                        include_popup_passthroughs: bool = True,
                        queue_informational_notices: bool = True,
                        include_notifications: bool = True,
                        **extra) -> dict:
    """Standard response builder. ALL POST endpoints must use this.

    Structurally guarantees:
    - Standard gameplay envelope (impossible to forget)
    - Diplomatic top-bar fields (always present, never stale)
    - War-status payload (`active_wars`) in every gameplay response
    - Game state summary (always present)
    - Optional popup passthroughs / notice queuing / notification draining
      for endpoints that need to defer those surfaces temporarily

    Endpoint-specific fields passed as **extra.
    """
    from backend.game_logic.war_status import build_active_wars

    response = {
        "success": success,
        "message": message,
        "events": events if events is not None else [],
        "game_state": world.get_filtered_game_state_summary(),
        "action_summary": world.get_action_summary(),
        "active_wars": build_active_wars(world),
        # Diplomatic top-bar fields — present in EVERY gameplay response
        "diplomatic_points": int(getattr(world, 'diplomatic_points', 0)),
        "max_diplomatic_points": int(getattr(world, 'max_diplomatic_points', 3)),
        "talleyrand_state": _get_talleyrand_state_label(world),
        "talleyrand_mission_summary": _get_talleyrand_mission_summary(world),
        "threat_level": int(getattr(world, 'threat_level', 0)),
        "coalition_brewing": getattr(world, 'coalition_brewing', None) is not None,
        "coalition_brewing_turns": int(
            world.coalition_brewing.get("turns_remaining", 0)
        ) if getattr(world, 'coalition_brewing', None) else None,
        # Session 2 follow-up: Single source of truth for mailbox badge
        "pending_envoy_count": int(world.dialogue_manager.get_mailbox_count()),
    }
    response.update(extra)
    if include_popup_passthroughs:
        _include_popup_passthroughs(response, world)
    if queue_informational_notices:
        _queue_informational_diplomacy_notices(response, world)
    notice_drain = getattr(world, "drain_settlement_draft_notices", None)
    if callable(notice_drain):
        draft_notices = notice_drain()
        if draft_notices:
            response["settlement_draft_notices"] = draft_notices
    # Notifications — persistent alerts for Godot notification bar
    if include_notifications and world.notifications.has_pending():
        response["notifications"] = world.notifications.get_pending()
    return response


def _build_result_response(result: dict, world) -> dict:
    """Build a standard response from an executor result dict.

    Strips new_state (circular refs), adds base fields via build_base_response().
    Used for /command early returns and endpoints that forward executor results.
    """
    extra = {k: v for k, v in result.items() if k != "new_state"}
    return build_base_response(
        world,
        success=extra.pop("success", False),
        message=extra.pop("message", ""),
        events=extra.pop("events", []),
        **extra
    )


def _build_command_response(result: dict, world, feedback: dict | None = None) -> dict:
    """Build the main /command response from the shared base contract.

    /command still has one legitimate divergence from the default builder:
    when enemy_phase is present, choice-requiring popups are deferred so Godot
    can show the end-turn report first. Start from build_base_response() and
    layer only that specialized post-processing afterward.
    """
    response = build_base_response(
        world,
        success=result.get("success", False),
        message=result.get("message", "Command executed"),
        events=result.get("events", []),
        include_popup_passthroughs=False,
        queue_informational_notices=False,
        include_notifications=False,
        action_info=result.get("action_info", {}),
        # Turn the enemy phase actually happened on (before advance_turn increments).
        turn_ended=int(result["turn_ended"]) if "turn_ended" in result else None,
    )
    if feedback:
        response["feedback"] = feedback
    return response


_COMMAND_RESULT_SIMPLE_FIELDS = (
    "show_load_dialog",
    "cavalry_terrain_message",
    "bombardment_advisory",
    "battle_report",
    "reinforcement_messages",
    "coordination_tutorial",
    "opening_attack_guidance",
    "mild_concerns",
    "morning_dispatch",
    # G4F-21: failed mounts (e.g. opening a settlement on an archived war)
    # name their refusal code and recovery surface; the /command response
    # dropped them while /respond_to_diplomatic_dialogue passed them through.
    "error",
    "error_display",
    "recovery_route",
)


def _copy_truthy_result_fields(
    response: dict, result: dict, field_names: tuple[str, ...]
) -> None:
    """Copy simple truthy executor fields into the API response."""
    for field_name in field_names:
        value = result.get(field_name)
        if value:
            response[field_name] = value


def _include_peace_ratification_summary(response: dict, result: dict) -> None:
    """Pass BPH-D ratification summaries through command response builders."""
    summary = result.get("peace_ratification_summary")
    proposal_result = response.get("proposal_result")
    if not summary and isinstance(proposal_result, dict):
        summary = proposal_result.get("peace_ratification_summary")
    if not summary:
        return

    response["peace_ratification_summary"] = summary
    if isinstance(proposal_result, dict):
        proposal_result["peace_ratification_summary"] = summary


def _include_command_bombardment_result(response: dict, result: dict) -> None:
    """Pass through bombardment payloads and keep the explicit action marker."""
    bombardment_result = result.get("bombardment_result")
    if bombardment_result:
        response["bombardment_result"] = bombardment_result
        response["action"] = "bombardment"


def _include_command_redemption_event(response: dict, result: dict, world) -> None:
    """Surface redemption choice state and persist it for the follow-up endpoint."""
    redemption_event = result.get("redemption_event")
    if redemption_event:
        response["state"] = "awaiting_redemption_choice"
        response["redemption_event"] = redemption_event
        world.pending_redemption = redemption_event
        print(f"[ALERT] REDEMPTION TRIGGERED for {redemption_event['marshal']}")


def _build_visible_enemy_phase(enemy_phase: dict, world) -> dict | None:
    """Serialize enemy-phase data and apply fog filtering for Godot."""
    cleaned_phase = {
        "nations": {},
        "total_actions": enemy_phase.get("total_actions", 0),
        "summary": [],
    }

    for nation, nation_data in enemy_phase.get("nations", {}).items():
        cleaned_actions = []
        for action in nation_data.get("actions", []):
            cleaned_action = {k: v for k, v in action.items() if k != "new_state"}
            if DEBUG_MODE:
                if "events" in cleaned_action:
                    print(
                        f"[ENEMY_PHASE_DEBUG] {nation} action has events: "
                        f"{len(cleaned_action.get('events', []))} events"
                    )
                    for evt in cleaned_action.get("events", []):
                        print(f"  - Event type: {evt.get('type')}, keys: {list(evt.keys())}")
                else:
                    print(
                        f"[ENEMY_PHASE_DEBUG] {nation} action has NO events! "
                        f"Keys: {list(cleaned_action.keys())}"
                    )
            cleaned_actions.append(cleaned_action)
        cleaned_phase["nations"][nation] = {
            "actions": cleaned_actions,
            "action_count": nation_data.get("action_count", 0),
        }

    if enemy_phase.get("enemy_victory"):
        cleaned_phase["enemy_victory"] = enemy_phase["enemy_victory"]

    raw_total = cleaned_phase.get("total_actions", 0)
    raw_nations = list(cleaned_phase.get("nations", {}).keys())
    cleaned_phase = _filter_enemy_phase_by_visibility(cleaned_phase, world)

    if cleaned_phase.get("total_actions", 0) > 0 or cleaned_phase.get("enemy_victory"):
        return cleaned_phase
    if raw_total > 0:
        cleaned_phase["fog_hidden_summary"] = [
            f"Our scouts report activity within {nation}'s borders, "
            f"but their formations remain beyond our sight."
            for nation in raw_nations
        ]
        return cleaned_phase
    return None


def _include_command_enemy_phase(response: dict, result: dict, world) -> None:
    """Attach enemy-phase payloads without leaking hidden actions."""
    enemy_phase = result.get("enemy_phase")
    if not enemy_phase:
        return

    cleaned_phase = _build_visible_enemy_phase(enemy_phase, world)
    if cleaned_phase is not None:
        response["enemy_phase"] = cleaned_phase

    if DEBUG_MODE and cleaned_phase is not None:
        print("[ENEMY_PHASE_FINAL] Sending to Godot:")
        for nation, data in cleaned_phase.get("nations", {}).items():
            print(f"  {nation}: {len(data.get('actions', []))} actions")
            for i, act in enumerate(data.get("actions", [])):
                has_events = "events" in act and len(act.get("events", [])) > 0
                print(
                    f"    [{i}] {act.get('ai_action', {}).get('action', '?')} "
                    f"- has_events: {has_events}"
                )


def _include_command_strategic_reports(response: dict, result: dict) -> None:
    """Pass through strategic reports and preserve debug visibility."""
    strategic_reports = result.get("strategic_reports")
    if strategic_reports:
        response["strategic_reports"] = strategic_reports
        if DEBUG_MODE:
            print(f"[STRATEGIC_REPORTS] Sending {len(strategic_reports)} reports to Godot:")
            for i, sr in enumerate(strategic_reports):
                print(
                    f"  [{i}] {sr.get('marshal')}: {sr.get('command')} -> "
                    f"{sr.get('action', 'N/A')}, status={sr.get('order_status')}, "
                    f"has_battle={bool(sr.get('battle_details'))}"
                )
    elif DEBUG_MODE:
        print(f"[STRATEGIC_REPORTS] No strategic reports in result (keys: {[k for k in result.keys() if 'strat' in k.lower()]})")


def _include_command_tactical_events(response: dict, result: dict, world) -> None:
    """Pass through fog-filtered tactical events for the turn log."""
    tactical_events = result.get("tactical_events")
    if tactical_events:
        response["tactical_events"] = _filter_tactical_events_by_visibility(
            tactical_events, world
        )


def _include_command_independent_report(response: dict, result: dict) -> None:
    """Pass through independent command report payloads when present."""
    if result.get("show_independent_command_report"):
        response["show_independent_command_report"] = True
        response["independent_command_report"] = result.get(
            "independent_command_report", []
        )


def _apply_command_popup_contract(response: dict, result: dict, world) -> None:
    """Apply the one /command-specific popup deferral rule after base response build."""
    if not response.get("enemy_phase"):
        if result.get("ai_proposal"):
            response["ai_proposal"] = result["ai_proposal"]
            if world.pending_diplomatic_dialogue:
                response["diplomatic_dialogue"] = world.pending_diplomatic_dialogue
        _include_popup_passthroughs(response, world)
        return

    # PL-5A + PL-30: proposal results are informational-only and safe to show
    # alongside enemy_phase; other choice popups stay deferred on world.
    proposal_result = world.proposal_result_popup
    if proposal_result is not None:
        from backend.display_names import diplomatic_decision_reason_display

        proposal_result = dict(proposal_result)
        if (
            proposal_result.get("decision_reason")
            and not proposal_result.get("decision_reason_display")
        ):
            proposal_result["decision_reason_display"] = diplomatic_decision_reason_display(
                str(proposal_result.get("decision_reason", ""))
            )
            world.proposal_result_popup = proposal_result
        response["proposal_result"] = proposal_result
        world.proposal_result_popup = None


def _finalize_command_notifications(response: dict, world) -> None:
    """Drain informational notices into the persistent notification rail."""
    _queue_informational_diplomacy_notices(response, world)
    if world.notifications.has_pending():
        response["notifications"] = world.notifications.get_pending()


def _apply_command_result_layers(response: dict, result: dict, world) -> None:
    """Keep /command post-processing centralized instead of hand-layered inline."""
    _copy_truthy_result_fields(response, result, _COMMAND_RESULT_SIMPLE_FIELDS)
    _include_command_bombardment_result(response, result)
    _include_command_redemption_event(response, result, world)
    _include_command_enemy_phase(response, result, world)
    _include_command_strategic_reports(response, result)
    _include_command_tactical_events(response, result, world)
    _include_command_independent_report(response, result)
    _apply_command_popup_contract(response, result, world)
    _include_peace_ratification_summary(response, result)
    _finalize_command_notifications(response, world)


def _derive_proposal_result_outcome(result: dict) -> str:
    """Best-effort ACCEPT/REJECT normalization for fallback proposal popups."""
    raw_outcome = result.get("outcome", result.get("result", ""))
    if raw_outcome is not None:
        normalized = str(raw_outcome).strip().upper()
        if "REJECT" in normalized or "DECLIN" in normalized or "COUNTER" in normalized:
            return "REJECT"
        if "ACCEPT" in normalized or "APPROV" in normalized or "SUCCESS" in normalized:
            return "ACCEPT"

    if "accepted" in result:
        return "ACCEPT" if bool(result.get("accepted")) else "REJECT"

    message = str(result.get("message", "")).lower()
    if ("reject" in message or "declin" in message or "empty-handed" in message
            or "not agree" in message or "unacceptable" in message):
        return "REJECT"
    if "accept" in message or "agreed" in message or "excellent news" in message:
        return "ACCEPT"
    # Gate-4 1805 smoke (E-4): a successful in-transit dispatch ("Talleyrand
    # departs for the Saxony court... Expect a response by next turn.") is
    # neither accepted nor rejected — the hard REJECT default titled every
    # such send "Diplomatic Action Rejected" on the notice rail.
    if ("departs for" in message or "expect a response" in message
            or "expect an answer" in message or "en route" in message):
        return "PENDING"

    return "REJECT"


def _queue_informational_diplomacy_notices(response: dict, world) -> None:
    """Mirror informational diplomacy outcomes into the persistent notice rail."""
    proposal_result = response.get("proposal_result")
    if not isinstance(proposal_result, dict) or not proposal_result:
        return

    from backend.notifications import (
        create_notification,
        DIPLOMATIC_PROPOSAL_RESULT,
        NotificationPriority,
    )

    outcome = _derive_proposal_result_outcome(proposal_result)
    target_nation = str(proposal_result.get("target_nation", "Unknown"))
    proposal_type = str(proposal_result.get("proposal_type", "Diplomatic Action"))
    message = str(proposal_result.get("message", "")).strip()
    feedback = str(proposal_result.get("feedback", "")).strip()

    outcome_word = {
        "ACCEPT": "Accepted",
        "PENDING": "Dispatched",
    }.get(outcome, "Rejected")
    world.notifications.add(create_notification(
        DIPLOMATIC_PROPOSAL_RESULT,
        NotificationPriority.NORMAL,
        f"{proposal_type} {outcome_word}",
        message or f"{target_nation} has responded to our {proposal_type.lower()}.",
        int(world.current_turn),
        details={
            "target_nation": target_nation,
            "proposal_type": proposal_type,
            "outcome": outcome,
            "feedback": feedback,
        },
    ))


def _include_popup_passthroughs(response: dict, world) -> None:
    """Read the HIGHEST-PRIORITY popup from world, include in response, clear from world.

    R4: Called internally by build_base_response() — do NOT call directly.
    Use build_base_response() or _build_result_response() instead, which
    structurally guarantee popup inclusion. The only exception is the
    /command main response path (enemy_phase popup deferral).

    R6+R76: Uses PopupQueue for priority resolution. Only one popup per response
    cycle. Lower-priority popups remain queued for subsequent cycles.

    Keys are ALWAYS included (None if not set) so Godot can rely on their presence.
    """
    from backend.models.cooldown_manager import PopupQueue
    # V2-90: Auto-pop rebellion popup from list if single field is empty
    if (world.vassal_rebellion_imminent_popup is None
            and getattr(world, 'vassal_rebellion_imminent_popups', None)):
        world.vassal_rebellion_imminent_popup = world.vassal_rebellion_imminent_popups.pop(0)

    # R6: Pop highest-priority popup from queue (clears from world automatically)
    winner_attr, winner_key, winner_value = world._popup_queue.pop_highest()

    # Include the winner in response (Golden Rule 4: already cleared by pop)
    if winner_key is not None:
        if winner_key == "incoming_proposal" and isinstance(winner_value, dict):
            from backend.display_names import (
                diplomatic_decision_reason_display,
                proposal_display_name,
            )

            popup = winner_value.copy()
            if "proposal_type" in popup and "proposal_type_display" not in popup:
                popup["proposal_type_display"] = proposal_display_name(popup.get("proposal_type"))
            if popup.get("decision_reason") and "decision_reason_display" not in popup:
                popup["decision_reason_display"] = diplomatic_decision_reason_display(
                    str(popup.get("decision_reason", ""))
                )
            response[winner_key] = popup
        elif winner_key == "proposal_result" and isinstance(winner_value, dict):
            from backend.display_names import diplomatic_decision_reason_display

            popup = winner_value.copy()
            if popup.get("decision_reason") and "decision_reason_display" not in popup:
                popup["decision_reason_display"] = diplomatic_decision_reason_display(
                    str(popup.get("decision_reason", ""))
                )
            response[winner_key] = popup
        else:
            response[winner_key] = winner_value

    # Set all non-winner response keys to None so Godot can rely on key presence
    for response_key in PopupQueue.RESPONSE_KEYS.values():
        if response_key not in response:
            # Special case: incoming_proposal safety valve from pending dialogue
            if (response_key == "incoming_proposal"
                    and world.pending_diplomatic_dialogue
                    and world.pending_diplomatic_dialogue.get("type") == "incoming_proposal"
                    and winner_attr is not None):
                # A higher-priority popup won — don't derive incoming_proposal from dialogue
                response[response_key] = None
            elif (response_key == "incoming_proposal"
                    and winner_attr is None
                    and world.pending_diplomatic_dialogue
                    and world.pending_diplomatic_dialogue.get("type") == "incoming_proposal"):
                # BUGFIX: Safety valve — derive clauses from dialogue context
                # instead of hardcoding []. Empty clauses cause blank popup
                # in Godot. See BUGFIX_PLAN_PROPOSAL_FLOW.md.
                dialogue = world.pending_diplomatic_dialogue
                context = dialogue.get("context", {})
                proposal = context.get("proposal", {})
                sv_proposal_type = proposal.get("type", "unknown")
                from backend.display_names import (
                    PERSONALITY_DISPLAY,
                    diplomatic_decision_reason_display,
                    proposal_display_name,
                )
                from backend.game_logic.mailbox_payloads import build_proposal_popup_clauses
                decision_reason = str(context.get("decision_reason", ""))
                response["incoming_proposal"] = {
                    "from_nation": dialogue.get("target_nation", "Unknown"),
                    "diplomat_name": context.get("diplomat_name", "Unknown diplomat"),
                    "diplomat_personality": PERSONALITY_DISPLAY.get(
                        context.get("diplomat_personality", "unknown"), "Unknown"),
                    "proposal_type": sv_proposal_type,
                    "proposal_type_display": proposal_display_name(sv_proposal_type),
                    "clauses": build_proposal_popup_clauses(proposal),
                    "talleyrand_assessment": dialogue.get("talleyrand_text", ""),
                    "acceptance_hint": "Review the proposal carefully.",
                    "rejection_hint": "",
                    "is_counter_offer": False,
                    "decision_reason": decision_reason,
                    "decision_reason_display": diplomatic_decision_reason_display(decision_reason),
                }
            else:
                response[response_key] = None

    # V2-89 → R12C: Auto-promote from queue handled by dialogue_manager.pop() auto-promote.
    # Explicit promote_if_empty() covers the case where current is already None.
    world.dialogue_manager.promote_if_empty()

def _filter_enemy_phase_by_visibility(enemy_phase: dict, world_state) -> dict:
    """
    Fog of War (Session 34B): Filter enemy phase actions by player visibility.

    Fog filters information, not mechanics. The enemy AI ran omnisciently;
    this function redacts the DISPLAY of those actions based on what the
    player can see.

    Rules:
    - Battle involving a player marshal -> ALWAYS SHOW (player was in the battle)
    - Action in FULL visibility region -> show as-is
    - Action below FULL -> suppress (safe default)
    - Missing/unrecognized fields -> suppress (never show more than intended)
    """
    if not enemy_phase or not enemy_phase.get("nations"):
        return enemy_phase

    player_nation = world_state.player_nation
    filtered_phase = {
        "nations": {},
        "total_actions": 0,
        "summary": []
    }

    for nation, nation_data in enemy_phase.get("nations", {}).items():
        filtered_actions = []
        for action in nation_data.get("actions", []):
            # Check 1: Does this action involve a player marshal? (battle)
            involves_player = False
            events = action.get("events", [])
            if isinstance(events, list):
                for evt in events:
                    if isinstance(evt, dict):
                        # Battle events with player involvement
                        if evt.get("type") in ("battle", "bombardment"):
                            attacker = evt.get("attacker", "")
                            defender = evt.get("defender", "")
                            # attacker/defender can be dicts ({"name": ..., "casualties": ...})
                            # or strings — extract name safely for comparison
                            attacker_name = attacker.get("name", "") if isinstance(attacker, dict) else attacker
                            defender_name = defender.get("name", "") if isinstance(defender, dict) else defender
                            attacker_nation = evt.get("attacker_nation", "")
                            defender_nation = evt.get("defender_nation", "")
                            if (attacker_nation == player_nation or
                                    defender_nation == player_nation):
                                involves_player = True
                                break
                            # Also check marshal names against player marshals
                            for pm in world_state.get_player_marshals():
                                if pm.name in (attacker_name, defender_name):
                                    involves_player = True
                                    break

            # Also check ai_action target against player marshals
            ai_action = action.get("ai_action", {})
            if ai_action and isinstance(ai_action, dict):
                target = ai_action.get("target", "")
                if target:
                    for pm in world_state.get_player_marshals():
                        if pm.name == target:
                            involves_player = True
                            break

            if involves_player:
                filtered_actions.append(action)
                continue

            # Check 2: Determine action region and check visibility
            action_region = None

            # Try to get region from ai_action
            if ai_action and isinstance(ai_action, dict):
                ai_marshal_name = ai_action.get("marshal", "")
                if ai_marshal_name:
                    ai_marshal = world_state.get_marshal(ai_marshal_name)
                    if ai_marshal:
                        action_region = ai_marshal.location

            # If we have a region, check visibility
            if action_region:
                intel = world_state.get_region_intel(action_region)
                if intel.visibility == FULL:
                    filtered_actions.append(action)
                    continue
            # Missing region or below FULL -> suppress (safe default)

        if filtered_actions:
            filtered_phase["nations"][nation] = {
                "actions": filtered_actions,
                "action_count": len(filtered_actions)
            }
            filtered_phase["total_actions"] += len(filtered_actions)

    # 2A-1: Rebuild summary from filtered (visible) actions only
    rebuilt_summary = []
    for nation, nation_data in filtered_phase["nations"].items():
        for action in nation_data.get("actions", []):
            ai_action = action.get("ai_action", {})
            if ai_action:
                marshal_name = ai_action.get("marshal", "Unknown")
                action_type = ai_action.get("action", "unknown")
                target = ai_action.get("target", "")
                entry = f"{marshal_name}: {action_type}"
                if target:
                    entry += f" → {target}"
                rebuilt_summary.append(entry)
    filtered_phase["summary"] = rebuilt_summary

    # Preserve enemy_victory if present
    if enemy_phase.get("enemy_victory"):
        filtered_phase["enemy_victory"] = enemy_phase["enemy_victory"]

    return filtered_phase


_filter_tactical_events_by_visibility = _filter_tactical_events_by_fog  # P3-2: consolidated alias


# Allow Godot to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3A-1: Serialize state-mutating requests to prevent concurrent corruption
@app.middleware("http")
async def serialize_state_mutations(request: Request, call_next):
    """Acquire state_lock for all POST requests (state-mutating)."""
    if request.method == "POST":
        with state_lock:
            response = await call_next(request)
            return response
    return await call_next(request)


class CommandRequest(BaseModel):
    command: str = Field(max_length=500)
    action: str | None = None
    target_nation: str | None = None
    war_id: str | None = None
    # GT-Slice-4: the SC-5R editor's structured Submit-for-Review fields
    # (`settlement_terms` / `selected_target_nation` /
    # `covered_enemy_participants`) are removed with the freeform editor
    # after a verify-dead pass — no non-editor producer ever sent them.
    # `target_nation` + `war_id` predate them and stay: the War Detail
    # reopen (PF-2) and the diplomacy wizard both send them.


class ObjectionResponse(BaseModel):
    """Request model for responding to marshal objections."""
    choice: str  # 'trust', 'insist', or 'compromise'


class DiplomaticObjectionResponse(BaseModel):
    """Request model for typed Talleyrand objection popup responses."""
    choice: str  # 'proceed', 'modify', or 'cancel'
    action: str | None = None
    target_nation: str | None = None


class RedemptionResponse(BaseModel):
    """Request model for responding to redemption events."""
    choice: str  # 'grant_autonomy', 'dismiss', or 'demand_obedience'


class GloriousChargeResponse(BaseModel):
    """Request model for responding to Glorious Charge popup."""
    choice: str  # 'charge' or 'restrain'


class CaptureChoiceResponse(BaseModel):
    """Request model for responding to plunder/secure choice (Phase 6.2.E)."""
    choice: str  # 'plunder' or 'secure'


class StrategicInterruptResponse(BaseModel):
    """Request model for responding to strategic command interrupts (Phase D)."""
    marshal_name: str
    response_type: str  # 'cannon_fire', 'blocked_path', 'ally_moving'
    choice: str  # varies by response_type


class SaveRequest(BaseModel):
    """Request model for saving game state."""
    save_name: str = "Quicksave"


class LoadRequest(BaseModel):
    """Request model for loading a saved game."""
    filename: str


class DeleteSaveRequest(BaseModel):
    """Request model for deleting a save file."""
    filename: str


@app.get("/test")
def test_connection():
    """Test endpoint for Godot connection."""
    from backend.game_logic.war_status import build_active_wars
    response = {
        "success": True,
        "status": "ok",
        "message": "Backend is running",
        "turn": int(world.current_turn),
        "gold": int(world.gold),
        "manpower_pools": {
            "infantry": int(world.manpower_pools.get(world.player_nation, {}).get("infantry", 0)),
            "cavalry": int(world.manpower_pools.get(world.player_nation, {}).get("cavalry", 0)),
            "artillery": int(world.manpower_pools.get(world.player_nation, {}).get("artillery", 0)),
        },
        "action_summary": world.get_action_summary(),
        "game_state": world.get_filtered_game_state_summary(),
        # Diplomatic top-bar fields (Session 8A)
        "diplomatic_points": int(getattr(world, 'diplomatic_points', 0)),
        "max_diplomatic_points": int(getattr(world, 'max_diplomatic_points', 3)),
        "talleyrand_state": _get_talleyrand_state_label(world),
        "talleyrand_mission_summary": _get_talleyrand_mission_summary(world),
        "threat_level": int(getattr(world, 'threat_level', 0)),
        "coalition_brewing": getattr(world, 'coalition_brewing', None) is not None,
        "coalition_brewing_turns": int(world.coalition_brewing.get("turns_remaining", 0)) if getattr(world, 'coalition_brewing', None) else None,
        # Session 2 follow-up: Single source of truth for mailbox badge
        "pending_envoy_count": int(world.dialogue_manager.get_mailbox_count()),
    }
    # War status panel data (N4f) — for HUD initialization on page load
    response["active_wars"] = build_active_wars(world)
    return response


@app.get("/map_topology")
def get_map_topology():
    """Static map topology (adjacency, terrain, grid) for frontend rendering.

    Source of truth for region adjacency shared between backend and Godot.
    Per-turn state (controller, marshals, fog) still lives in
    `game_state.map_data`; this endpoint exposes only authored scenario data.

    Map Slice 5: serves the ACTIVE world's map — the 126-province Europe
    graph on the default bootstrap, the 19-region set under
    SOVEREIGN_MAP=legacy — so backend and renderer can never drift.
    """
    from backend.models.region import get_starting_controllers

    starting_controllers = (
        getattr(world, "_starting_controllers", None) or get_starting_controllers()
    )
    regions = {}
    for name, region in world.regions.items():
        grid = region.grid_position or (0, 0)
        regions[name] = {
            "adjacent": list(region.adjacent_regions),
            "terrain": region.terrain,
            "region_type": region.region_type,
            "is_capital": bool(region.is_capital),
            "starting_controller": starting_controllers.get(name),
            "grid_position": [int(grid[0]), int(grid[1])],
        }
    return {
        "success": True,
        "regions": regions,
        "nation_capitals": dict(world.nation_capitals),
    }


@app.post("/command")
def execute_command(request: CommandRequest):
    """Execute a game command and return result."""
    # print(f"\n{'=' * 60}")
    # print(f"📨 COMMAND RECEIVED: '{request.command}'")
    # print(f"   Current turn: {world.current_turn}")
    # print(f"   Actions before: {world.actions_remaining}/{world.max_actions_per_turn}")
    # print(f"{'=' * 60}")

    try:
        # ════════════════════════════════════════════════════════════
        # GAME-OVER GUARD — No actions after the war ends
        # ════════════════════════════════════════════════════════════
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)

        # ════════════════════════════════════════════════════════════
        # EMPTY COMMAND CHECK — Reject blank input
        # ════════════════════════════════════════════════════════════
        if not request.command or not request.command.strip():
            return build_base_response(
                world, success=False, message="No command given, Sire.",
                action_info={"remaining": int(world.actions_remaining)})

        # ════════════════════════════════════════════════════════════
        # CR-2: PENDING COMMAND CLARIFICATION — one question, one answer.
        # Typed answers ("Davout", "2", "yes", "cancel") resolve against
        # the stored options into a full deterministic reissue command;
        # anything else clears the question and parses normally
        # (LOCAL_PLANNING never blocks). Consumed either way — the player
        # gets exactly one question per command, never a dialogue loop.
        # Adversarial-review fix: this MUST run before the strategic
        # interrupt loop — the clarification is the most recent question
        # asked, and the interrupt keyword matcher would otherwise hijack
        # answers like "cancel" and leave the dialogue lingering.
        # ════════════════════════════════════════════════════════════
        from backend.commands.clarification import (
            CLARIFICATION_DIALOGUE_TYPE,
            build_marshal_choice_clarification,
            build_unknown_name_clarification,
            interpret_clarification_answer,
            register_pending_clarification,
        )
        from backend.commands.delegation import (
            build_delegation_clarification,
            describe_cautious_delegation,
            detect_delegation,
            maybe_delegation_hint,
            parse_resolved_to_action,
            route_arm,
        )

        command_text = request.command
        pending_clarification = world.dialogue_manager.peek()
        if (pending_clarification is not None
                and pending_clarification.get("type") == CLARIFICATION_DIALOGUE_TYPE
                and not command_text.lower().strip().startswith("cheat ")):
            resolution = interpret_clarification_answer(
                pending_clarification, command_text)
            world.dialogue_manager.pop()
            if resolution["kind"] == "cancel":
                return build_base_response(
                    world, success=True,
                    message="Berthier nods. \"Very well, Sire — the order is withdrawn.\"",
                    action_info={
                        "cost": 0,
                        "remaining": int(world.actions_remaining),
                        "turn_advanced": False,
                        "new_turn": None,
                    })
            if resolution["kind"] == "command":
                print(f"[CLARIFICATION] Resolved answer '{request.command}' "
                      f"-> '{resolution['command']}'")
                command_text = resolution["command"]

        # ════════════════════════════════════════════════════════════
        # PENDING STRATEGIC INTERRUPT CHECK (Phase 5.2-D)
        # If a marshal has a pending interrupt (cannon fire, blocked path),
        # try to map the player's text input to a response choice.
        # This prevents the command from being parsed as a new order.
        # ════════════════════════════════════════════════════════════
        for m in world.get_player_marshals():
            pending = getattr(m, 'pending_interrupt', None)
            if pending:
                cmd_lower = command_text.strip().lower()

                # ── Guard: if command addresses a DIFFERENT marshal, skip ──
                # "grouchy march to brittany" should NOT be routed as
                # Davout's interrupt response just because "march to" matches.
                known_marshal_names = [
                    pm.name.lower() for pm in world.get_player_marshals()
                ]
                addressed_other = any(
                    name in cmd_lower
                    for name in known_marshal_names
                    if name != m.name.lower()
                )
                if addressed_other:
                    # Command is for a different marshal — clear stale interrupt
                    # and let it parse normally
                    m.pending_interrupt = None
                    continue

                options = pending.get("options", [])
                interrupt_type = pending.get("interrupt_type", "")

                # Map natural language to response choices
                choice = None
                if any(kw in cmd_lower for kw in ["investigate", "march to", "guns", "attack", "charge", "join"]):
                    choice = "investigate" if "investigate" in options else "attack" if "attack" in options else None
                elif any(kw in cmd_lower for kw in ["continue", "ignore", "keep going", "carry on", "press on"]):
                    choice = "continue_order" if "continue_order" in options else None
                elif any(kw in cmd_lower for kw in ["hold", "stay", "stop", "wait", "halt"]):
                    choice = "hold_position" if "hold_position" in options else None
                elif any(kw in cmd_lower for kw in ["go around", "reroute", "avoid"]):
                    choice = "go_around" if "go_around" in options else None
                elif any(kw in cmd_lower for kw in ["cancel", "abort", "belay"]):
                    choice = "cancel_order" if "cancel_order" in options else None

                if choice:
                    print(f"[INTERRUPT ROUTE] Routing '{request.command}' -> "
                          f"{m.name} {interrupt_type} response: {choice}")
                    from backend.commands.strategic import StrategicOrderProcessor
                    strategic_exec = StrategicOrderProcessor(executor)
                    result = strategic_exec.handle_response(
                        m.name, interrupt_type, choice, world, game_state)
                    return _build_result_response(result, world)

        # ════════════════════════════════════════════════════════════
        # CR-4: CONTEXT CARRYOVER — resolve shorthand references ("again",
        # "same target", "him"/"there", "not you, Davout") against the
        # command history BEFORE the parser sees them (Golden Rule 6: the
        # rewrite is fully deterministic). A reference with nothing to
        # resolve against gets a helpful in-character reply rather than a
        # confusing parse failure. Runs after the clarification-answer and
        # interrupt steps so those terse answers are never treated as
        # references.
        # ════════════════════════════════════════════════════════════
        from backend.commands.context_carryover import (
            resolve_context_references,
            try_focus_reissue,
        )
        # Safe during a pending diplomatic dialogue too: a terse decline
        # ("no"/"nope"/"not you") with no resolvable marshal falls through as
        # a pass, so it still reaches the dialogue routing; only an explicit
        # reference ("again", "not you, Davout") rewrites — and the resolved
        # military command is then blocked by any hard-stop just as the raw
        # input would be. (Objection answers use /respond_to_objection.)
        carryover = resolve_context_references(command_text, world)
        if carryover["kind"] == "error":
            return build_base_response(
                world, success=False, message=carryover["message"],
                action_info={
                    "cost": 0,
                    "remaining": int(world.actions_remaining),
                    "turn_advanced": False,
                    "new_turn": None,
                })
        if carryover["kind"] == "rewrite":
            print(f"[CARRYOVER] '{command_text}' -> '{carryover['command']}'")
            command_text = carryover["command"]

        # Parse command
        # Build LLM-compatible game state for command parsing
        llm_game_state = get_llm_game_state()
        parsed = parser.parse(command_text, llm_game_state, world=world)
        if parsed.get("success") and isinstance(parsed.get("command"), dict):
            if request.action:
                parsed["command"]["action"] = request.action
            if request.target_nation:
                parsed["command"]["target_nation"] = request.target_nation
            if request.war_id:
                parsed["command"]["war_id"] = request.war_id
        print(f"[OK] Parsed: {parsed.get('command', {}).get('action', 'unknown')}")

        # ════════════════════════════════════════════════════════════
        # COMMAND HISTORY: Track parsed commands for LLM repetition detection
        # (live-mode prompt) AND CR-4 context carryover ("again"/"same
        # target"/"him"/"there"/"not you, X"). CR-4 decision: record in BOTH
        # mock and live modes — carryover must resolve with the fast/mock
        # parser too, and the live-only repetition prompt is unaffected.
        # ``target`` is recorded (CR-4) so "same target"/"him"/"there" and
        # "not you, X" reconstruction have an objective to reference. Recorded
        # only when the command will execute as a REAL field order — NOT when
        # it is consumed as a dialogue answer (a response that happens to
        # parse as a valid action must not be recorded as a phantom order).
        # A soft-stop mailbox dialogue (incoming proposal / settlement offer)
        # does not block ordinary orders, so an order typed while one is
        # pending still executes (soft-stop pass-through) and MUST be recorded;
        # only inputs matching the dialogue's own options are answers.
        # ════════════════════════════════════════════════════════════
        _consumed_as_dialogue_answer = False
        if world.pending_diplomatic_dialogue is not None:
            if world.dialogue_manager.is_hard_stop():
                _consumed_as_dialogue_answer = True
            else:
                _raw_lower = command_text.lower()
                for _opt in world.pending_diplomatic_dialogue.get("options", []):
                    _lbl = (_opt.get("label") or "").lower().strip()
                    _act = (_opt.get("action") or "").lower().strip()
                    if (_lbl and _lbl in _raw_lower) or (_act and _act in _raw_lower):
                        _consumed_as_dialogue_answer = True
                        break
        if parsed.get("success") and not _consumed_as_dialogue_answer:
            _parsed_command = parsed.get("command", {})
            world.add_to_command_history({
                "raw_input": command_text,
                "marshal": _parsed_command.get("marshal"),
                "action": _parsed_command.get("action"),
                "target": _parsed_command.get("target"),
                "turn": int(world.current_turn),
            })

        # ════════════════════════════════════════════════════════════
        # CR-5: PERSONALITY-BIASED DISAMBIGUATION (COMMAND_ROBUSTNESS_SPEC §6).
        # A delegation verb ("Soult, deal with Mack") cedes the method to the
        # marshal; the concrete action is inferred from his CHARACTER, and the
        # routing here is DETERMINISTIC (Golden Rule 6 — the executor is never
        # LLM-driven):
        #   - literal / neutral / mock  -> ASK the Emperor (attack or observe?),
        #     overriding whatever the live LLM guessed for a literal marshal.
        #   - cautious                  -> observe first; a battle action the
        #     live LLM produced is CLAMPED to scout (he never assaults on a
        #     vague order, §6.3c) + a soft note that names his character.
        #   - aggressive                -> NOT YET ENABLED (rides the ungated
        #     lethal attack-on-arrival seam) — degrades to ASK until Phase 3's
        #     gate + Phase 4 flip. route_arm() applies that phase gate.
        # Guarded by _consumed_as_dialogue_answer so a hard-stop dialogue answer
        # is never hijacked; runs AFTER CR-4 carryover + history recording.
        # ════════════════════════════════════════════════════════════
        _cautious_note = None
        _delegation_hint = None
        if not _consumed_as_dialogue_answer:
            _deleg = detect_delegation(world, command_text,
                                       parsed.get("command"))
            if _deleg is not None:
                # §6.7: once-per-campaign discoverability hint on first delegation
                _delegation_hint = maybe_delegation_hint(world)
                _arm = route_arm(_deleg.personality,
                                 parse_resolved_to_action(parsed))
                if _arm == "cautious":
                    # Deterministic: a cautious marshal observes first (§6.2).
                    # Re-issue an explicit scout at the OBSERVE target (the
                    # enemy's location) — a plain re-parse, no LLM (Golden Rule
                    # 6). This also corrects the live LLM's unreliable target
                    # resolution (playtest: "deal with Kutuzov" mis-scouted
                    # Algarve); the detector's target is authoritative.
                    _reissue = f"{_deleg.marshal} scout {_deleg.scout_target}"
                    parsed = parser.parse(_reissue, llm_game_state, world=world)
                    command_text = _reissue
                    _cautious_note = describe_cautious_delegation(
                        _deleg, "scout")
                    print(f"[CR-5] Delegation CAUTIOUS ({_deleg.marshal}) "
                          f"-> scout {_deleg.scout_target}")
                elif _arm == "ask":
                    _deleg_clar = build_delegation_clarification(
                        world, _deleg, command_text)
                    if _delegation_hint:
                        _deleg_clar["message"] = (
                            f"{_deleg_clar['message']}\n\n{_delegation_hint}")
                    _deleg_clar["clarification_registered"] = (
                        register_pending_clarification(
                            world, _deleg_clar, command_text))
                    print(f"[CR-5] Delegation ASK "
                          f"({_deleg.marshal}/{_deleg.personality or 'unset'}) "
                          f"-> frontend")
                    return _build_result_response(_deleg_clar, world)

        # ════════════════════════════════════════════════════════════
        # DIPLOMATIC DIALOGUE RESPONSE ROUTING (Audit fix)
        # Must run BEFORE Berthier parse recovery — dialogue keywords
        # like "accept"/"reject" fail parsing and would trigger
        # Berthier recovery early return, preventing dialogue routing.
        # ════════════════════════════════════════════════════════════
        # Cheat commands bypass dialogue guard
        is_cheat = parsed.get("success") and parsed.get("command", {}).get("action") == "cheat"

        if world.pending_diplomatic_dialogue is not None and not is_cheat:
            raw_lower = command_text.lower()
            is_hard_stop = world.dialogue_manager.is_hard_stop()

            _DIALOGUE_RESPONSE_KEYWORDS = [
                "accept", "reject", "decline", "counter",
                "proceed", "cancel", "confront", "overlook",
                "apologize", "replace", "continue", "invest", "garrison",
                "send", "execute", "reconsider", "modify",
                "honor", "side", "dismiss",
                "harsh", "generous", "adjust",  # Proposal confirm popup actions
                "nudge", "insist",  # PL-23: Drafting pushback actions
                "deliver", "ultimatum", "customize", "demand",  # PL-14/15: Ultimatum wizard
                "confirm", "back out", "back_out", "revise", "revise_terms",  # Imperial settlement
                "elaborate", "review", "consider",  # Template actions (GAP-1)
                "begin",  # Mission start (GAP-4/6)
                "yes", "agree", "start", "more", "no", "never mind",
            ]

            matched_keyword = None
            if is_hard_stop:
                # Hard-stop: broad substring keyword matching (current behavior)
                for keyword in _DIALOGUE_RESPONSE_KEYWORDS:
                    if keyword in raw_lower:
                        matched_keyword = keyword
                        break
            else:
                # PL-27: Soft-stop — only match against actual dialogue options
                # to avoid capturing unrelated commands like "garrison"
                dialogue = world.pending_diplomatic_dialogue
                for opt in dialogue.get("options", []):
                    label = (opt.get("label") or "").lower().strip()
                    action = (opt.get("action") or "").lower().strip()
                    if label and label in raw_lower:
                        matched_keyword = label
                        break
                    if action and action in raw_lower:
                        matched_keyword = action
                        break

            if matched_keyword:
                print(f"[DIPLOMATIC] Routing dialogue response: {matched_keyword}")
                result = executor.handle_diplomatic_dialogue_response(
                    matched_keyword, game_state)
            elif is_hard_stop:
                # Hard-stop: label matching fallback, then executor (which blocks)
                print(f"[DIPLOMATIC] Hard-stop fallback label-match: {raw_lower}")
                result = executor.handle_diplomatic_dialogue_response(
                    command_text, game_state)
                msg = (result or {}).get("message", "")
                if "Please choose an option" in msg:
                    result = executor.execute(parsed, game_state)
            else:
                # PL-27: Soft-stop — no dialogue keyword match, execute normally
                print(f"[DIPLOMATIC] Soft-stop pass-through: {raw_lower}")
                result = executor.execute(parsed, game_state)
        else:
            # m1: Dialogue keywords typed with no active dialogue — clear message
            raw_lower_check = command_text.lower().strip()
            # Only keywords that are NEVER valid game commands.
            # Excludes: cancel (strategic order cancel), garrison, more, execute, start, yes, no
            _DIALOGUE_ONLY_KEYWORDS = [
                "accept", "reject", "decline", "counter",
                "proceed", "confront", "overlook",
                "apologize", "replace", "reconsider", "modify",
                "honor", "side", "dismiss",
                "harsh", "generous", "adjust",
                "nudge", "insist",  # PL-23: Drafting pushback
                "elaborate", "review", "consider",
                "begin",
                "agree", "never mind",
            ]
            if raw_lower_check in _DIALOGUE_ONLY_KEYWORDS:
                return build_base_response(
                    world, success=False,
                    message="Berthier: \"There is no pending diplomatic matter to respond to, Sire.\"",
                    action_info={
                        "cost": 0,
                        "remaining": int(world.actions_remaining),
                        "turn_advanced": False,
                        "new_turn": None,
                    })

            # ════════════════════════════════════════════════════════════
            # CR-2: UNKNOWN-NAME CLARIFICATION — a parse failure that
            # carries structured candidates ("Murat, charge" on a world
            # without Murat; "Davut, attack") becomes a one-question
            # did-you-mean instead of a dead-end error. Before CR-2 these
            # errors fell through the executor into the generic Berthier
            # shrug and the computed suggestions were dropped entirely.
            # ════════════════════════════════════════════════════════════
            if not parsed.get("success") and parsed.get("candidates"):
                name_clarification = build_unknown_name_clarification(
                    world,
                    parsed.get("unknown_name") or "",
                    parsed["candidates"],
                    command_text,
                    parsed.get("kind") or "marshal_not_found",
                    partial_action=parsed.get("partial_action"),
                )
                if name_clarification is not None:
                    name_clarification["clarification_registered"] = (
                        register_pending_clarification(
                            world, name_clarification, command_text))
                    print("[CLARIFICATION] Unknown-name question -> frontend")
                    return _build_result_response(name_clarification, world)

            # ════════════════════════════════════════════════════════════
            # BERTHIER PARSE RECOVERY: Replace generic "Unknown action"
            # with in-character Berthier clarification. Only fires for
            # type-1 parse failures; marshal typos & validation errors
            # pass through unchanged.
            # ════════════════════════════════════════════════════════════
            if not parsed.get("success") and (parsed.get("error") or "").startswith("Unknown action"):
                berthier_msg = parser.llm.generate_berthier_recovery(
                    raw_command=command_text,
                    game_state=llm_game_state,
                    partial_parse={
                        "recognized_marshal": parsed.get("partial_marshal"),
                        "recognized_target": parsed.get("partial_target"),
                        "raw_input": parsed.get("raw_input", command_text),
                    },
                    # CR-3(c): the parse-stage LLM call already failed —
                    # don't stack a second blocking call on this request
                    skip_llm=bool(parsed.get("llm_error")),
                )
                return build_base_response(
                    world, success=False, message=berthier_msg,
                    action_info={
                        "cost": 0,
                        "remaining": int(world.actions_remaining),
                        "turn_advanced": False,
                        "new_turn": None,
                    })

            # Execute command
            result = executor.execute(parsed, game_state)

        # ════════════════════════════════════════════════════════════
        # CR-2: parser warnings (sequential-order drop note, non-standard
        # marshal note) were computed and then never surfaced — append them
        # to the player-visible message ("every input gets a response").
        # Sits BEFORE the early-return checks so diplomatic dialogues and
        # popup paths carry the note too; objection popups (success=False)
        # deliberately skip it — the objection dominates, and the sequel
        # note re-surfaces if the reissued/proceeded command re-parses.
        # ════════════════════════════════════════════════════════════
        if result.get("success") and parsed.get("warning"):
            result["message"] = (
                f"{result.get('message') or ''}\n\n"
                f"Berthier: \"{parsed['warning']}\""
            ).strip()

        # CR-5: a cautious delegation executed as an observe-first order —
        # append the character-naming soft note (§6.3c legibility) so the
        # player sees WHY the marshal scouted and can press the assault. The
        # once-per-campaign discoverability hint (§6.7) rides the same message.
        if _cautious_note and isinstance(result, dict) and result.get("success"):
            _tail = _cautious_note
            if _delegation_hint:
                _tail = f"{_cautious_note}\n\n{_delegation_hint}"
            result["message"] = (
                f"{(result.get('message') or '').strip()}\n\n{_tail}"
            ).strip()

        # ════════════════════════════════════════════════════════════
        # BERTHIER EXECUTOR RECOVERY: Catch "Marshal 'None' not found"
        # This happens when a valid action is parsed but no marshal was
        # identified (e.g., "move to Belgium" without naming a marshal).
        # CR-2: upgraded to the one-question marshal-choice clarification
        # ("Which marshal shall march to Belgium, Sire?") with reissue
        # options; Berthier prose remains the no-candidate fallback.
        # ════════════════════════════════════════════════════════════
        if not result.get("success") and "Marshal 'None' not found" in (result.get("message") or ""):
            # CR-4: PERSISTENT COMMAND FOCUS — a bare specific order ("hold",
            # "move to Vienna") defaults to the marshal the player is already
            # commanding instead of re-asking. Only fires at this seam (the
            # missing-executor case), so it never overrides an explicitly-
            # addressed marshal or a general/auto-assign order; falls through
            # to the CR-2 clarification when no eligible focus exists.
            focus_handled = False
            if parsed.get("success"):
                focus_outcome = try_focus_reissue(
                    world, parser, executor, parsed, command_text,
                    game_state, llm_game_state)
                if focus_outcome is not None:
                    parsed, command_text, result = focus_outcome
                    print(f"[FOCUS] Reissued bare order to "
                          f"{parsed.get('command', {}).get('marshal')}")
                    focus_handled = True
                    # CR-4 (audit): the parser-warning surfacing block ran
                    # above on the OLD (failed) result, so the reissued
                    # command's own warning (e.g. the sequential-clause drop
                    # note) would be lost — re-surface it here so a focus
                    # reissue matches an explicitly-addressed order.
                    if result.get("success") and parsed.get("warning"):
                        result["message"] = (
                            f"{result.get('message') or ''}\n\n"
                            f"Berthier: \"{parsed['warning']}\""
                        ).strip()

            if not focus_handled:
                if parsed.get("success"):
                    marshal_clarification = build_marshal_choice_clarification(
                        world, parsed, command_text)
                    if marshal_clarification is not None:
                        marshal_clarification["clarification_registered"] = (
                            register_pending_clarification(
                                world, marshal_clarification, command_text))
                        print("[CLARIFICATION] Marshal-choice question -> frontend")
                        return _build_result_response(marshal_clarification, world)
                berthier_msg = parser.llm.generate_berthier_recovery(
                    raw_command=command_text,
                    game_state=llm_game_state,
                    partial_parse={
                        "recognized_marshal": None,
                        "recognized_target": parsed.get("command", {}).get("target"),
                        "raw_input": command_text,
                    },
                    skip_llm=bool(parsed.get("llm_error")),  # CR-3(c)
                )
                return build_base_response(
                    world, success=False, message=berthier_msg,
                    action_info={
                        "cost": 0,
                        "remaining": int(world.actions_remaining),
                        "turn_advanced": False,
                        "new_turn": None,
                    })

        # ════════════════════════════════════════════════════════════
        # CHECK FOR OBJECTION: If awaiting player choice, return full result
        # Tactical objections: state == "awaiting_player_choice"
        # Strategic objections (Phase M): pending_objection == True
        # ════════════════════════════════════════════════════════════
        if result.get("state") == "awaiting_player_choice":
            print("[OBJECTION] TACTICAL OBJECTION - Returning full result to frontend")
            return _build_result_response(result, world)

        if result.get("pending_objection"):
            print("[OBJECTION] STRATEGIC OBJECTION (Phase M) - Returning full result to frontend")
            return _build_result_response(result, world)

        # ════════════════════════════════════════════════════════════
        # CHECK FOR CLARIFICATION: If awaiting clarification, return full result
        # CR-2: also register the question on the DialogueManager so the
        # player's next typed input can answer it (player path only — AI
        # commands never flow through this endpoint).
        # ════════════════════════════════════════════════════════════
        if result.get("state") == "awaiting_clarification":
            result["clarification_registered"] = (
                register_pending_clarification(world, result, command_text))
            print("[CLARIFICATION] Returning clarification popup to frontend")
            return _build_result_response(result, world)

        # ════════════════════════════════════════════════════════════
        # CHECK FOR GLORIOUS CHARGE: If pending, return full result for popup
        # ════════════════════════════════════════════════════════════
        if result.get("pending_glorious_charge"):
            print("GLORIOUS CHARGE PENDING - Returning full result to frontend")
            return _build_result_response(result, world)

        # ════════════════════════════════════════════════════════════
        # CHECK FOR STRATEGIC INTERRUPT: Blocked path, cannon fire popup
        # (Session 39: was missing — pending_interrupt dropped at response build)
        # ════════════════════════════════════════════════════════════
        if result.get("pending_interrupt"):
            print("[INTERRUPT] STRATEGIC INTERRUPT - Returning full result to frontend")
            return _build_result_response(result, world)

        # ════════════════════════════════════════════════════════════
        # CHECK FOR CAPTURE CHOICE (Phase 6.2.E): Plunder or Secure popup
        # ════════════════════════════════════════════════════════════
        if result.get("pending_capture_choice"):
            print("[CAPTURE] PLUNDER/SECURE CHOICE PENDING - Returning full result to frontend")
            return _build_result_response(result, world)

        # ════════════════════════════════════════════════════════════
        # CHECK FOR DIPLOMATIC DIALOGUE (Phase 8 Session 3)
        # ════════════════════════════════════════════════════════════
        if result.get("diplomatic_dialogue") or result.get("awaiting_diplomatic_response"):
            print("[DIPLOMATIC] Diplomatic dialogue - Returning full result to frontend")
            return _build_result_response(result, world)


        # ════════════════════════════════════════════════════════════
        # FEEDBACK GENERATION (Phase 5): Generate immersive feedback
        # Only for non-mock mode, successful player commands
        #
        # REQUIRED FIELDS FROM parser.parse() - see parser.py docstring:
        #   - parsed["mode"]: "mock" or "live"
        #   - parsed["strategic_score"]: 0-100 (controls morale/trust bonus)
        #   - parsed["ambiguity"]: 0-100 (controls clarity feedback)
        #
        # If these are missing, check parser.py return dict construction!
        # ════════════════════════════════════════════════════════════
        feedback = {}
        mode = parsed.get("mode", "mock")

        if mode != "mock" and result.get("success", False):
            from backend.ai.feedback import get_strategic_feedback, get_ambiguity_feedback

            # Get scores from parsed command
            strategic_score = parsed.get("strategic_score", 0)
            ambiguity_score = parsed.get("ambiguity", 0)
            print(f"[FEEDBACK DEBUG] mode={mode}, strategic_score={strategic_score}, ambiguity={ambiguity_score}")

            # Get marshal info - try result first, then parsed command
            marshal_name = result.get("marshal") or parsed.get("command", {}).get("marshal")
            if marshal_name:
                marshal = world.get_marshal(marshal_name)
                if marshal and marshal.nation == world.player_nation:
                    personality = getattr(marshal, 'personality', 'balanced')

                    # Generate feedback strings
                    strategic_text = get_strategic_feedback(strategic_score, marshal_name)
                    ambiguity_text = get_ambiguity_feedback(ambiguity_score, marshal_name, personality)

                    if strategic_text:
                        feedback["strategic"] = strategic_text
                    if ambiguity_text:
                        feedback["ambiguity"] = ambiguity_text

        response = _build_command_response(result, world, feedback)
        _apply_command_result_layers(response, result, world)
        return response
    except Exception as e:
        print(f"[ERROR]: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}",
            action_info={"remaining": int(world.actions_remaining)})


@app.get("/status")
def get_status():
    """Get current game status — Berthier's Intelligence Report (Session 34A)."""
    from backend.intel_report import generate_intel_report
    from backend.game_logic.war_status import build_active_wars
    report = generate_intel_report(world)
    report["game_state"] = world.get_filtered_game_state_summary()
    report["active_wars"] = build_active_wars(world)
    return report


# ============================================================
# DISOBEDIENCE SYSTEM API ENDPOINTS (Phase 2)
# ============================================================

@app.get("/pending_objection")
def get_pending_objection():
    """
    Get the current pending objection if any.

    Returns objection details including:
    - marshal: Name of objecting marshal
    - message: The objection message
    - severity: How serious the objection is
    - choices: Available responses (trust, insist, compromise)
    - alternative: Marshal's suggested alternative (if any)
    """
    if world.pending_objection is None:
        return {
            "has_pending": False,
            "message": "No pending objection"
        }

    objection = world.pending_objection
    from backend.display_names import ACTION_DISPLAY
    trigger = objection.get("trigger")
    return {
        "has_pending": True,
        "marshal": objection.get("marshal"),
        "message": objection.get("message"),
        "severity": int(objection.get("severity", 0.5) * 100),  # int % for Godot — no raw floats
        "type": objection.get("type", "major"),
        "trigger": trigger,
        "trigger_display": ACTION_DISPLAY.get(trigger, (trigger or "").replace("_", " ")) if trigger else "",
        "choices": ["trust", "insist", "compromise"] if objection.get("alternative") else ["trust", "insist"],
        "alternative": objection.get("alternative"),
        "original_order": objection.get("original_order")
    }


@app.post("/respond_to_objection")
def respond_to_objection(request: ObjectionResponse):
    """
    Respond to a marshal's objection.

    Args:
        request: ObjectionResponse with 'choice' field
            - 'trust': Accept marshal's judgment/alternative
            - 'insist': Override marshal and execute original order
            - 'compromise': Find middle ground (if available)

    Returns execution result after choice is processed.
    """
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        # Handle the objection response through executor
        result = executor.handle_objection_response(request.choice, game_state)

        response = build_base_response(
            world,
            success=result.get("success", False),
            message=result.get("message", "Response processed"),
            events=result.get("events", []),
            objection_resolved=result.get("objection_resolved", True),
            choice=result.get("choice"),
            trust_change=result.get("trust_change", 0),
            authority_change=result.get("authority_change", 0),
            disobeyed=result.get("disobeyed", False),
            action_info=result.get("action_info", {}),
            strategic_reports=result.get("strategic_reports", []),
        )
        if result.get("battle_report"):
            response["battle_report"] = result["battle_report"]

        # V2b: Defiance passthrough
        if result.get("defiance"):
            response["defiance"] = True
            response["defiance_action"] = result.get("defiance_action")
            response["defiance_outcome"] = result.get("defiance_outcome")
            # R7: Display-friendly versions for UI
            from backend.display_names import DEFIANCE_DISPLAY, DEFIANCE_OUTCOME_DISPLAY
            da = result.get("defiance_action", "")
            response["defiance_action_display"] = DEFIANCE_DISPLAY.get(da, da.replace("_", " ")) if da else ""
            do = result.get("defiance_outcome", "")
            response["defiance_outcome_display"] = DEFIANCE_OUTCOME_DISPLAY.get(do, do.replace("_", " ").title()) if do else ""
            response["berthier_text"] = result.get("berthier_text", "")
        # V2b: Authority event passthrough
        if result.get("authority_event"):
            response["authority_event"] = result["authority_event"]

        # Strategic interrupt: post-objection command may hit blocked path
        if result.get("pending_interrupt"):
            response["pending_interrupt"] = result["pending_interrupt"]
            response["requires_input"] = True

        # Redemption event: trust dropped to critical level
        if result.get("redemption_event"):
            response["state"] = "awaiting_redemption_choice"
            response["redemption_event"] = result["redemption_event"]
            world.pending_redemption = result["redemption_event"]
            print(f"[ALERT] REDEMPTION TRIGGERED for {result['redemption_event']['marshal']}")

        return response
    except Exception as e:
        print(f"[ERROR] handling objection response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.post("/respond_to_diplomatic_dialogue")
async def respond_to_diplomatic_dialogue(request: dict):
    """Respond to a diplomatic dialogue from Talleyrand (Phase 8 Session 3).

    Args:
        request: dict with 'choice' field (int 1-based index or str keyword)
    """
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        dialogue_before = world.pending_diplomatic_dialogue or {}
        choice = request.get("choice")
        # Re-front Slice 2: structured settlement Tier-2 affordances (dials /
        # coverage edits / focus) ride on per-court rows + rail buttons and
        # carry `scope` / `nation` params the keyword path cannot express.
        action_params = request.get("action_params")
        result = executor.handle_diplomatic_dialogue_response(
            choice, game_state, action_params=action_params,
        )

        # PF-1 / D2: pass the handler's own text through instead of swallowing
        # it behind a literal "Response processed". Settlement failure arms
        # speak through `talleyrand_text` (in character) and `error_display`
        # (humanized reason) and may omit `message`; the old `.get` default
        # printed "Response processed" in red with no explanation.
        response = build_base_response(
            world,
            success=result.get("success", False),
            message=(
                result.get("message")
                or result.get("talleyrand_text")
                or result.get("error_display")
                or "Response processed"
            ),
        )
        # PF-1 / D3: surface the failure fields so the client can render the
        # reason on a re-mounted dialogue instead of a silent no-op.
        for failure_key in ("error", "error_display", "validation_error",
                            "validation_detail", "validation_error_index"):
            if result.get(failure_key) is not None:
                response[failure_key] = result[failure_key]

        # Pass through diplomatic dialogue if a new one was generated
        if result.get("diplomatic_dialogue"):
            response["diplomatic_dialogue"] = result["diplomatic_dialogue"]
        elif (result.get("success")
              and world.proposal_result_popup is None
              and not result.get("suppress_proposal_result_popup")):
            # PL-14 safety net: If dialogue concluded (no new dialogue pushed)
            # and handler forgot to set proposal_result_popup, create one from
            # the result message so it shows as a Godot popup, not terminal text.
            msg = result.get("message", "")
            if msg and not result.get("awaiting_diplomatic_response"):
                proposal_result = {
                    "target_nation": result.get(
                        "target_nation", dialogue_before.get("target_nation", "")
                    ),
                    "proposal_type": "Diplomatic Action",
                    "outcome": _derive_proposal_result_outcome(result),
                    "message": msg,
                    "feedback": "",
                    "decision_reason": result.get("decision_reason", ""),
                }
                if result.get("peace_ratification_summary"):
                    proposal_result["peace_ratification_summary"] = result[
                        "peace_ratification_summary"
                    ]
                world.proposal_result_popup = proposal_result
                # Rebuild response to pick up the newly-set popup
                response = build_base_response(
                    world,
                    success=result.get("success", False),
                    message=result.get("message", "Response processed"),
                )

        _include_peace_ratification_summary(response, result)
        if result.get("settlement_result_feedback"):
            response["settlement_result_feedback"] = result["settlement_result_feedback"]
        if result.get("reopen_target"):
            response["reopen_target"] = result["reopen_target"]
        if result.get("must_reopen"):
            response["must_reopen"] = result["must_reopen"]
        if result.get("recovery_route"):
            response["recovery_route"] = result["recovery_route"]
        if result.get("war_detail_actionability"):
            response["war_detail_actionability"] = result["war_detail_actionability"]
        if result.get("terminal_recovery_copy"):
            response["terminal_recovery_copy"] = result["terminal_recovery_copy"]
        if result.get("error_display"):
            response["error_display"] = result["error_display"]
        return response
    except Exception as e:
        print(f"[ERROR] handling diplomatic dialogue response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.post("/respond_to_diplomatic_objection")
def respond_to_diplomatic_objection(request: DiplomaticObjectionResponse):
    """Respond to a Talleyrand objection popup without synthesizing a command string."""
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)

        result = executor.handle_diplomatic_objection_response(
            request.choice,
            game_state,
            action=request.action,
            target_nation=request.target_nation,
        )

        response = build_base_response(
            world,
            success=result.get("success", False),
            message=result.get("message", "Response processed"),
            events=result.get("events", []),
        )
        if result.get("diplomatic_dialogue"):
            response["diplomatic_dialogue"] = result["diplomatic_dialogue"]
        if result.get("awaiting_diplomatic_response"):
            response["awaiting_diplomatic_response"] = True
        return response
    except Exception as e:
        print(f"[ERROR] handling diplomatic objection response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.post("/capture_choice")
def capture_choice(request: CaptureChoiceResponse):
    """Respond to the plunder/secure choice after capturing a region (Phase 6.2.E).

    Args:
        request: CaptureChoiceResponse with 'choice' field ('plunder' or 'secure')
    """
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        result = executor.handle_capture_choice(request.choice, game_state)

        return build_base_response(
            world,
            success=result.get("success", False),
            message=result.get("message", "Choice processed"),
            events=result.get("events", []),
            capture_choice=result.get("capture_choice"),
        )
    except Exception as e:
        print(f"ERROR handling capture choice: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.post("/respond_to_redemption")
def respond_to_redemption(request: RedemptionResponse):
    """
    Respond to a redemption event (trust at critical low).

    Args:
        request: RedemptionResponse with 'choice' field
            - 'grant_autonomy': Marshal acts independently for 3 turns
            - 'dismiss': Remove marshal, transfer troops
            - 'demand_obedience': Keep marshal but high disobey chance

    Returns result of the redemption choice.
    """
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        # Check for pending redemption
        if not hasattr(world, 'pending_redemption') or world.pending_redemption is None:
            return build_base_response(
                world, success=False, message="No redemption event pending.")

        redemption_event = world.pending_redemption

        # Validate choice (Phase 3: administrative_role replaces demand_obedience)
        valid_choices = ['grant_autonomy', 'administrative_role', 'dismiss']
        if request.choice not in valid_choices:
            return build_base_response(
                world, success=False,
                message=f"Invalid choice: '{request.choice}'. Valid: {', '.join(valid_choices)}")

        # Process the redemption response
        result = world.disobedience_system.handle_redemption_response(
            redemption_event=redemption_event,
            choice=request.choice,
            game_state=game_state
        )

        # Clear pending redemption
        world.pending_redemption = None

        return build_base_response(
            world,
            success=result.get("success", False),
            message=result.get("message", "Redemption processed"),
            choice=request.choice,
            autonomous=result.get("autonomous", False),
            autonomy_turns=result.get("autonomy_turns", 0),
            dismissed=result.get("dismissed", False),
            administrative=result.get("administrative", False),
            new_max_actions=result.get("new_max_actions", 0),
            troops_frozen=result.get("troops_frozen", 0),
            authority_bonus=result.get("authority_bonus", 0),
        )
    except Exception as e:
        print(f"[ERROR] handling redemption response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.get("/pending_redemption")
def get_pending_redemption():
    """
    Get the current pending redemption event if any.

    Returns redemption details including:
    - marshal: Name of marshal with broken trust
    - trust: Current trust level
    - options: Available choices
    """
    if not hasattr(world, 'pending_redemption') or world.pending_redemption is None:
        return {
            "has_pending": False,
            "message": "No pending redemption event"
        }

    redemption = world.pending_redemption
    return {
        "has_pending": True,
        "marshal": redemption.get("marshal"),
        "trust": redemption.get("trust"),
        "message": redemption.get("message"),
        "options": redemption.get("options", [])
    }


@app.post("/respond_to_glorious_charge")
def respond_to_glorious_charge(request: GloriousChargeResponse):
    """
    Respond to a Glorious Charge popup (Phase 3 Cavalry Recklessness).

    Args:
        request: GloriousChargeResponse with 'choice' field
            - 'charge': Execute Glorious Charge (2x damage dealt AND taken)
            - 'restrain': Normal attack (recklessness continues to build)

    Returns result of the charge/restrain choice.
    """
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        # Validate choice
        valid_choices = ['charge', 'restrain']
        if request.choice not in valid_choices:
            return build_base_response(
                world, success=False,
                message=f"Invalid choice: '{request.choice}'. Valid: {', '.join(valid_choices)}")

        # Process the response through executor
        result = executor.respond_to_glorious_charge(request.choice, world)

        response = build_base_response(
            world,
            success=result.get("success", False),
            message=result.get("message", "Charge processed"),
            events=result.get("events", []),
            choice=request.choice,
        )
        if result.get("battle_report"):
            response["battle_report"] = result["battle_report"]
        return response
    except Exception as e:
        print(f"[ERROR] handling Glorious Charge response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.post("/strategic_response")
def handle_strategic_response(request: StrategicInterruptResponse):
    """
    Respond to a strategic command interrupt (Phase D).

    Called when a marshal's strategic order hits an interrupt that requires
    player input (cannon fire, blocked path, ally moving).

    Args:
        request: StrategicInterruptResponse with marshal_name, response_type, choice

    Returns execution result after choice is processed.
    """
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        from backend.commands.strategic import StrategicOrderProcessor
        strategic_exec = StrategicOrderProcessor(executor)
        result = strategic_exec.handle_response(
            request.marshal_name, request.response_type,
            request.choice, world, game_state
        )

        response = build_base_response(
            world,
            success=result.get("success", False),
            message=result.get("message", "Response processed"),
            order_cleared=result.get("order_cleared", False),
            trust_change=result.get("trust_change", 0),
            action_taken=result.get("action_taken"),
        )
        # F1b: surface the same combat extras the direct /command attack path shows
        # (reinforcement narration, battle report, etc.) so the "attack anyway"
        # interrupt path is as legible as a direct attack.
        _copy_truthy_result_fields(response, result, _COMMAND_RESULT_SIMPLE_FIELDS)
        # Redemption event from strategic trust penalty
        if result.get("redemption_event"):
            response["state"] = "awaiting_redemption_choice"
            response["redemption_event"] = result["redemption_event"]
            world.pending_redemption = result["redemption_event"]
            print(f"[ALERT] REDEMPTION TRIGGERED for {result['redemption_event']['marshal']}")
        return response
    except Exception as e:
        print(f"[ERROR] handling strategic response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.get("/authority_status")
def get_authority_status():
    """
    Get the current authority tracker status.

    Returns:
    - authority: Current authority level (0-100)
    - label: Authority status label (e.g., "Divine Right", "Questionable")
    - trust_modifier: Modifier affecting trust gains
    - obedience_modifier: Modifier affecting marshal obedience
    - recent_responses: Last few player responses to objections
    """
    authority = world.authority_tracker
    return {
        "authority": int(authority.authority),
        "label": authority.get_authority_label(),
        "trust_modifier": int(authority.get_trust_gain_modifier() * 100),  # As percentage (e.g., 80 = 0.8x)
        "obedience_modifier": int(authority.get_obedience_modifier() * 100),  # As percentage
        "recent_responses": list(authority.recent_responses[-5:])  # Last 5 responses
    }


@app.get("/marshal_trust/{marshal_name}")
def get_marshal_trust(marshal_name: str):
    """
    Get trust and disobedience info for a specific marshal.

    Returns:
    - name: Marshal name
    - trust: Current trust value (0-100)
    - trust_label: Trust status label (e.g., "Loyal", "Strained")
    - vindication_score: How often marshal has been proven right (-5 to +5)
    - recent_battles: Last 3 battle results
    - recent_overrides: Recent times player overrode marshal
    """
    marshal = world.get_marshal(marshal_name)
    if not marshal:
        return {
            "success": False,
            "message": f"Marshal '{marshal_name}' not found"
        }

    # Fog guard: only return data for player marshals
    if marshal.nation != world.player_nation:
        return {
            "success": False,
            "message": f"No intelligence available on {marshal_name}"
        }

    return {
        "success": True,
        "name": marshal.name,
        "trust": int(marshal.trust.value) if hasattr(marshal, 'trust') else 70,
        "trust_label": marshal.trust.get_label() if hasattr(marshal, 'trust') else "Unknown",
        "vindication_score": int(getattr(marshal, 'vindication_score', 0)),
        "recent_battles": list(getattr(marshal, 'recent_battles', [])),
        "recent_overrides": list(getattr(marshal, 'recent_overrides', [])),
        "personality": marshal.personality
    }


@app.get("/debug_marshal/{marshal_name}")
def debug_marshal(marshal_name: str):
    """
    DEBUG ENDPOINT: Get comprehensive marshal data for debugging disobedience system.

    Returns:
    - All trust/vindication/authority data
    - Personality details
    - Recent decision history
    - Last objection severity
    """
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug endpoints disabled"}
    marshal = world.get_marshal(marshal_name)
    if not marshal:
        return {
            "success": False,
            "message": f"Marshal '{marshal_name}' not found",
            "available_marshals": [m.name for m in world.get_player_marshals()]
        }

    # Get vindication tracker data
    vindication_data = world.vindication_tracker.get_vindication_data(marshal_name)

    return {
        "success": True,
        "marshal": marshal.name,
        "personality": {
            "type": marshal.personality,
            "description": {
                "aggressive": "Favors bold attacks, objects to caution",
                "cautious": "Prefers defensive positions, objects to risky moves",
                "literal": "Follows orders precisely, objects to vague commands"
            }.get(marshal.personality, "Unknown")
        },
        "trust": {
            "value": int(marshal.trust.value) if hasattr(marshal, 'trust') else 70,
            "label": marshal.trust.get_label() if hasattr(marshal, 'trust') else "Unknown",
            "threshold_for_objection": "Trust affects objection likelihood"
        },
        "vindication": {
            "score": vindication_data.get("score", 0),
            "recent_overrides": vindication_data.get("recent_overrides", []),
            "recent_battles": vindication_data.get("recent_battles", []),
            "has_pending": world.vindication_tracker.has_pending(marshal_name)
        },
        "authority_context": {
            "player_authority": int(world.authority_tracker.authority),
            "authority_label": world.authority_tracker.get_authority_label(),
            "affects_trust_gains": int(world.authority_tracker.get_trust_gain_modifier() * 100)  # int % for Godot
        },
        "location": marshal.location,
        "strength": int(marshal.strength),
        "morale": int(marshal.morale)
    }


def _get_fortify_state_safe(marshal) -> dict:
    """Safe wrapper for _get_fortify_state with error handling."""
    try:
        return _get_fortify_state(marshal)
    except Exception as e:
        print(f"[FORTIFY_STATE_ERROR] Exception for {getattr(marshal, 'name', 'unknown')}: {e}")
        return {
            "direction": "error",
            "floor": 0,
            "turns_until_decay": -1,
            "turns_fortified": 0,
            "error": str(e)
        }


def _get_fortify_state(marshal) -> dict:
    """
    Get fortification state for display (Phase 3 - Fortify Decay).

    Returns:
        Dict with direction, floor, turns_until_decay for frontend display.
    """
    if not getattr(marshal, 'fortified', False):
        return {
            "direction": "none",
            "floor": 0,
            "turns_until_decay": -1,
            "turns_fortified": 0
        }

    # DEBUG: Print fortify state calculation
    print(f"[FORTIFY_STATE_DEBUG] {marshal.name}: fortified=True, defense_bonus={getattr(marshal, 'defense_bonus', 0)}, turns_fortified={getattr(marshal, 'turns_fortified', 0)}")

    from backend.models.personality_modifiers import get_max_fortify_bonus

    personality = getattr(marshal, 'personality', 'unknown')
    is_cavalry = getattr(marshal, 'cavalry', False)
    current_bonus = getattr(marshal, 'defense_bonus', 0)
    turns_fortified = getattr(marshal, 'turns_fortified', 0)
    max_bonus = get_max_fortify_bonus(personality)

    # Decay configuration by personality
    decay_config = {
        "aggressive": {"start": 4, "rate": 0.02, "floor": 0.0},
        "balanced": {"start": 6, "rate": 0.01, "floor": 0.0},
        "cautious": {"start": 8, "rate": 0.01, "floor": 0.05},
        "literal": {"start": 8, "rate": 0.01, "floor": 0.05},
    }
    default_decay = {"start": 6, "rate": 0.01, "floor": 0.0}
    decay_settings = decay_config.get(personality, default_decay)

    floor_percent = int(decay_settings["floor"] * 100)

    # Cavalry uses different system (auto-unfortify at turn 3)
    if is_cavalry:
        turns_until_unfortify = max(0, 3 - turns_fortified)
        return {
            "direction": "cavalry_limit",
            "floor": 0,
            "turns_until_decay": turns_until_unfortify,
            "turns_fortified": turns_fortified
        }

    # Determine direction
    decay_starts = decay_settings["start"]
    turns_until_decay = max(0, decay_starts - turns_fortified)

    if turns_fortified >= decay_starts:
        if current_bonus <= decay_settings["floor"]:
            direction = "at_floor"
        else:
            direction = "decaying"
    elif current_bonus >= max_bonus:
        # At max, waiting for decay to start
        direction = "stable"
    else:
        direction = "growing"

    result = {
        "direction": direction,
        "floor": floor_percent,
        "turns_until_decay": turns_until_decay,
        "turns_fortified": turns_fortified
    }
    print(f"[FORTIFY_STATE_DEBUG]   -> direction={direction}, floor={floor_percent}%, turns_until_decay={turns_until_decay}")
    return result


# ════════════════════════════════════════════════════════════
# SAVE/LOAD ENDPOINTS (Phase 6: Save/Load System)
# ════════════════════════════════════════════════════════════

def _validate_save_filename(filename: str) -> bool:
    """Reject filenames with path traversal characters."""
    if ".." in filename or "/" in filename or "\\" in filename:
        return False
    # Verify resolved path stays within saves dir
    resolved = (save_manager.SAVE_DIR / filename).resolve()
    return str(resolved).startswith(str(save_manager.SAVE_DIR.resolve()))


@app.post("/save")
async def save_endpoint(request: SaveRequest):
    """Save current game state."""
    global world
    # 3D-2: Validate save filename before passing to save_game
    if request.save_name and not _validate_save_filename(request.save_name):
        return build_base_response(world, success=False, message="Invalid save name")
    try:
        result = save_game(world, save_name=request.save_name)
        return build_base_response(world, **{k: v for k, v in result.items() if k != "new_state"})
    except Exception as e:
        print(f"[ERROR] handling save: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(world, success=False, message=f"Save failed: {str(e)}")


@app.post("/new_game")
async def new_game_endpoint():
    """Start a fresh campaign without restarting the backend process."""
    try:
        player_nation = get_player_nation(world)
        new_world = _reset_world_state(player_nation=player_nation)
        autosave_result = autosave(new_world)
        autosave_ok = bool(autosave_result.get("success", False))
        message = "New campaign started."
        if autosave_ok:
            message += " Autosave refreshed."
        else:
            message += " Warning: autosave refresh failed."
        return build_base_response(
            new_world,
            message=message,
            new_game=True,
            autosave_success=autosave_ok,
            autosave_message=autosave_result.get("message", ""),
        )
    except Exception as e:
        print(f"[ERROR] handling new_game: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(world, success=False, message=f"New game failed: {str(e)}")


@app.post("/load")
async def load_endpoint(request: LoadRequest):
    """Load a saved game. Replaces current game state."""
    if not _validate_save_filename(request.filename):
        return {"success": False, "message": "Invalid save filename"}
    filepath = save_manager.SAVE_DIR / request.filename
    result = load_game(filepath)
    if result["success"]:
        _set_active_world(result["world"])
        return build_base_response(world, message=result["message"])
    return build_base_response(world, success=False, message=result["message"])


@app.get("/saves")
async def list_saves_endpoint():
    """List all available save files."""
    saves = list_saves()
    return {"saves": saves}


@app.post("/delete_save")
async def delete_save_endpoint(request: DeleteSaveRequest):
    """Delete a save file."""
    if not _validate_save_filename(request.filename):
        return {"success": False, "message": "Invalid save filename"}
    filepath = save_manager.SAVE_DIR / request.filename
    result = delete_save(filepath)
    return build_base_response(world, **{k: v for k, v in result.items() if k != "new_state"})


# ════════════════════════════════════════════════════════════
# CAMPAIGN LOG ENDPOINT (Phase 6.5)
# ════════════════════════════════════════════════════════════

@app.get("/campaign_log")
def get_campaign_log():
    """Get fog-filtered campaign event log grouped by turn (descending)."""
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    from backend.campaign_log import filter_campaign_log, format_event_oneliner, CATEGORY_MAP

    filtered = filter_campaign_log(world.event_log, world)

    # Group by turn descending
    turns = {}
    for event in filtered:
        t = event.get("turn", 0)
        if t not in turns:
            turns[t] = []
        turns[t].append({
            **{k: (int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v)
               for k, v in event.items() if k != "battle_report"},
            "display": format_event_oneliner(event),
            "category": CATEGORY_MAP.get(event.get("type", ""), "unknown"),
        })

    # Hide empty turns (0 visible events after fog filtering)
    sorted_turns = [{"turn": int(t), "events": evts}
                    for t, evts in sorted(turns.items(), reverse=True)
                    if evts]
    return {"success": True, "turns": sorted_turns, "current_turn": int(world.current_turn)}


# ════════════════════════════════════════════════════════════
# DISPATCH RE-READ ENDPOINT (Session A)
# ════════════════════════════════════════════════════════════

@app.get("/dispatch")
def get_dispatch():
    """Get the last morning dispatch for re-read screen."""
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    dispatch = world.last_morning_dispatch
    if not dispatch:
        return {"success": True, "dispatch": {}}
    return {"success": True, "dispatch": dispatch}


# ════════════════════════════════════════════════════════════
# STRATEGIC LEDGER ENDPOINT (Session B)
# ════════════════════════════════════════════════════════════

@app.get("/ledger")
def get_ledger():
    """Get the strategic ledger for the ledger screen."""
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    from backend.game_logic.ledger import build_strategic_ledger
    ledger = build_strategic_ledger(world)
    return {"success": True, "ledger": ledger}


# ════════════════════════════════════════════════════════════
# PENDING ENVOY RECOVERY (PL-27 Session 2)
# ════════════════════════════════════════════════════════════

def _build_proposal_popup_clauses(terms, *, include_base=True):
    """Build incoming_proposal_popup.gd-compatible clause strings."""
    from backend.game_logic.mailbox_payloads import build_proposal_popup_clauses

    return build_proposal_popup_clauses(terms, include_base=include_base)


def _build_acceptance_hints(acceptance):
    """Translate acceptance components into Godot-friendly hint strings."""
    from backend.game_logic.mailbox_payloads import build_acceptance_hints

    return build_acceptance_hints(acceptance)


def _build_pending_envoy_popup_from_terms(
    world,
    *,
    nation,
    terms,
    assessment="",
    is_counter_offer=False,
    acceptance=None,
    acceptance_score=None,
    decision_reason="",
):
    """Build the popup payload shape incoming_proposal_popup.gd expects."""
    from backend.game_logic.mailbox_payloads import build_pending_envoy_popup_from_terms

    return build_pending_envoy_popup_from_terms(
        world,
        nation=nation,
        terms=terms,
        assessment=assessment,
        is_counter_offer=is_counter_offer,
        acceptance=acceptance,
        acceptance_score=acceptance_score,
        decision_reason=decision_reason,
    )


def _build_pending_envoy_popup_from_dialogue(world, dialogue):
    """Recover popup payload for an active soft-stop dialogue."""
    from backend.display_names import proposal_display_name

    context = dialogue.get("context", {})
    terms = context.get("counter_terms") or context.get("proposal") or {}
    popup_payload = dialogue.get("popup_payload") or context.get("popup_payload")
    if isinstance(popup_payload, dict) and popup_payload:
        popup = popup_payload.copy()
        popup["is_counter_offer"] = dialogue.get("type", "") in (
            "counter_offer", "counter_offer_response"
        )
        if "proposal_type_display" not in popup:
            proposal_type = popup.get("proposal_type", terms.get("type"))
            if proposal_type is not None:
                popup["proposal_type_display"] = proposal_display_name(proposal_type)
        return popup

    existing_popup = getattr(world, "incoming_proposal_popup", None)
    expected_nation = dialogue.get("target_nation", context.get("source_nation", "Unknown"))
    expected_type = terms.get("type")
    if isinstance(existing_popup, dict) and existing_popup:
        if (
            existing_popup.get("from_nation") == expected_nation
            and (not expected_type or existing_popup.get("proposal_type") == expected_type)
        ):
            popup = existing_popup.copy()
            popup["is_counter_offer"] = dialogue.get("type", "") in (
                "counter_offer", "counter_offer_response"
            )
            if "proposal_type_display" not in popup:
                proposal_type = popup.get("proposal_type", expected_type)
                if proposal_type is not None:
                    popup["proposal_type_display"] = proposal_display_name(proposal_type)
            return popup

    return _build_pending_envoy_popup_from_terms(
        world,
        nation=expected_nation,
        terms=terms,
        assessment=dialogue.get("talleyrand_text", ""),
        is_counter_offer=dialogue.get("type", "") in ("counter_offer", "counter_offer_response"),
        acceptance_score=context.get("acceptance_score"),
        decision_reason=context.get("decision_reason", ""),
    )


@app.get("/pending_envoy")
def get_pending_envoy():
    """Return the current active mailbox item for envoy recovery.

    Session 2 follow-up: Active-item-only. If no active mailbox item
    (queued-only or non-mailbox active), returns has_pending=false with
    accurate count. GET /mailbox is the authoritative browse surface.

    SC-5 reversal commit 2 (Slice G1): incoming settlement offers are
    now first-class mailbox items. Save-loaded saves that carry
    pending settlement offers get promoted into the mailbox queue on
    every read so the badge / pending_envoy / mailbox surfaces stay
    consistent.
    """
    from backend.game_logic.settlement_offers import (
        build_ally_settlement_petition_popup,
        build_incoming_settlement_offer_popup,
        promote_pending_settlement_offers,
    )

    world = game_state["world"]
    promote_pending_settlement_offers(world)
    dm = world.dialogue_manager

    result = {
        "success": True,
        "has_pending": False,
        "pending_envoy_count": int(dm.get_mailbox_count()),
    }

    current = dm.peek()
    if current and current.get("type", "") in dm.SOFT_STOP_MAILBOX_TYPES:
        dtype = current.get("type", "")
        if dtype == "incoming_settlement_offer":
            result["has_pending"] = True
            result["dialogue_type"] = dtype
            popup = current.get("popup_payload")
            if not isinstance(popup, dict) or not popup:
                popup = build_incoming_settlement_offer_popup(world, current)
                current["popup_payload"] = popup
            result["incoming_settlement_offer"] = popup
        elif dtype == "ally_settlement_petition":
            result["has_pending"] = True
            result["dialogue_type"] = dtype
            popup = current.get("popup_payload")
            if not isinstance(popup, dict) or not popup:
                popup = build_ally_settlement_petition_popup(current)
                current["popup_payload"] = popup
            result["diplomatic_dialogue"] = popup
        elif dtype in ("incoming_proposal", "counter_offer", "counter_offer_response"):
            result["has_pending"] = True
            result["dialogue_type"] = dtype
            result["incoming_proposal"] = _build_pending_envoy_popup_from_dialogue(
                world, current
            )

    return result


@app.get("/mailbox")
def get_mailbox():
    """Return ordered list of mailbox items for the inbox panel.

    Session 2 follow-up: Authoritative browse surface for pending diplomacy.

    SC-5 reversal commit 2 (Slice G1): incoming settlement offers are
    first-class mailbox rows. Save-loaded saves get promoted on first
    read so badge counts stay accurate across game sessions.
    """
    from backend.game_logic.settlement_offers import (
        promote_pending_settlement_offers,
    )

    world = game_state["world"]
    promote_pending_settlement_offers(world)
    dm = world.dialogue_manager

    items = list(dm.get_mailbox_items())
    return {
        "success": True,
        "items": items,
        "count": len(items),
    }


class MailboxActivateRequest(BaseModel):
    mailbox_id: int


@app.post("/mailbox/activate")
def activate_mailbox_item(request: MailboxActivateRequest):
    """Swap a queued mailbox item into the active slot.

    Session 2 follow-up: Returns the popup-safe payload for the newly
    active item. The previously active item returns to queue.

    SC-5 reversal commit 2 (Slice G1): incoming settlement offers
    activate into the popup the same way ordinary proposals do.
    Save-loaded saves get promoted into the mailbox queue first so the
    selected `mailbox_id` resolves to a real dialogue.
    """
    from backend.game_logic.settlement_offers import (
        build_ally_settlement_petition_popup,
        build_incoming_settlement_offer_popup,
        promote_pending_settlement_offers,
    )

    world = game_state["world"]
    promote_pending_settlement_offers(world)
    dm = world.dialogue_manager

    dialogue = dm.activate_mailbox_item(request.mailbox_id)

    if dialogue is None:
        return {
            "success": False,
            "message": "Item not found or activation blocked by current dialogue.",
            "items": list(dm.get_mailbox_items()),
            "count": int(dm.get_mailbox_count()),
        }

    dtype = dialogue.get("type", "")
    result = {
        "success": True,
        "dialogue_type": dtype,
        "items": list(dm.get_mailbox_items()),
        "count": int(dm.get_mailbox_count()),
    }

    if dtype in ("incoming_proposal", "counter_offer", "counter_offer_response"):
        popup = _build_pending_envoy_popup_from_dialogue(world, dialogue)
        dialogue["popup_payload"] = popup.copy()
        world.incoming_proposal_popup = popup
        result["incoming_proposal"] = popup
    elif dtype == "incoming_settlement_offer":
        popup = dialogue.get("popup_payload")
        if not isinstance(popup, dict) or not popup:
            popup = build_incoming_settlement_offer_popup(world, dialogue)
            dialogue["popup_payload"] = popup
        result["incoming_settlement_offer"] = popup
    elif dtype == "ally_settlement_petition":
        popup = dialogue.get("popup_payload")
        if not isinstance(popup, dict) or not popup:
            popup = build_ally_settlement_petition_popup(dialogue)
            dialogue["popup_payload"] = popup
        result["diplomatic_dialogue"] = popup

    return result


# ════════════════════════════════════════════════════════════
# DIPLOMATIC LEDGER ENDPOINT (Session 8A)
# ════════════════════════════════════════════════════════════

@app.get("/diplomatic_preview")
def get_diplomatic_preview_endpoint(
    nation: str = "",
    mode: str = "",
    war_id: str = "",
    proposer_side: str = "",
    density: str = "medium",
):
    """Get diplomatic preview for the diplomacy wizard (§3c).

    Without ?nation: returns categorized nation list for Step 1.
    With ?nation=X: returns full preview for Step 2.
    """
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    if mode == "settlement":
        try:
            from backend.game_logic.settlement_staging import build_settlement_preview
            return build_settlement_preview(
                world,
                war_id=war_id,
                proposer_side=proposer_side or None,
                settlement_terms=[],
                actor_nation=getattr(world, "player_nation", "France"),
                density=density,
            )
        except Exception as e:
            return {"success": False, "error": str(e), "mode": "settlement", "war_id": war_id}
    if not nation or not nation.strip():
        # Step 1: Return categorized nation list for the wizard
        try:
            from backend.display_names import STATE_DISPLAY as _STATE_DISPLAY_NAMES
            player = world.player_nation
            enemy_nations = list(getattr(world, 'enemy_nations', []))
            vassals = getattr(world, 'vassals', {})
            dp = int(getattr(world, 'diplomatic_points', 0))
            dm = world.dialogue_manager
            dialogue_pending = dm.is_hard_stop() or dm.has_current_turn_offers() or dm.is_local_planning()
            # PL-30: Distinguish blocking dialogue from deferred proposal result
            has_deferred_result = world.proposal_result_popup is not None

            categories = {"at_war": [], "treaties": [], "vassals": [], "neutral": []}
            treaty_states = {"ARMISTICE", "OPEN_BORDERS", "NON_AGGRESSION",
                             "DEFENSIVE_ALLIANCE", "ALLIANCE"}

            from backend.game_logic.diplomacy import get_relation_descriptor

            # W2: Check for active mission target
            active_mission = getattr(world, 'active_diplomatic_mission', None)
            mission_target = None
            if active_mission and isinstance(active_mission, dict) and not active_mission.get("completed"):
                mission_target = active_mission.get("target")

            for n in enemy_nations:
                # Skip eliminated nations (no marshals with strength, no regions)
                has_forces = any(
                    m.strength > 0 for m in world.marshals.values() if m.nation == n
                )
                has_regions = any(
                    r.controller == n for r in world.regions.values()
                )
                if not has_forces and not has_regions:
                    continue

                diplo_key = world._make_diplo_key(player, n)
                state = world.diplomatic_states.get(diplo_key, "PEACE")
                is_vassal = n in vassals

                # W1: Relation score and descriptor
                relation = int(world.nation_relations.get(diplo_key, 0) or 0)
                relation_desc = get_relation_descriptor(relation)

                entry = {
                    "name": n,
                    "state": state,
                    "state_display": _STATE_DISPLAY_NAMES.get(state, state),
                    "is_vassal": is_vassal,
                    "relation": relation,
                    "relation_descriptor": relation_desc,
                    "has_active_mission": (mission_target == n),
                }

                if is_vassal:
                    entry["state_display"] = "Vassal"
                    categories["vassals"].append(entry)
                elif state == "WAR":
                    categories["at_war"].append(entry)
                elif state in treaty_states:
                    categories["treaties"].append(entry)
                else:
                    categories["neutral"].append(entry)

            return {
                "success": True,
                "mode": "nations",
                "dp_available": int(dp),
                "dialogue_pending": dialogue_pending,
                "pending_envoy_count": int(dm.get_mailbox_count()),
                "has_deferred_result": has_deferred_result,
                "categories": categories,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    try:
        from backend.game_logic.diplomacy import get_diplomatic_preview
        nation = nation.strip()
        # Reject self-proposal
        if nation == world.player_nation:
            return {"success": False, "error": "We cannot conduct diplomacy with ourselves, Your Excellency."}
        # Reject eliminated nations
        if nation in list(getattr(world, 'enemy_nations', [])):
            has_forces = any(m.strength > 0 for m in world.marshals.values() if m.nation == nation)
            has_regions = any(r.controller == nation for r in world.regions.values())
            if not has_forces and not has_regions:
                return {"success": False, "error": f"{nation} has been eliminated from the war."}
        preview = get_diplomatic_preview(world, nation)
        return {
            "success": True,
            "dialogue_pending": (
                world.dialogue_manager.is_hard_stop()
                or world.dialogue_manager.has_current_turn_offers()
                or world.dialogue_manager.is_local_planning()
            ),
            "pending_envoy_count": int(world.dialogue_manager.get_mailbox_count()),
            **preview,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/diplomatic_preview")
def post_diplomatic_preview_endpoint(request: dict):
    """Preview draft diplomatic payloads.

    Slice C2 currently supports `{"mode": "settlement"}` only. This endpoint
    is preview-only and must not stage settlement_confirm or mutate world state.
    """
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    if request.get("mode") != "settlement":
        return {"success": False, "error": "unsupported_preview_mode"}
    try:
        from backend.game_logic.settlement_staging import (
            build_settlement_preview,
        )
        from backend.game_logic.settlement_validation import (
            validate_settlement_terms,
        )
        actor = request.get("actor_nation") or getattr(world, "player_nation", "France")
        terms = request.get("settlement_terms", [])
        war_id_str = str(request.get("war_id") or "")
        # SC-1: validate authored terms before building preview.
        war_instance = (getattr(world, "war_instances", {}) or {}).get(war_id_str) or {}
        actor_side = None
        for side in ("attackers", "defenders"):
            if actor in (war_instance.get(side) or []):
                actor_side = side
                break
        validation = validate_settlement_terms(
            terms,
            actor_nation=actor,
            player_nation=getattr(world, "player_nation", "France"),
            proposer_side=request.get("proposer_side"),
            actor_side_in_war=actor_side,
            covered_enemy_participants=request.get("covered_enemy_participants"),
            world=world,
            war_instance=war_instance,
        )
        if not validation.get("valid"):
            return {
                "success": False,
                "mode": "settlement",
                "war_id": war_id_str,
                "error": validation.get("error"),
                "error_index": validation.get("error_index"),
                "disabled_reason_display": validation.get("disabled_reason_display"),
                "mutated": False,
            }
        return build_settlement_preview(
            world,
            war_id=war_id_str,
            proposer_side=request.get("proposer_side"),
            settlement_terms=terms,
            covered_enemy_participants=request.get("covered_enemy_participants"),
            actor_nation=actor,
            density=str(request.get("density") or "medium"),
        )
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "mode": "settlement",
            "war_id": request.get("war_id"),
        }


@app.get("/diplomatic_ledger")
def get_diplomatic_ledger():
    """Get the diplomatic ledger for the diplomatic ledger screen."""
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    try:
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        ledger = build_diplomatic_ledger(world)
        return {"success": True, "ledger": ledger}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/cancel_order")
async def cancel_order(request: Request):
    """Cancel a marshal's strategic order from the Orders tab."""
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        data = await request.json()
        marshal_name = data.get("marshal")
        if not marshal_name:
            return build_base_response(
                world, success=False, message="No marshal specified.")

        if not game_state.get("world"):
            return build_base_response(
                world, success=False, message="No active game")

        # AP pre-check (matches typed cancel command flow)
        if world.actions_remaining <= 0:
            return build_base_response(
                world, success=False,
                message="No actions remaining this turn.")

        # 2A-4: Dialogue guard — block cancel during active diplomatic dialogue
        if world.pending_diplomatic_dialogue is not None:
            return build_base_response(
                world, success=False,
                message="Talleyrand awaits your response to a diplomatic matter.")

        command = {"action": "cancel", "marshal": marshal_name}
        result = executor._execute_cancel(command, game_state)

        # Deduct 1 AP for successful cancels (matches typed "cancel" command flow)
        if result.get("success") and not result.get("no_action_cost"):
            world.use_action("cancel")

        return _build_result_response(result, world)
    except Exception as e:
        print(f"[ERROR] handling cancel_order: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.get("/marshal_overview")
def get_marshal_overview():
    """Get the marshal overview for the Marshal Management screen."""
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    from backend.game_logic.marshal_overview import build_marshal_overview
    overview = build_marshal_overview(world)
    return {"success": True, "marshals": overview}


# ════════════════════════════════════════════════════════════
# NOTIFICATION ENDPOINTS (Phase 6.5)
# ════════════════════════════════════════════════════════════

@app.post("/notifications/dismiss")
async def dismiss_notification(request: Request):
    """Dismiss a notification by ID, or dismiss all if id='all'."""
    data = await request.json()
    notification_id = data.get("id")
    if not notification_id:
        return {"success": False, "message": "Missing notification id"}
    if notification_id == "all":
        count = world.notifications.dismiss_all()
        return build_base_response(world, dismissed=int(count))
    dismissed = world.notifications.dismiss(notification_id)
    return build_base_response(
        world, success=dismissed, dismissed=1 if dismissed else 0)


@app.get("/notifications")
def get_notifications():
    """Get all pending notifications."""
    if not game_state.get("world"):
        return {"success": False, "notifications": []}
    return {"notifications": world.notifications.get_pending()}


# ════════════════════════════════════════════════════════════
# DEBUG ENDPOINTS (Only available when DEBUG_MODE = True)
# ════════════════════════════════════════════════════════════

@app.post("/debug/set_trust")
async def debug_set_trust(request: Request):
    """
    DEBUG: Set marshal trust to specific value.

    Usage:
        POST /debug/set_trust
        Body: {"marshal": "Ney", "trust": 25}
    """
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    data = await request.json()
    marshal_name = data.get("marshal")
    trust_value = data.get("trust")

    if marshal_name is None or trust_value is None:
        return {"success": False, "message": "Required: marshal, trust"}

    marshal = world.get_marshal(marshal_name)
    if not marshal:
        return {"success": False, "message": f"Unknown marshal: {marshal_name}"}

    old_trust = int(marshal.trust.value)
    marshal.trust.set(int(trust_value))

    print(f"[DEBUG] Set {marshal_name} trust: {old_trust} -> {marshal.trust.value}")

    return build_base_response(world,
        marshal=marshal_name,
        old_trust=old_trust,
        new_trust=int(marshal.trust.value),
        trust_label=marshal.trust.get_label())


@app.get("/debug/marshal_status/{marshal_name}")
def debug_marshal_status(marshal_name: str):
    """
    DEBUG: Get full marshal status including autonomy state.

    Usage:
        GET /debug/marshal_status/Ney
    """
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    marshal = world.get_marshal(marshal_name)
    if not marshal:
        available = [m.name for m in world.get_player_marshals()]
        return {
            "success": False,
            "message": f"Unknown marshal: {marshal_name}",
            "available_marshals": available
        }

    return {
        "success": True,
        "name": marshal.name,
        "nation": marshal.nation,
        "location": marshal.location,
        "strength": int(marshal.strength),
        "morale": int(marshal.morale),
        "trust": int(marshal.trust.value) if hasattr(marshal, 'trust') else 70,
        "trust_label": marshal.trust.get_label() if hasattr(marshal, 'trust') else "Unknown",
        "vindication": int(getattr(marshal, 'vindication_score', 0)),
        "autonomous": getattr(marshal, 'autonomous', False),
        "autonomy_turns": getattr(marshal, 'autonomy_turns', 0),
        "personality": marshal.personality,
        "recent_overrides": list(getattr(marshal, 'recent_overrides', [])),
    }


@app.get("/debug/status")
def debug_status():
    """
    DEBUG: Get overall debug status and available commands.

    Usage:
        GET /debug/status
    """
    return {
        "debug_mode": DEBUG_MODE,
        "message": "Debug mode is " + ("ENABLED" if DEBUG_MODE else "DISABLED"),
        "available_endpoints": [
            "POST /debug/set_trust - Set marshal trust value",
            "GET /debug/marshal_status/{name} - Get full marshal status",
            "GET /debug/status - This endpoint",
            "GET /debug/trigger_redemption/{name} - Force redemption event",
            "POST /debug/set_authority - Set player authority level",
        ] if DEBUG_MODE else []
    }


@app.get("/debug/trigger_redemption/{marshal_name}")
def debug_trigger_redemption(marshal_name: str):
    """
    DEBUG: Force a redemption event by setting trust to critical.

    Usage:
        GET /debug/trigger_redemption/Ney
    """
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    marshal = world.get_marshal(marshal_name)
    if not marshal:
        return {"success": False, "message": f"Unknown marshal: {marshal_name}"}

    old_trust = int(marshal.trust.value)
    marshal.trust.set(15)  # Set to critical level

    # Create redemption event
    redemption_event = world.disobedience_system._create_redemption_event(marshal)
    world.pending_redemption = redemption_event

    print(f"[DEBUG] Triggered redemption for {marshal_name} (trust: {old_trust} -> 15)")

    return {
        "success": True,
        "marshal": marshal_name,
        "old_trust": old_trust,
        "new_trust": 15,
        "redemption_event": redemption_event,
        "message": f"Redemption event triggered for {marshal_name}. Use /respond_to_redemption to resolve."
    }


@app.post("/debug/set_authority")
async def debug_set_authority(request: Request):
    """
    DEBUG: Set player authority level.

    Usage:
        POST /debug/set_authority
        Body: {"authority": 50}
    """
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    data = await request.json()
    authority_value = data.get("authority")

    if authority_value is None:
        return {"success": False, "message": "Required: authority"}

    old_authority = int(world.authority_tracker.authority)
    world.authority_tracker.authority = max(0, min(100, int(authority_value)))

    print(f"[DEBUG] Set authority: {old_authority} -> {world.authority_tracker.authority}")

    return build_base_response(world,
        old_authority=old_authority,
        new_authority=int(world.authority_tracker.authority),
        authority_label=world.authority_tracker.get_authority_label())


# ════════════════════════════════════════════════════════════
# DIPLOMATIC DEBUG ENDPOINTS (Session 8A)
# ════════════════════════════════════════════════════════════

@app.get("/debug/diplomatic_status")
def debug_diplomatic_status():
    """DEBUG: Full diplomatic snapshot — states, relations, treaties, vassals, DP, Talleyrand."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    # Serialize tuple-keyed dicts as "A_B" strings
    diplomatic_states = {k: v for k, v in world.diplomatic_states.items()}
    nation_relations = {k: int(v) for k, v in world.nation_relations.items()}
    active_treaties = {}
    for k, v in getattr(world, 'active_treaties', {}).items():
        active_treaties[k] = v.copy() if isinstance(v, dict) else v

    vassals = {}
    for k, v in getattr(world, 'vassals', {}).items():
        vassals[k] = v.copy() if isinstance(v, dict) else v

    diplomats_data = {}
    for k, v in getattr(world, 'diplomats', {}).items():
        diplomats_data[k] = v.to_dict() if hasattr(v, 'to_dict') else str(v)

    # R7: Add display-friendly state names
    from backend.display_names import STATE_DISPLAY
    diplomatic_states_display = {k: STATE_DISPLAY.get(v, v) for k, v in diplomatic_states.items()}

    return {
        "success": True,
        "diplomatic_states": diplomatic_states,
        "diplomatic_states_display": diplomatic_states_display,
        "nation_relations": nation_relations,
        "active_treaties": active_treaties,
        "vassals": vassals,
        "diplomatic_points": int(getattr(world, 'diplomatic_points', 0)),
        "max_diplomatic_points": int(getattr(world, 'max_diplomatic_points', 3)),
        "talleyrand": diplomats_data.get(get_player_nation(world), {}),
    }


@app.get("/debug/war_scores")
def debug_war_scores():
    """DEBUG: Per nation-pair war score with component breakdown."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    from backend.game_logic.diplomacy import calculate_war_score
    scores = []
    for diplo_key, state in world.diplomatic_states.items():
        if state == "WAR":
            parts = diplo_key.split("|")
            if len(parts) == 2:
                components = calculate_war_score(parts[0], parts[1], world, return_components=True)
                scores.append({
                    "nation_a": parts[0],
                    "nation_b": parts[1],
                    "components": components,
                    "total": components["total"],
                })

    return {"success": True, "war_scores": scores}


@app.post("/debug/acceptance_preview")
async def debug_acceptance_preview(request: Request):
    """DEBUG: Run acceptance formula on a proposal body."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    data = await request.json()
    proposal = data.get("proposal", {})
    if not proposal:
        return {"success": False, "message": "No proposal provided."}

    from backend.game_logic.diplomacy import calculate_acceptance
    result = calculate_acceptance(proposal, world)
    return {"success": True, "acceptance": result}


@app.get("/debug/coalition_status")
def debug_coalition_status():
    """DEBUG: Coalition threat, brewing, active coalition snapshot."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    from backend.game_logic.coalition import get_qualifying_nations
    qualifying = get_qualifying_nations(world)

    threat = int(getattr(world, 'threat_level', 0))
    if threat >= 80:
        tier = "CRITICAL"
    elif threat >= 60:
        tier = "HIGH"
    elif threat >= 30:
        tier = "MODERATE"
    else:
        tier = "LOW"

    brewing = getattr(world, 'coalition_brewing', None)
    coalition = getattr(world, 'active_coalition', None)

    return {
        "success": True,
        "threat_level": threat,
        "threat_tier": tier,
        "brewing": brewing is not None,
        "brewing_turns": int(brewing.get("turns_remaining", 0)) if brewing else None,
        "qualifying_nations": qualifying,
        "active_coalition": coalition.copy() if coalition else None,
    }


@app.get("/debug/threat_sources")
def debug_threat_sources():
    """DEBUG: Threat sources this turn."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    return {
        "success": True,
        "threat_sources_this_turn": list(getattr(world, 'threat_sources_this_turn', [])),
    }


@app.get("/debug/proposal_cooldowns")
def debug_proposal_cooldowns():
    """DEBUG: AI and player proposal cooldowns."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    return {
        "success": True,
        "ai_proposal_cooldowns": dict(getattr(world, 'ai_proposal_cooldowns', {})),
        "player_proposal_cooldowns": dict(getattr(world, 'player_proposal_cooldowns', {})),
    }


@app.get("/debug/vassal_loyalty/{nation}")
def debug_vassal_loyalty(nation: str):
    """DEBUG: Vassal loyalty value + per-modifier breakdown."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    if nation not in getattr(world, 'vassals', {}):
        return {"success": False, "message": f"{nation} is not a vassal."}

    state = world.vassals[nation]
    lord = state["lord"]
    loyalty = int(state["loyalty"])

    # Compute modifiers manually to match vassal.py process_vassal_loyalty
    from backend.game_logic.vassal import AUTONOMY_DRIFT

    autonomy = state.get("autonomy", 1)
    drift = AUTONOMY_DRIFT.get(autonomy, 0)

    garrison_bonus = 0
    vassal_capital = world.get_nation_capital(nation)
    if vassal_capital:
        region = world.regions.get(vassal_capital)
        if region:
            garrison_troops = getattr(region, 'garrison_troops', 0) or 0
            if garrison_troops > 0 and getattr(region, 'controller', '') == lord:
                garrison_bonus = 5 + min(garrison_troops // 5000, 3)

    shared_enemy_bonus = 0
    all_nations = set(getattr(world, "enemy_nations", []))
    all_nations.update(world.get_active_nations())
    all_nations.update({lord, nation})
    for other_nation in sorted(all_nations):
        if other_nation == lord or other_nation == nation:
            continue
        lord_state = world.get_diplomatic_state(lord, other_nation)
        vassal_state_diplo = world.get_diplomatic_state(nation, other_nation)
        if lord_state == "WAR" and vassal_state_diplo == "WAR":
            shared_enemy_bonus += 2

    diplo_key = world._make_diplo_key(nation, lord)
    relation = world.nation_relations.get(diplo_key, 0)
    relation_modifier = relation // 20

    return {
        "success": True,
        "nation": nation,
        "loyalty": loyalty,
        "lord": lord,
        "modifiers": {
            "autonomy_drift": drift,
            "garrison_bonus": garrison_bonus,
            "shared_enemy_bonus": shared_enemy_bonus,
            "relation_modifier": relation_modifier,
        },
    }


@app.get("/debug/proposal_queue")
def debug_proposal_queue():
    """DEBUG: Mailbox items (replaces old diplomatic_queue debug)."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    world = game_state["world"]
    dm = world.dialogue_manager
    return {
        "success": True,
        "mailbox_items": dm.get_mailbox_items(),
        "mailbox_count": int(dm.get_mailbox_count()),
        "dialogue_manager": dm.to_dict(),
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("[*] GAME INITIALIZED")
    print(f"[*] DEBUG MODE: {'ENABLED' if DEBUG_MODE else 'DISABLED'}")
    print("=" * 60)
    print(f"Turn: {world.current_turn}")
    print(f"Actions: {world.actions_remaining}/{world.max_actions_per_turn}")
    print(f"Gold: {world.gold}")
    print(f"Regions: {len(world.get_player_regions())}")
    print("=" * 60)
    print("[*] Server: http://127.0.0.1:8005")
    print("[*] API Docs: http://127.0.0.1:8005/docs")
    print("=" * 60)

    uvicorn.run(app, host="127.0.0.1", port=8005)
