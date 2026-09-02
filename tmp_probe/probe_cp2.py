import contextlib, io, sys
sys.stdout.reconfigure(encoding="utf-8")
from backend.models.world_state import WorldState
from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
P = "godot-client/project-sovereign/assets/maps/europe_1805.json"
with contextlib.redirect_stdout(io.StringIO()):
    w = WorldState.from_scenario(P)
print("Tyrol adj:", w.get_region("Tyrol").adjacent_regions)
print("Carniola adj:", w.get_region("Carniola").adjacent_regions)
