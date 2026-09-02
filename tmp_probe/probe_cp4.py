import contextlib, io, sys
sys.stdout.reconfigure(encoding="utf-8")
from backend.models.world_state import WorldState
from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
P = "godot-client/project-sovereign/assets/maps/europe_1805.json"
with contextlib.redirect_stdout(io.StringIO()):
    w = WorldState.from_scenario(P)

j = w.marshals["ArchdukeJohn"]
j.location = "Tyrol"; j.strength = 20000
for n, s in (("Massena", 42000), ("Ney", 24000)):
    w.marshals[n].location = "Milan"; w.marshals[n].strength = s
for n in ("Davout","Soult","Lannes","Bernadotte","Napoleon","Murat"):
    w.marshals[n].location = "Paris"
w.marshals["Deroy"].location = "Berlin"
w.invalidate_active_nations_cache(); w.refresh_marshal_indexes()
j.counter_punch_available = True

ai = EnemyAI(CommandExecutor())
with contextlib.redirect_stdout(io.StringIO()) as buf:
    act = ai._get_counter_punch_action(j, "Austria", w)
print("DIRECT ->", act, " ratio 20000/66000 =", round(20000/66000, 3))

ai2 = EnemyAI(CommandExecutor())
with contextlib.redirect_stdout(io.StringIO()) as buf2:
    res = ai2._evaluate_marshal(j, "Austria", w)
print("FULL _evaluate_marshal ->", res)
for line in buf2.getvalue().splitlines():
    if any(k in line for k in ("P3", "COUNTER", "P2", "P4", "THREAT")):
        print("   |", line)
