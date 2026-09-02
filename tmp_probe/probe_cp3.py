import contextlib, io, sys
sys.stdout.reconfigure(encoding="utf-8")
from backend.models.world_state import WorldState
from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
P = "godot-client/project-sovereign/assets/maps/europe_1805.json"
with contextlib.redirect_stdout(io.StringIO()):
    w = WorldState.from_scenario(P)

# ArchdukeJohn (Austria, cautious, 20,000) at Tyrol.
j = w.marshals["ArchdukeJohn"]
j.location = "Tyrol"; j.strength = 20000
# A French army of 88,000 in Milan (adjacent to Tyrol)
for n, s in (("Massena", 42000), ("Ney", 24000), ("Murat", 22000)):
    w.marshals[n].location = "Milan"; w.marshals[n].strength = s
# Clear everyone else out of the way
for n in ("Davout","Soult","Lannes","Bernadotte","Napoleon"):
    w.marshals[n].location = "Paris"
w.invalidate_active_nations_cache(); w.refresh_marshal_indexes()

ai = EnemyAI(CommandExecutor())
print("has_counter_punch (before grant):", j.has_counter_punch())
j.counter_punch_available = True
print("has_counter_punch (after grant):", j.has_counter_punch())
with contextlib.redirect_stdout(io.StringIO()) as buf:
    act = ai._get_counter_punch_action(j, "Austria", w)
print("DIRECT _get_counter_punch_action ->", act)
print("  20,000 vs 88,000 in Milan; ratio =", 20000/88000)

# Now the full decision path
ai2 = EnemyAI(CommandExecutor())
with contextlib.redirect_stdout(io.StringIO()) as buf2:
    res = ai2._evaluate_marshal(j, "Austria", w)
print("FULL _evaluate_marshal ->", res)
txt = buf2.getvalue()
for line in txt.splitlines():
    if "P3.25" in line or "COUNTER" in line.upper() or "P3:" in line:
        print("   |", line)
