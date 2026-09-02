import contextlib, io, sys
sys.stdout.reconfigure(encoding="utf-8")
from backend.models.world_state import WorldState
from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.models.marshal import Stance
P = "godot-client/project-sovereign/assets/maps/europe_1805.json"
with contextlib.redirect_stdout(io.StringIO()):
    w = WorldState.from_scenario(P)
j = w.marshals["ArchdukeJohn"]; j.location = "Tyrol"; j.strength = 20000
j.stance = Stance.DEFENSIVE
j.counter_punch_available = True
w.marshals["Massena"].location = "Milan"; w.marshals["Massena"].strength = 60000
for n in ("Ney","Davout","Soult","Lannes","Bernadotte","Napoleon","Murat"):
    w.marshals[n].location = "Paris"
w.marshals["Deroy"].location = "Berlin"
w.invalidate_active_nations_cache(); w.refresh_marshal_indexes()
ai = EnemyAI(CommandExecutor())
ai._unfortified_this_turn = {"ArchdukeJohn"}      # the documented refortify block
with contextlib.redirect_stdout(io.StringIO()) as b:
    res = ai._evaluate_marshal(j, "Austria", w)
print("20,000 cautious vs a SINGLE adjacent 60,000 corps, ratio 0.33")
print("  _evaluate_marshal ->", res)
