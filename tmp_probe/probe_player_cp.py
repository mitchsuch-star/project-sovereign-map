import contextlib, io, os, sys, random
sys.stdout.reconfigure(encoding="utf-8")
os.environ["SOVEREIGN_SEED"] = "ulm"
from fastapi.testclient import TestClient
import backend.main as M
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState
from backend.ai.enemy_ai import EnemyAI

P = "godot-client/project-sovereign/assets/maps/europe_1805.json"
with contextlib.redirect_stdout(io.StringIO()):
    w = WorldState.from_scenario(P, seed="ulm")
    M.parser = CommandParser(use_real_llm=False)
    M.world = w
    M.game_state = {"world": w}
assert M.parser.llm.use_real_api is False

j = w.marshals["ArchdukeJohn"]; j.location = "Tyrol"; j.strength = 20000
for n, s in (("Massena", 15000), ("Ney", 15000), ("Lannes", 15000)):
    w.marshals[n].location = "Milan"; w.marshals[n].strength = s
for n in ("Davout","Soult","Bernadotte","Napoleon","Murat"):
    w.marshals[n].location = "Paris"
w.marshals["Deroy"].location = "Berlin"
w.marshals["Mack"].location = "Vienna"
w.marshals["ArchdukeCharles"].location = "Hungary"
w.invalidate_active_nations_cache(); w.refresh_marshal_indexes()

hits = []
orig = EnemyAI._get_counter_punch_action
def wrapped(self, marshal, nation, world):
    r = orig(self, marshal, nation, world)
    if r:
        tgt = world.marshals.get(r["target"])
        field = sum(m.strength for m in world.marshals.values()
                    if tgt and m.location == tgt.location and m.nation == tgt.nation and m.strength > 0)
        hits.append((marshal.name, marshal.strength, r["target"],
                     tgt.strength if tgt else 0, field))
    return r
EnemyAI._get_counter_punch_action = wrapped

c = TestClient(M.app)
random.seed(11)
with contextlib.redirect_stdout(io.StringIO()):
    r1 = c.post("/command", json={"command": "Ney, attack ArchdukeJohn"}).json()
print("PLAYER ATTACK ->", (r1.get("message") or "")[:600])
print("John counter_punch_available:", j.counter_punch_available)
print("Ney:", w.marshals['Ney'].strength, "John:", j.strength)
print()
with contextlib.redirect_stdout(io.StringIO()):
    r2 = c.post("/command", json={"command": "end turn"}).json()
print("counter-punch decisions:", hits)
ep = r2.get("enemy_phase") or {}
for a in (ep.get("actions") or []):
    if a.get("marshal") in ("ArchdukeJohn",) or "ArchdukeJohn" in str(a.get("message","")):
        print("ENEMY PHASE:", str(a.get("message"))[:700])
print()
print("after: Ney", w.marshals['Ney'].strength, "Massena", w.marshals['Massena'].strength,
      "Lannes", w.marshals['Lannes'].strength, "John", j.strength, "@", j.location)
