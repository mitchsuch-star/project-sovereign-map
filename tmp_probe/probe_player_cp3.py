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
    M.parser = CommandParser(use_real_llm=False); M.world = w; M.game_state = {"world": w}
assert M.parser.llm.use_real_api is False

j = w.marshals["ArchdukeJohn"]; j.location = "Tyrol"; j.strength = 26000
w.marshals["Ney"].location = "Munich"; w.marshals["Ney"].strength = 16000
for n in ("Massena", "Lannes", "Davout"):
    m = w.marshals[n]; m.location = "Milan"; m.strength = 15000
    m.fortified = True; m.defense_bonus = 0.15
for n in ("Soult","Bernadotte","Napoleon","Murat"):
    w.marshals[n].location = "Paris"
w.marshals["Deroy"].location = "Berlin"; w.marshals["Mack"].location = "Vienna"
w.marshals["ArchdukeCharles"].location = "Hungary"
w.invalidate_active_nations_cache(); w.refresh_marshal_indexes()

hits = []
orig = EnemyAI._get_counter_punch_action
def wrapped(self, marshal, nation, world):
    r = orig(self, marshal, nation, world)
    if r:
        t = world.marshals.get(r["target"])
        field = sum(m.strength for m in world.marshals.values()
                    if t and m.location == t.location and m.nation == t.nation and m.strength > 0)
        hits.append((marshal.name, marshal.strength, r["target"], t.strength if t else 0,
                     t.location if t else "?", field))
    return r
EnemyAI._get_counter_punch_action = wrapped

c = TestClient(M.app)
random.seed(5)
with contextlib.redirect_stdout(io.StringIO()):
    r1 = c.post("/command", json={"command": "Ney, attack ArchdukeJohn"}).json()
print("PLAYER ATTACK tail:", (r1.get("message") or "")[-380:])
print("counter_punch granted:", j.counter_punch_available, "| John:", j.strength, "Ney:", w.marshals['Ney'].strength, "@", w.marshals['Ney'].location)
before = {n: w.marshals[n].strength for n in ("Massena","Lannes","Davout")}
with contextlib.redirect_stdout(io.StringIO()):
    r2 = c.post("/command", json={"command": "end turn"}).json()
print("\ncounter-punch decisions:", hits)
ep = r2.get("enemy_phase") or {}
for a in (ep.get("actions") or []):
    s = str(a.get("message") or "")
    if "John" in s:
        print("\nENEMY PHASE:", s[:900])
print("\nMilan before:", before, "\nMilan after :", {n: w.marshals[n].strength for n in ("Massena","Lannes","Davout")})
print("John:", j.strength, "@", j.location)
