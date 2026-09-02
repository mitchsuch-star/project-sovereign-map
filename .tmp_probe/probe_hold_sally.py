import contextlib, io, sys, json
sys.stdout.reconfigure(encoding="utf-8")
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicOrderProcessor
from backend.models.marshal import StrategicOrder
P = "godot-client/project-sovereign/assets/maps/europe_1805.json"
with contextlib.redirect_stdout(io.StringIO()):
    w = WorldState.from_scenario(P)

ney = w.get_marshal("Ney")
moore = w.get_marshal("Moore")
print("Ney personality:", ney.personality, "| artillery:", getattr(ney,"artillery",False))
print("Moore:", moore.nation, moore.location, moore.strength)
ney.location = "Normandy"
moore.location = "London"
moore.strength = 20000
ney.strength = 40000
with contextlib.redirect_stdout(io.StringIO()):
    w.calculate_visibility()
reg = w.get_region("Normandy")
print("Normandy adjacent:", reg.adjacent_regions)
print("at war FR/GB:", w.is_at_war("France","Britain"))
from backend.game_logic.naval import crossing_check_reach
print("crossing:", crossing_check_reach(w,"France","Normandy","London",40000))

ney.strategic_order = StrategicOrder(command_type="HOLD", target="Normandy",
                                     target_type="region", started_turn=0, original_command="Ney, hold Normandy", issued_turn=-1)
ney.holding_position = True
ney.hold_region = "Normandy"

proc = StrategicOrderProcessor(CommandExecutor())
before_battles = len(w.battles_this_turn)
with contextlib.redirect_stdout(io.StringIO()):
    reports = proc.process_strategic_orders(w, {"world": w})
for r in reports:
    print("---- REPORT ----")
    print("action:", r.get("action"), "| outcome:", repr(r.get("outcome")), "| status:", r.get("order_status"))
    print("message:", r.get("message"))
    bd = r.get("battle_details")
    if bd is not None:
        print("battle_details.success:", bd.get("success"))
        print("battle_details.message:", (bd.get("message") or "")[:200])
        print("battle_details.blocked_naval:", bd.get("blocked_naval"))
    print("battle_message:", repr((r.get("battle_message") or "")[:200]))
    print("battle_report present:", r.get("battle_report") is not None)
print("battles recorded:", len(w.battles_this_turn) - before_battles)
print("Ney loc:", ney.location, "str:", ney.strength, "| Moore loc:", moore.location, "str:", moore.strength)
