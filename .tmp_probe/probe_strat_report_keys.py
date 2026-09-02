import contextlib, io, sys, json
sys.stdout.reconfigure(encoding="utf-8")
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicOrderProcessor
from backend.models.marshal import StrategicOrder
P = "godot-client/project-sovereign/assets/maps/europe_1805.json"
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    w = WorldState.from_scenario(P)
ney = w.get_marshal("Ney"); mack = w.get_marshal("Mack")
ney.location = "Rhineland"; ney.strength = 40000
mack.location = "Frankfurt"; mack.strength = 15000
with contextlib.redirect_stdout(buf):
    w.calculate_visibility()
ney.strategic_order = StrategicOrder(command_type="MOVE_TO", target="Frankfurt",
    target_type="region", started_turn=0, original_command="Ney, march to Frankfurt",
    issued_turn=-1, path=["Frankfurt"])
proc = StrategicOrderProcessor(CommandExecutor())
with contextlib.redirect_stdout(buf):
    reports = proc.process_strategic_orders(w, {"world": w})
for r in reports:
    print("keys:", sorted(r.keys()))
    print("action:", r.get("action"), "| outcome:", r.get("outcome"), "| status:", r.get("order_status"))
    print("message:", (r.get("message") or "")[:200])
    br = r.get("battle_report")
    print("battle_report is None:", br is None, "| type:", type(br).__name__)
    if isinstance(br, dict):
        print("battle_report keys:", sorted(br.keys())[:12])
    bd = r.get("battle_details")
    if isinstance(bd, dict):
        print("battle_details keys:", sorted(bd.keys())[:20])
        print("battle_details success:", bd.get("success"))
print("battles_this_turn:", len(w.battles_this_turn))
print("Ney", ney.location, ney.strength, "| Mack", mack.location, mack.strength)

print("=== raw battle event ===")
for r in reports:
    bd = r.get("battle_details") or {}
    for evt in bd.get("events", []):
        print("evt type:", evt.get("type"), "| outcome:", repr(evt.get("outcome")), "| victor:", repr(evt.get("victor")), "| enemy_destroyed:", evt.get("enemy_destroyed"))
