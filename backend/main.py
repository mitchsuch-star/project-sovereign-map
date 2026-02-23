"""
FastAPI server for Project Sovereign
Connects Godot frontend to Python game logic
"""

import os
from dotenv import load_dotenv

# Load .env BEFORE any imports that might read env vars
load_dotenv()

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.commands.parser import CommandParser
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState
from backend.models.intel import FULL, PARTIAL
from backend.save_manager import save_game, load_game, list_saves, delete_save

# ════════════════════════════════════════════════════════════
# DEBUG MODE: Set to True to enable debug endpoints
# ════════════════════════════════════════════════════════════
DEBUG_MODE = True  # Set to False for production

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
world = WorldState(player_nation="France")
game_state = {"world": world, "debug_mode": DEBUG_MODE}


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

    # Build enemies dict
    enemies = {}
    for m in world.get_enemy_marshals():
        if m.strength > 0:  # Only alive marshals
            enemies[m.name] = {
                "location": m.location,
                "strength": int(m.strength),
                "nation": m.nation,
            }

    # Build map_data dict
    map_data = {}
    for region_name, region in world.regions.items():
        marshals_here = world.get_marshals_in_region(region_name)
        map_data[region_name] = {
            "controller": region.controller or "Neutral",
            "marshals": [
                {"name": m.name, "personality": getattr(m, 'personality', 'unknown')}
                for m in marshals_here if m.strength > 0
            ]
        }

    return {
        "turn": int(world.current_turn),
        "gold": int(world.gold),
        "marshals": marshals,
        "enemies": enemies,
        "map_data": map_data,
    }

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
        "summary": enemy_phase.get("summary", [])
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

    # Preserve enemy_victory if present
    if enemy_phase.get("enemy_victory"):
        filtered_phase["enemy_victory"] = enemy_phase["enemy_victory"]

    return filtered_phase


def _filter_tactical_events_by_visibility(events: list, world_state) -> list:
    """
    Fog of War (Session 34B): Filter tactical events by player visibility.

    Rules:
    - Player nation events -> always show
    - Auto-charge results -> always show (involve player marshal)
    - Enemy events in visible regions (PARTIAL+) -> show
    - Enemy events in fogged regions -> suppress
    """
    if not events:
        return events

    player_nation = world_state.player_nation
    filtered = []

    for event in events:
        if not isinstance(event, dict):
            filtered.append(event)
            continue

        # Player nation events always shown
        event_nation = event.get("nation", "")
        event_marshal = event.get("marshal", "")

        # Check if this is a player-side event
        is_player_event = False
        if event_nation == player_nation:
            is_player_event = True
        elif event_marshal:
            pm = world_state.get_marshal(event_marshal)
            if pm and pm.nation == player_nation:
                is_player_event = True

        # Auto-charge and reckless events always involve player
        event_type = event.get("type", "")
        if event_type in ("auto_charge", "reckless_cavalry"):
            is_player_event = True

        # Fog events (intel_updated, intel_decayed, target_not_found) always shown
        if event_type in ("intel_updated", "intel_decayed", "target_not_found"):
            is_player_event = True

        if is_player_event:
            filtered.append(event)
            continue

        # Enemy event — check region visibility
        event_location = event.get("location", "") or event.get("region", "")
        if event_location:
            intel = world_state.get_region_intel(event_location)
            if intel.visibility in (FULL, PARTIAL):
                filtered.append(event)
                continue
        # No location or below PARTIAL -> suppress

    return filtered


# Allow Godot to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CommandRequest(BaseModel):
    command: str


class ObjectionResponse(BaseModel):
    """Request model for responding to marshal objections."""
    choice: str  # 'trust', 'insist', or 'compromise'


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
    return {
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
        "game_state": world.get_filtered_game_state_summary()
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
        # PENDING STRATEGIC INTERRUPT CHECK (Phase 5.2-D)
        # If a marshal has a pending interrupt (cannon fire, blocked path),
        # try to map the player's text input to a response choice.
        # This prevents the command from being parsed as a new order.
        # ════════════════════════════════════════════════════════════
        for m in world.get_player_marshals():
            pending = getattr(m, 'pending_interrupt', None)
            if pending:
                cmd_lower = request.command.strip().lower()

                # ── Guard: if command addresses a DIFFERENT marshal, skip ──
                # "grouchy march to brittany" should NOT be routed as
                # Davout's interrupt response just because "march to" matches.
                known_marshal_names = [
                    name.lower() for name in world.marshals.keys()
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
                    from backend.commands.strategic import StrategicExecutor
                    strategic_exec = StrategicExecutor(executor)
                    result = strategic_exec.handle_response(
                        m.name, interrupt_type, choice, world, game_state)
                    cleaned = {k: v for k, v in result.items() if k != "new_state"}
                    cleaned["action_summary"] = world.get_action_summary()
                    cleaned["game_state"] = world.get_filtered_game_state_summary()
                    if world.notifications.has_pending():
                        cleaned["notifications"] = world.notifications.get_pending()
                    return cleaned

        # Parse command
        # Build LLM-compatible game state for command parsing
        llm_game_state = get_llm_game_state()
        parsed = parser.parse(request.command, llm_game_state, world=world)
        print(f"[OK] Parsed: {parsed.get('command', {}).get('action', 'unknown')}")

        # ════════════════════════════════════════════════════════════
        # COMMAND HISTORY (Phase 5): Track commands for LLM repetition detection
        # Only in LLM mode (not mock) and only for successfully parsed commands
        # ════════════════════════════════════════════════════════════
        if parsed.get("mode") != "mock" and parsed.get("success"):
            world.add_to_command_history({
                "raw_input": request.command,
                "marshal": parsed.get("command", {}).get("marshal"),
                "action": parsed.get("command", {}).get("action"),
                "turn": int(world.current_turn),
            })

        # ════════════════════════════════════════════════════════════
        # BERTHIER PARSE RECOVERY: Replace generic "Unknown action"
        # with in-character Berthier clarification. Only fires for
        # type-1 parse failures; marshal typos & validation errors
        # pass through unchanged.
        # ════════════════════════════════════════════════════════════
        if not parsed.get("success") and (parsed.get("error") or "").startswith("Unknown action"):
            berthier_msg = parser.llm.generate_berthier_recovery(
                raw_command=request.command,
                game_state=llm_game_state,
                partial_parse={
                    "recognized_marshal": parsed.get("partial_marshal"),
                    "recognized_target": parsed.get("partial_target"),
                    "raw_input": parsed.get("raw_input", request.command),
                },
            )
            return {
                "success": False,
                "message": berthier_msg,
                "events": [],
                "action_info": {
                    "cost": 0,
                    "remaining": int(world.actions_remaining),
                    "turn_advanced": False,
                    "new_turn": None,
                },
                "action_summary": world.get_action_summary(),
                "game_state": world.get_filtered_game_state_summary(),
            }

        # Execute command
        result = executor.execute(parsed, game_state)

        # ════════════════════════════════════════════════════════════
        # BERTHIER EXECUTOR RECOVERY: Catch "Marshal 'None' not found"
        # This happens when a valid action is parsed but no marshal was
        # identified (e.g., "move to Belgium" without naming a marshal).
        # ════════════════════════════════════════════════════════════
        if not result.get("success") and "Marshal 'None' not found" in (result.get("message") or ""):
            berthier_msg = parser.llm.generate_berthier_recovery(
                raw_command=request.command,
                game_state=llm_game_state,
                partial_parse={
                    "recognized_marshal": None,
                    "recognized_target": parsed.get("command", {}).get("target"),
                    "raw_input": request.command,
                },
            )
            return {
                "success": False,
                "message": berthier_msg,
                "events": [],
                "action_info": {
                    "cost": 0,
                    "remaining": int(world.actions_remaining),
                    "turn_advanced": False,
                    "new_turn": None,
                },
                "action_summary": world.get_action_summary(),
                "game_state": world.get_filtered_game_state_summary(),
            }

        # ════════════════════════════════════════════════════════════
        # CHECK FOR OBJECTION: If awaiting player choice, return full result
        # Tactical objections: state == "awaiting_player_choice"
        # Strategic objections (Phase M): pending_objection == True
        # ════════════════════════════════════════════════════════════
        if result.get("state") == "awaiting_player_choice":
            print("[OBJECTION] TACTICAL OBJECTION - Returning full result to frontend")
            cleaned = {k: v for k, v in result.items() if k != "new_state"}
            cleaned["action_summary"] = world.get_action_summary()
            cleaned["game_state"] = world.get_filtered_game_state_summary()
            if world.notifications.has_pending():
                cleaned["notifications"] = world.notifications.get_pending()
            return cleaned

        if result.get("pending_objection"):
            print("[OBJECTION] STRATEGIC OBJECTION (Phase M) - Returning full result to frontend")
            cleaned = {k: v for k, v in result.items() if k != "new_state"}
            cleaned["action_summary"] = world.get_action_summary()
            cleaned["game_state"] = world.get_filtered_game_state_summary()
            if world.notifications.has_pending():
                cleaned["notifications"] = world.notifications.get_pending()
            return cleaned

        # ════════════════════════════════════════════════════════════
        # CHECK FOR CLARIFICATION: If awaiting clarification, return full result
        # ════════════════════════════════════════════════════════════
        if result.get("state") == "awaiting_clarification":
            print("[CLARIFICATION] Returning clarification popup to frontend")
            cleaned = {k: v for k, v in result.items() if k != "new_state"}
            cleaned["action_summary"] = world.get_action_summary()
            cleaned["game_state"] = world.get_filtered_game_state_summary()
            if world.notifications.has_pending():
                cleaned["notifications"] = world.notifications.get_pending()
            return cleaned

        # ════════════════════════════════════════════════════════════
        # CHECK FOR GLORIOUS CHARGE: If pending, return full result for popup
        # ════════════════════════════════════════════════════════════
        if result.get("pending_glorious_charge"):
            print("GLORIOUS CHARGE PENDING - Returning full result to frontend")
            cleaned = {k: v for k, v in result.items() if k != "new_state"}
            cleaned["action_summary"] = world.get_action_summary()
            cleaned["game_state"] = world.get_filtered_game_state_summary()
            if world.notifications.has_pending():
                cleaned["notifications"] = world.notifications.get_pending()
            return cleaned

        # ════════════════════════════════════════════════════════════
        # CHECK FOR STRATEGIC INTERRUPT: Blocked path, cannon fire popup
        # (Session 39: was missing — pending_interrupt dropped at response build)
        # ════════════════════════════════════════════════════════════
        if result.get("pending_interrupt"):
            print("[INTERRUPT] STRATEGIC INTERRUPT - Returning full result to frontend")
            cleaned = {k: v for k, v in result.items() if k != "new_state"}
            cleaned["action_summary"] = world.get_action_summary()
            cleaned["game_state"] = world.get_filtered_game_state_summary()
            if world.notifications.has_pending():
                cleaned["notifications"] = world.notifications.get_pending()
            return cleaned

        # ════════════════════════════════════════════════════════════
        # CHECK FOR CAPTURE CHOICE (Phase 6.2.E): Plunder or Secure popup
        # ════════════════════════════════════════════════════════════
        if result.get("pending_capture_choice"):
            print("[CAPTURE] PLUNDER/SECURE CHOICE PENDING - Returning full result to frontend")
            cleaned = {k: v for k, v in result.items() if k != "new_state"}
            cleaned["action_summary"] = world.get_action_summary()
            cleaned["game_state"] = world.get_filtered_game_state_summary()
            if world.notifications.has_pending():
                cleaned["notifications"] = world.notifications.get_pending()
            return cleaned

        # Get action summary
        action_summary = world.get_action_summary()

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

        response = {
            "success": result.get("success", False),
            "message": result.get("message", "Command executed"),
            "events": result.get("events", []),
            "action_info": result.get("action_info", {}),
            "action_summary": action_summary,
            "game_state": world.get_filtered_game_state_summary()
        }

        # Add feedback if generated
        if feedback:
            response["feedback"] = feedback

        # Save/Load: pass through show_load_dialog flag for Godot
        if result.get("show_load_dialog"):
            response["show_load_dialog"] = True

        # Phase 6.1: Include cavalry terrain message if present
        # (same passthrough pattern as mild_concerns — field exists in combat
        # result but wasn't being forwarded to Godot as a separate field)
        if result.get("cavalry_terrain_message"):
            response["cavalry_terrain_message"] = result["cavalry_terrain_message"]

        # Berthier's Bombardment Advisory (Artillery Session 2)
        if result.get("bombardment_advisory"):
            response["bombardment_advisory"] = result["bombardment_advisory"]

        # Bombardment result (Phase 6.5: separate bombardment resolution path)
        if result.get("bombardment_result"):
            response["bombardment_result"] = result["bombardment_result"]
            response["action"] = "bombardment"

        # Redemption event (bombardment friendly fire can trigger this — §4.4)
        if result.get("redemption_event"):
            response["state"] = "awaiting_redemption_choice"
            response["redemption_event"] = result["redemption_event"]
            world.pending_redemption = result["redemption_event"]
            print(f"[ALERT] REDEMPTION TRIGGERED for {result['redemption_event']['marshal']}")

        # Berthier's After-Action Report
        if result.get("battle_report"):
            response["battle_report"] = result["battle_report"]

        # V2a: Include mild concerns for turn log display
        # BUG FIX: Only send mild_concerns from the result dict (end_turn path).
        # Previously, the elif fallback sent world.mild_concerns_this_turn on EVERY
        # command response, which caused stale MILD concerns from failed actions to
        # appear on the next successful command. MILD dispatches should only appear
        # after end_turn, where executor.py saves them before advance_turn clears the list.
        if result.get("mild_concerns"):
            response["mild_concerns"] = result["mild_concerns"]

        # Include enemy_phase if present (from end_turn)
        # Clean up non-serializable fields (new_state contains circular references)
        if result.get("enemy_phase"):
            enemy_phase = result["enemy_phase"]
            cleaned_phase = {
                "nations": {},
                "total_actions": enemy_phase.get("total_actions", 0),
                "summary": enemy_phase.get("summary", [])
            }
            # Clean each nation's actions
            for nation, nation_data in enemy_phase.get("nations", {}).items():
                cleaned_actions = []
                for action in nation_data.get("actions", []):
                    # Remove new_state which has circular references
                    cleaned_action = {k: v for k, v in action.items() if k != "new_state"}
                    # DEBUG: Check if events are present
                    if "events" in cleaned_action:
                        print(f"[ENEMY_PHASE_DEBUG] {nation} action has events: {len(cleaned_action.get('events', []))} events")
                        for evt in cleaned_action.get("events", []):
                            print(f"  - Event type: {evt.get('type')}, keys: {list(evt.keys())}")
                    else:
                        print(f"[ENEMY_PHASE_DEBUG] {nation} action has NO events! Keys: {list(cleaned_action.keys())}")
                    cleaned_actions.append(cleaned_action)
                cleaned_phase["nations"][nation] = {
                    "actions": cleaned_actions,
                    "action_count": nation_data.get("action_count", 0)
                }
            if enemy_phase.get("enemy_victory"):
                cleaned_phase["enemy_victory"] = enemy_phase["enemy_victory"]

            # FOG OF WAR (Session 34B): Filter enemy actions by visibility
            cleaned_phase = _filter_enemy_phase_by_visibility(cleaned_phase, world)

            response["enemy_phase"] = cleaned_phase

            # DEBUG: Print final enemy_phase structure
            print("[ENEMY_PHASE_FINAL] Sending to Godot:")
            for nation, data in cleaned_phase.get("nations", {}).items():
                print(f"  {nation}: {len(data.get('actions', []))} actions")
                for i, act in enumerate(data.get("actions", [])):
                    has_events = "events" in act and len(act.get("events", [])) > 0
                    print(f"    [{i}] {act.get('ai_action', {}).get('action', '?')} - has_events: {has_events}")

        # Include strategic reports if present (Phase 5.2-C)
        if result.get("strategic_reports"):
            response["strategic_reports"] = result["strategic_reports"]
            print(f"[STRATEGIC_REPORTS] Sending {len(result['strategic_reports'])} reports to Godot:")
            for i, sr in enumerate(result["strategic_reports"]):
                print(f"  [{i}] {sr.get('marshal')}: {sr.get('command')} -> {sr.get('action', 'N/A')}, status={sr.get('order_status')}, has_battle={bool(sr.get('battle_details'))}")
        else:
            print(f"[STRATEGIC_REPORTS] No strategic reports in result (keys: {[k for k in result.keys() if 'strat' in k.lower()]})")

        # Include tactical events if present (from end_turn).
        # Contains supply attrition messages, occupation updates, etc.
        # Godot main.gd reads tactical_events for display in turn log.
        if result.get("tactical_events"):
            # FOG OF WAR (Session 34B): Filter tactical events by visibility
            response["tactical_events"] = _filter_tactical_events_by_visibility(
                result["tactical_events"], world)

        # Include independent command report if present (Phase 2.5)
        if result.get("show_independent_command_report"):
            response["show_independent_command_report"] = True
            response["independent_command_report"] = result.get("independent_command_report", [])

        # Morning Dispatch — Berthier's turn-start briefing (Phase 6.5)
        if result.get("morning_dispatch"):
            response["morning_dispatch"] = result["morning_dispatch"]

        # Notifications — persistent alerts for Godot notification bar
        if world.notifications.has_pending():
            response["notifications"] = world.notifications.get_pending()

        return response
    except Exception as e:
        print(f"[ERROR]: {e}")
        import traceback
        traceback.print_exc()

        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "events": [],
            "action_info": {"remaining": int(world.actions_remaining)},
            "action_summary": world.get_action_summary(),
            "game_state": world.get_filtered_game_state_summary()
        }


@app.get("/status")
def get_status():
    """Get current game status — Berthier's Intelligence Report (Session 34A)."""
    from backend.intel_report import generate_intel_report
    report = generate_intel_report(world)
    report["game_state"] = world.get_filtered_game_state_summary()
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
    return {
        "has_pending": True,
        "marshal": objection.get("marshal"),
        "message": objection.get("message"),
        "severity": int(objection.get("severity", 0.5) * 100),  # int % for Godot — no raw floats
        "type": objection.get("type", "major"),
        "trigger": objection.get("trigger"),
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
        # Handle the objection response through executor
        result = executor.handle_objection_response(request.choice, game_state)

        response = {
            "success": result.get("success", False),
            "message": result.get("message", "Response processed"),
            "objection_resolved": result.get("objection_resolved", True),
            "choice": result.get("choice"),
            "trust_change": result.get("trust_change", 0),
            "authority_change": result.get("authority_change", 0),
            "disobeyed": result.get("disobeyed", False),
            "events": result.get("events", []),
            "action_info": result.get("action_info", {}),
            "action_summary": world.get_action_summary(),
            "game_state": world.get_filtered_game_state_summary(),
            "strategic_reports": result.get("strategic_reports", []),
        }
        if result.get("battle_report"):
            response["battle_report"] = result["battle_report"]

        # ════════════════════════════════════════════════════════════
        # STRATEGIC INTERRUPT: Post-objection command may hit blocked path
        # (Session 39: pending_interrupt was being dropped here)
        # ════════════════════════════════════════════════════════════
        if result.get("pending_interrupt"):
            response["pending_interrupt"] = result["pending_interrupt"]
            response["requires_input"] = True

        # ════════════════════════════════════════════════════════════
        # REDEMPTION EVENT: Check if trust dropped to critical level
        # ════════════════════════════════════════════════════════════
        if result.get("redemption_event"):
            response["state"] = "awaiting_redemption_choice"
            response["redemption_event"] = result["redemption_event"]
            # Store pending redemption for the endpoint
            world.pending_redemption = result["redemption_event"]
            print(f"[ALERT] REDEMPTION TRIGGERED for {result['redemption_event']['marshal']}")

        # Notifications — insist can cause battle → combat notifications
        if world.notifications.has_pending():
            response["notifications"] = world.notifications.get_pending()

        return response
    except Exception as e:
        print(f"[ERROR] handling objection response: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "game_state": world.get_filtered_game_state_summary()
        }


@app.post("/capture_choice")
def capture_choice(request: CaptureChoiceResponse):
    """Respond to the plunder/secure choice after capturing a region (Phase 6.2.E).

    Args:
        request: CaptureChoiceResponse with 'choice' field ('plunder' or 'secure')
    """
    try:
        result = executor.handle_capture_choice(request.choice, game_state)

        response = {
            "success": result.get("success", False),
            "message": result.get("message", "Choice processed"),
            "events": result.get("events", []),
            "capture_choice": result.get("capture_choice"),
            "action_summary": world.get_action_summary(),
            "game_state": world.get_filtered_game_state_summary(),
        }
        return response
    except Exception as e:
        print(f"ERROR handling capture choice: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "game_state": world.get_filtered_game_state_summary()
        }


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
        # Check for pending redemption
        if not hasattr(world, 'pending_redemption') or world.pending_redemption is None:
            return {
                "success": False,
                "message": "No redemption event pending.",
                "game_state": world.get_filtered_game_state_summary()
            }

        redemption_event = world.pending_redemption

        # Validate choice (Phase 3: administrative_role replaces demand_obedience)
        valid_choices = ['grant_autonomy', 'administrative_role', 'dismiss']
        if request.choice not in valid_choices:
            return {
                "success": False,
                "message": f"Invalid choice: '{request.choice}'. Valid: {', '.join(valid_choices)}",
                "game_state": world.get_filtered_game_state_summary()
            }

        # Process the redemption response
        result = world.disobedience_system.handle_redemption_response(
            redemption_event=redemption_event,
            choice=request.choice,
            game_state=game_state
        )

        # Clear pending redemption
        world.pending_redemption = None

        return {
            "success": result.get("success", False),
            "message": result.get("message", "Redemption processed"),
            "choice": request.choice,
            "autonomous": result.get("autonomous", False),
            "autonomy_turns": result.get("autonomy_turns", 0),
            "dismissed": result.get("dismissed", False),
            "administrative": result.get("administrative", False),
            "new_max_actions": result.get("new_max_actions", 0),
            "troops_frozen": result.get("troops_frozen", 0),
            "authority_bonus": result.get("authority_bonus", 0),
            "action_summary": world.get_action_summary(),
            "game_state": world.get_filtered_game_state_summary()
        }
    except Exception as e:
        print(f"[ERROR] handling redemption response: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "game_state": world.get_filtered_game_state_summary()
        }


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
        # Validate choice
        valid_choices = ['charge', 'restrain']
        if request.choice not in valid_choices:
            return {
                "success": False,
                "message": f"Invalid choice: '{request.choice}'. Valid: {', '.join(valid_choices)}",
                "game_state": world.get_filtered_game_state_summary()
            }

        # Process the response through executor
        result = executor.respond_to_glorious_charge(request.choice, world)

        response = {
            "success": result.get("success", False),
            "message": result.get("message", "Charge processed"),
            "choice": request.choice,
            "events": result.get("events", []),
            "action_summary": world.get_action_summary(),
            "game_state": world.get_filtered_game_state_summary()
        }
        if result.get("battle_report"):
            response["battle_report"] = result["battle_report"]
        # Notifications — charge combat can trigger counter-punch/drill-cancelled
        if world.notifications.has_pending():
            response["notifications"] = world.notifications.get_pending()
        return response
    except Exception as e:
        print(f"[ERROR] handling Glorious Charge response: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "game_state": world.get_filtered_game_state_summary()
        }


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
        from backend.commands.strategic import StrategicExecutor
        strategic_exec = StrategicExecutor(executor)
        result = strategic_exec.handle_response(
            request.marshal_name, request.response_type,
            request.choice, world, game_state
        )

        response = {
            "success": result.get("success", False),
            "message": result.get("message", "Response processed"),
            "order_cleared": result.get("order_cleared", False),
            "trust_change": result.get("trust_change", 0),
            "action_taken": result.get("action_taken"),
            "action_summary": world.get_action_summary(),
            "game_state": world.get_filtered_game_state_summary()
        }
        # Notifications — interrupt responses can trigger actions
        if world.notifications.has_pending():
            response["notifications"] = world.notifications.get_pending()
        return response
    except Exception as e:
        print(f"[ERROR] handling strategic response: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "game_state": world.get_filtered_game_state_summary()
        }


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

@app.post("/save")
async def save_endpoint(request: SaveRequest):
    """Save current game state."""
    global world
    result = save_game(world, save_name=request.save_name)
    return result


@app.post("/load")
async def load_endpoint(request: LoadRequest):
    """Load a saved game. Replaces current game state."""
    global world, game_state
    filepath = Path("saves") / request.filename
    result = load_game(filepath)
    if result["success"]:
        world = result["world"]
        game_state["world"] = world
        # Return game state summary so Godot can refresh
        return {
            "success": True,
            "message": result["message"],
            "game_state": world.get_filtered_game_state_summary()
        }
    return {"success": False, "message": result["message"]}


@app.get("/saves")
async def list_saves_endpoint():
    """List all available save files."""
    saves = list_saves()
    return {"saves": saves}


@app.post("/delete_save")
async def delete_save_endpoint(request: DeleteSaveRequest):
    """Delete a save file."""
    filepath = Path("saves") / request.filename
    return delete_save(filepath)


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
        return {"success": True, "dismissed": int(count)}
    dismissed = world.notifications.dismiss(notification_id)
    return {"success": dismissed, "dismissed": 1 if dismissed else 0}


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
    marshal.trust._value = max(0, min(100, int(trust_value)))

    print(f"[DEBUG] Set {marshal_name} trust: {old_trust} -> {marshal.trust.value}")

    return {
        "success": True,
        "marshal": marshal_name,
        "old_trust": old_trust,
        "new_trust": int(marshal.trust.value),
        "trust_label": marshal.trust.get_label()
    }


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
    marshal.trust._value = 15  # Set to critical level

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

    return {
        "success": True,
        "old_authority": old_authority,
        "new_authority": int(world.authority_tracker.authority),
        "authority_label": world.authority_tracker.get_authority_label()
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