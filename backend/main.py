"""
FastAPI server for Project Sovereign
Connects Godot frontend to Python game logic
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.commands.parser import CommandParser
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState

# Initialize game
app = FastAPI(title="Project Sovereign API")
parser = CommandParser(use_real_llm=False)
executor = CommandExecutor()
world = WorldState(player_nation="France")
game_state = {"world": world}

# Allow Godot to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CommandRequest(BaseModel):
    command: str


@app.get("/test")
def test_connection():
    """Test endpoint for Godot connection."""
    return {
        "status": "ok",
        "message": "Backend is running",
        "turn": int(world.current_turn),
        "gold": int(world.gold),
        "action_summary": world.get_action_summary()
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
        print(f"✅ Parsed: {parsed.get('command', {}).get('action', 'unknown')}")

        # Execute command
        result = executor.execute(parsed, game_state)

        # print(f"📤 RESULT:")
        # print(f"   Success: {result.get('success')}")
        # print(f"   Actions after: {world.actions_remaining}/{world.max_actions_per_turn}")
        # print(f"{'=' * 60}\n")

        # Get action summary
        action_summary = world.get_action_summary()

        return {
            "success": result.get("success", False),
            "message": result.get("message", "Command executed"),
            "events": result.get("events", []),
            "action_info": result.get("action_info", {}),
            "action_summary": action_summary,
            "game_state": world.get_game_state_summary()
        }
    except Exception as e:
        print(f"❌ ERROR: {e}")
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


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("🚀 GAME INITIALIZED")
    print("=" * 60)
    print(f"Turn: {world.current_turn}")
    print(f"Actions: {world.actions_remaining}/{world.max_actions_per_turn}")
    print(f"Gold: {world.gold}")
    print(f"Regions: {len(world.get_player_regions())}")
    print("=" * 60)
    print("📍 Server: http://127.0.0.1:8000")
    print("📖 API Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)

    uvicorn.run(app, host="127.0.0.1", port=8005)