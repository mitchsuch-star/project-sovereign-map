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

# France holds Munich with a 10,000 capital-style garrison and NO field army in it.
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
ep = resp.get("enemy_phase") or {}
for a in (ep.get("actions") or []):
    if a.get("marshal") == "ArchdukeCharles" or "Charles" in str(a.get("message","")):
        print("action_type :", a.get("action_type"), "| target:", a.get("target"))
        print("keys        :", sorted(a.keys()))
        print("events      :", json.dumps(a.get("events"), indent=2)[:800])
        print("battle_report present:", "battle_report" in a)
        print("message     :", str(a.get("message"))[:400])
        print("-"*60)
print("Munich garrison now:", w.regions["Munich"].garrison_strength, "| Charles:", w.marshals["ArchdukeCharles"].strength)

print("\n=== ALL enemy_phase actions ===")
import json as _j
for a in (ep.get("actions") or []):
    print(a.get("nation"), "|", a.get("marshal"), "|", a.get("action_type"), "->", a.get("target"),
          "| events:", [e.get("type") for e in (a.get("events") or [])])
print("\nMunich controller:", w.regions["Munich"].controller)
