"""
FastAPI server for Project Sovereign
Connects Godot frontend to Python game logic
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.commands.parser import CommandParser
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState

# ════════════════════════════════════════════════════════════
# DEBUG MODE: Set to True to enable debug endpoints
# ════════════════════════════════════════════════════════════
DEBUG_MODE = True  # Set to False for production

# Initialize game
app = FastAPI(title="Project Sovereign API")
parser = CommandParser(use_real_llm=False)
executor = CommandExecutor()
world = WorldState(player_nation="France")
game_state = {"world": world, "debug_mode": DEBUG_MODE}

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


@app.get("/test")
def test_connection():
    """Test endpoint for Godot connection."""
    return {
        "status": "ok",
        "message": "Backend is running",
        "turn": int(world.current_turn),
        "gold": int(world.gold),
        "action_summary": world.get_action_summary(),
        "game_state": world.get_game_state_summary()
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
        # Parse command
        parsed = parser.parse(request.command)
        print(f"[OK] Parsed: {parsed.get('command', {}).get('action', 'unknown')}")

        # Execute command
        result = executor.execute(parsed, game_state)

        # ════════════════════════════════════════════════════════════
        # CHECK FOR OBJECTION: If awaiting player choice, return full result
        # ════════════════════════════════════════════════════════════
        if result.get("state") == "awaiting_player_choice":
            print(f"🛑 OBJECTION RESPONSE - Returning full result to frontend")
            # Return the full objection result plus action summary
            result["action_summary"] = world.get_action_summary()
            result["game_state"] = world.get_game_state_summary()
            return result

        # Get action summary
        action_summary = world.get_action_summary()

        response = {
            "success": result.get("success", False),
            "message": result.get("message", "Command executed"),
            "events": result.get("events", []),
            "action_info": result.get("action_info", {}),
            "action_summary": action_summary,
            "game_state": world.get_game_state_summary()
        }

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
                    cleaned_actions.append(cleaned_action)
                cleaned_phase["nations"][nation] = {
                    "actions": cleaned_actions,
                    "action_count": nation_data.get("action_count", 0)
                }
            if enemy_phase.get("enemy_victory"):
                cleaned_phase["enemy_victory"] = enemy_phase["enemy_victory"]
            response["enemy_phase"] = cleaned_phase

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
            "game_state": world.get_game_state_summary()
        }


@app.get("/status")
def get_status():
    """Get current game status."""
    return world.get_game_state_summary()


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
        "severity": objection.get("severity", 0.5),
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
            "game_state": world.get_game_state_summary()
        }

        # ════════════════════════════════════════════════════════════
        # REDEMPTION EVENT: Check if trust dropped to critical level
        # ════════════════════════════════════════════════════════════
        if result.get("redemption_event"):
            response["state"] = "awaiting_redemption_choice"
            response["redemption_event"] = result["redemption_event"]
            # Store pending redemption for the endpoint
            world.pending_redemption = result["redemption_event"]
            print(f"🚨 REDEMPTION TRIGGERED for {result['redemption_event']['marshal']}")

        return response
    except Exception as e:
        print(f"❌ ERROR handling objection response: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "game_state": world.get_game_state_summary()
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
                "game_state": world.get_game_state_summary()
            }

        redemption_event = world.pending_redemption

        # Validate choice
        valid_choices = ['grant_autonomy', 'dismiss', 'demand_obedience']
        if request.choice not in valid_choices:
            return {
                "success": False,
                "message": f"Invalid choice: '{request.choice}'. Valid: {', '.join(valid_choices)}",
                "game_state": world.get_game_state_summary()
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
            "strained": result.get("strained", False),
            "action_summary": world.get_action_summary(),
            "game_state": world.get_game_state_summary()
        }
    except Exception as e:
        print(f"❌ ERROR handling redemption response: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "game_state": world.get_game_state_summary()
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
            "affects_trust_gains": world.authority_tracker.get_trust_gain_modifier()
        },
        "location": marshal.location,
        "strength": int(marshal.strength),
        "morale": int(marshal.morale)
    }


def _get_map_data(world: WorldState) -> dict:
    """Get map visualization data with marshal debug info."""
    map_data = {}

    for region_name, region in world.regions.items():
        # Find ALL marshals in this region (player + enemy)
        all_marshals_here = world.get_marshals_in_region(region_name)

        # Build marshal data with debug info
        marshals_data = []
        for m in all_marshals_here:
            marshal_data = {
                "name": m.name,
                "nation": m.nation,
                "strength": int(m.strength),
                "morale": int(m.morale),
                "movement_range": int(m.movement_range)
            }

            # Add debug info for player marshals
            if m.nation == world.player_nation:
                marshal_data["personality"] = m.personality
                marshal_data["trust"] = int(m.trust.value) if hasattr(m, 'trust') else 70
                marshal_data["trust_label"] = m.trust.get_label() if hasattr(m, 'trust') else "Unknown"

                # Get vindication data
                vindication_data = world.vindication_tracker.get_vindication_data(m.name)
                marshal_data["vindication"] = vindication_data.get("score", 0)
                marshal_data["has_pending_vindication"] = world.vindication_tracker.has_pending(m.name)

                # Tactical states for hover info
                marshal_data["tactical_state"] = {
                    # Drill state
                    "drilling": bool(getattr(m, 'drilling', False)),
                    "drilling_locked": bool(getattr(m, 'drilling_locked', False)),
                    "shock_bonus": int(getattr(m, 'shock_bonus', 0)),
                    "drill_complete_turn": int(getattr(m, 'drill_complete_turn', -1)),
                    # Fortify state
                    "fortified": bool(getattr(m, 'fortified', False)),
                    "defense_bonus": int(getattr(m, 'defense_bonus', 0)),
                    "fortify_expires_turn": int(getattr(m, 'fortify_expires_turn', -1)),
                    # Retreat state
                    "retreating": bool(getattr(m, 'retreating', False)),
                    "retreat_recovery": int(getattr(m, 'retreat_recovery', 0)),
                }

            marshals_data.append(marshal_data)

        controller = region.controller or "Neutral"
        map_data[region_name] = {
            "controller": controller,
            "marshals": marshals_data
        }

        # Debug: Show captured regions
        if controller == "France" and region_name in ["Waterloo", "Netherlands", "Bavaria", "Vienna"]:
            print(f"🚩 {region_name} is now controlled by France!")

    return map_data


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

    print(f"🔧 DEBUG: Set {marshal_name} trust: {old_trust} → {marshal.trust.value}")

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

    print(f"🔧 DEBUG: Triggered redemption for {marshal_name} (trust: {old_trust} → 15)")

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

    print(f"🔧 DEBUG: Set authority: {old_authority} → {world.authority_tracker.authority}")

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