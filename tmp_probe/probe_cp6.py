import contextlib, io, sys, random
sys.stdout.reconfigure(encoding="utf-8")
from backend.models.world_state import WorldState
from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
P = "godot-client/project-sovereign/assets/maps/europe_1805.json"

def build():
    with contextlib.redirect_stdout(io.StringIO()):
        w = WorldState.from_scenario(P)
    j = w.marshals["ArchdukeJohn"]
    j.location = "Tyrol"; j.strength = 20000
    for n, s in (("Massena", 15000), ("Ney", 15000), ("Lannes", 15000)):
        w.marshals[n].location = "Milan"; w.marshals[n].strength = s
    for n in ("Davout","Soult","Bernadotte","Napoleon","Murat"):
        w.marshals[n].location = "Paris"
    w.marshals["Deroy"].location = "Berlin"
    w.invalidate_active_nations_cache(); w.refresh_marshal_indexes()
    j.counter_punch_available = True
    return w, j

random.seed(7)
w, j = build()
ai = EnemyAI(CommandExecutor())
gs = {"world": w}
with contextlib.redirect_stdout(io.StringIO()) as buf:
    res = ai._evaluate_marshal(j, "Austria", w)
    act = res[0]
    out = ai._execute_action(act, gs)
print("decision:", act)
print("success:", out.get("success"))
print("MESSAGE:\n", (out.get("message") or "")[:1400])
print("\nJohn strength after:", w.marshals["ArchdukeJohn"].strength,
      "| Ney:", w.marshals["Ney"].strength,
      "| Massena:", w.marshals["Massena"].strength,
      "| Lannes:", w.marshals["Lannes"].strength)
