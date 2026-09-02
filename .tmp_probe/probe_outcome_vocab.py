import contextlib, io, sys
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
mack.location = "Frankfurt"; mack.strength = 20000
ex = CommandExecutor()
with contextlib.redirect_stdout(buf):
    res = ex.execute({"command": {"marshal": "Ney", "action": "attack",
                                  "target": "Mack", "_strategic_execution": True}},
                     {"world": w})
print("A) direct attack result keys:", sorted(k for k in res if k != "new_state"))
print("   'battle_result' in result:", "battle_result" in res)
print("   events[0] keys:", sorted(res["events"][0].keys())[:8])
print("   events[0]['outcome'] =", repr(res["events"][0].get("outcome")),
      "| victor =", repr(res["events"][0].get("victor")))
print("   success:", res.get("success"))

# B) drive _handle_combat_result with each real outcome word
proc = StrategicOrderProcessor(ex)
for outcome_word, victor in [("attacker_victory","Ney"),
                             ("attacker_tactical_victory","Ney"),
                             ("defender_victory","Mack"),
                             ("defender_tactical_victory","Mack"),
                             ("stalemate",""),
                             ("mutual_destruction","")]:
    m = w.get_marshal("Ney")
    m.strategic_order = StrategicOrder(command_type="MOVE_TO", target="Frankfurt",
        target_type="region", started_turn=0, original_command="x", issued_turn=-1,
        path=["Frankfurt"])
    m.pending_interrupt = None
    fake = {"success": True, "message": "battle",
            "events": [{"type": "battle", "outcome": outcome_word, "victor": victor}]}
    with contextlib.redirect_stdout(buf):
        row = proc._handle_combat_result(m, mack, fake, w, {"world": w})
    print(f"B) events outcome={outcome_word!r:32} -> report outcome={row.get('outcome')!r:12} "
          f"status={row.get('order_status')!r:16} attempts={m.strategic_order.combat_attempts if m.strategic_order else 'ORDER GONE'}")
    print("      msg:", (row.get("message") or "")[:110])
