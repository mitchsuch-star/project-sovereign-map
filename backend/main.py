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


@app.post("/command")
async def execute_command(request: CommandRequest):
    """Execute a game command and return result."""
    try:
        # Parse command
        parsed = parser.parse(request.command)

        # Execute command
        result = executor.execute(parsed, game_state)

        return {
            "success": True,
            "message": result.get("message", "Command executed"),
            "events": result.get("events", []),
            "game_state": world.get_game_state_summary()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "events": [],
            "game_state": world.get_game_state_summary()
        }


@app.get("/status")
async def get_status():
    """Get current game status."""
    return world.get_game_state_summary()


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Project Sovereign API Server...")
    print("📍 Server running at: http://127.0.0.1:8005")
    print("📖 Docs at: http://127.0.0.1:8005/docs")
    uvicorn.run(app, host="127.0.0.1", port=8005)