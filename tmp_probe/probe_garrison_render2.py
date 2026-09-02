import contextlib, io, os, sys, json, random
sys.stdout.reconfigure(encoding="utf-8")
os.environ["SOVEREIGN_SEED"] = "ulm"
from fastapi.testclient import TestClient
import backend.main as M
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState
P = "godot-client/project-sovereign/assets/maps/europe_1805.json"
with contextlib.redirect_stdout(io.StringIO()):
    w = WorldState.from_scenario(P, seed="ulm")
    M.parser = CommandParser(use_real_llm=False); M.world = w; M.game_state = {"world": w}
assert M.parser.llm.use_real_api is False
r = w.regions["Munich"]; r.controller = "France"; r.garrison_strength = 10000
c = w.marshals["ArchdukeCharles"]; c.location = "Tyrol"; c.strength = 29000
for n in ("Mack","ArchdukeJohn"): w.marshals[n].location = "Vienna"
for n in ("Ney","Davout","Soult","Lannes","Bernadotte","Massena","Napoleon","Murat"):
    w.marshals[n].location = "Paris"
w.marshals["Deroy"].location = "Berlin"
w.invalidate_active_nations_cache(); w.refresh_marshal_indexes()
cl = TestClient(M.app)
random.seed(2)
with contextlib.redirect_stdout(io.StringIO()):
    resp = cl.post("/command", json={"command": "end turn"}).json()
print("top-level keys:", sorted(resp.keys()))
ep = resp.get("enemy_phase")
print("enemy_phase type:", type(ep), "keys:", sorted(ep.keys()) if isinstance(ep, dict) else ep)
if isinstance(ep, dict):
    print("actions:", len(ep.get("actions") or []), "| summary:", str(ep.get("summary"))[:300])
    for a in (ep.get("actions") or [])[:40]:
        print("  ", a.get("nation"), a.get("marshal"), a.get("action_type"), "->", a.get("target"),
              [e.get("type") for e in (a.get("events") or [])])
print("\nMunich:", w.regions["Munich"].controller, w.regions["Munich"].garrison_strength,
      "| Charles:", w.marshals["ArchdukeCharles"].strength, "@", w.marshals["ArchdukeCharles"].location)
print("\nmessage tail:", str(resp.get("message"))[-600:])

print("\n=== nations block ===")
for nat in (ep.get("nations") or []):
    print("NATION:", nat.get("nation"))
    for a in (nat.get("actions") or []):
        print("   action_type:", a.get("action_type"), "| target:", a.get("target"),
              "| events:", [e.get("type") for e in (a.get("events") or [])],
              "| has battle_report:", "battle_report" in a)
        print("   keys:", sorted(a.keys()))
        print("   events full:", json.dumps(a.get("events"))[:500])

print("
=== nations block ===")
print(json.dumps(ep.get("nations"), indent=1)[:4000])
