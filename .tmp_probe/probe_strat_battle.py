import contextlib, io, sys, json
sys.stdout.reconfigure(encoding="utf-8")
from fastapi.testclient import TestClient
import backend.main as M
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState
from backend.models.marshal import StrategicOrder
P = "godot-client/project-sovereign/assets/maps/europe_1805.json"
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    w = WorldState.from_scenario(P)
    M.parser = CommandParser(use_real_llm=False)
    M.world = w
    M.game_state = {"world": w}
c = TestClient(M.app)

ney = w.get_marshal("Ney"); mack = w.get_marshal("Mack")
mack.strength = 15000
ney.strength = 40000
ney.location = "Rhineland"
mack.location = "Frankfurt"
reg = w.get_region("Rhineland")
print("Rhineland adj:", reg.adjacent_regions)
print("Mack at", mack.location)
ney.strategic_order = StrategicOrder(command_type="MOVE_TO", target="Frankfurt",
    target_type="region", started_turn=0, original_command="Ney, march to Frankfurt",
    issued_turn=-1, path=["Frankfurt"])
with contextlib.redirect_stdout(buf):
    r = c.post("/command", json={"command": "end turn"}).json()
print("TOP-LEVEL KEYS:", sorted(r.keys()))
print("has top-level battle_report:", "battle_report" in r)
sr = r.get("strategic_reports") or []
print("strategic_reports n:", len(sr))
for row in sr:
    print("  row keys:", sorted(row.keys()))
    print("  action:", row.get("action"), "outcome:", row.get("outcome"), "status:", row.get("order_status"))
    print("  message:", (row.get("message") or "")[:160])
    print("  battle_report is None:", row.get("battle_report") is None)
    bd = row.get("battle_details")
    print("  battle_details success:", (bd or {}).get("success"))
print("battles this turn:", len(w.battles_this_turn))
