import contextlib, io, sys
sys.stdout.reconfigure(encoding="utf-8")
from backend.models.world_state import WorldState
from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
P = "godot-client/project-sovereign/assets/maps/europe_1805.json"
with contextlib.redirect_stdout(io.StringIO()):
    w = WorldState.from_scenario(P)

# Find a cautious Austrian marshal
for n, m in w.marshals.items():
    print(n, m.nation, m.personality, m.location, m.strength)
