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

j = w.marshals["ArchdukeJohn"]; j.location = "Tyrol"; j.strength = 20000
w.marshals["Ney"].location = "Munich"; w.marshals["Ney"].strength = 3000
for n, s in (("Massena", 15000), ("Lannes", 15000), ("Davout", 15000)):
    w.marshals[n].location = "Milan"; w.marshals[n].strength = s
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
random.seed(3)
with contextlib.redirect_stdout(io.StringIO()):
    r1 = c.post("/command", json={"command": "Ney, attack ArchdukeJohn"}).json()
msg = (r1.get("message") or "")
print("PLAYER ATTACK (last 500):", msg[-500:])
print("John counter_punch_available:", j.counter_punch_available, "| John:", j.strength, "Ney:", w.marshals['Ney'].strength)
print()
before = {n: w.marshals[n].strength for n in ("Massena","Lannes","Davout")}
with contextlib.redirect_stdout(io.StringIO()):
    r2 = c.post("/command", json={"command": "end turn"}).json()
print("counter-punch decisions:", hits)
ep = r2.get("enemy_phase") or {}
for a in (ep.get("actions") or []):
    s = str(a.get("message") or "")
    if "ArchdukeJohn" in s or "Archduke John" in s:
        print("ENEMY PHASE:", s[:800]); print()
print("Milan before:", before)
print("Milan after :", {n: w.marshals[n].strength for n in ("Massena","Lannes","Davout")})
print("John:", j.strength, "@", j.location)
