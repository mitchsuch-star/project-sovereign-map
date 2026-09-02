import contextlib, io, os, sys
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
assert M.parser.llm.use_real_api is False, "LIVE PARSER!"

hits = []
orig = EnemyAI._get_counter_punch_action
def wrapped(self, marshal, nation, world):
    r = orig(self, marshal, nation, world)
    if r:
        tgt = world.marshals.get(r["target"])
        if tgt:
            field = sum(m.strength for m in world.marshals.values()
                        if m.location == tgt.location and m.nation == tgt.nation
                        and m.strength > 0)
            hits.append((world.current_turn, marshal.name, nation, marshal.strength,
                         r["target"], tgt.strength, tgt.location, field))
    return r
EnemyAI._get_counter_punch_action = wrapped

c = TestClient(M.app)
with contextlib.redirect_stdout(io.StringIO()):
    for i in range(20):
        c.post("/command", json={"command": "end turn"})

print(f"counter-punch decisions over 20 ambient turns: {len(hits)}")
bad = 0
for h in hits:
    turn, name, nation, s, tname, ts, tloc, field = h
    priced = s / ts if ts else 999
    real = s / field if field else 999
    flag = "  <-- PRICED ONE, FOUGHT THE FIELD" if field > ts * 1.2 else ""
    if real < 0.7:
        bad += 1
    print(f"  t{turn:>2} {nation:9s} {name:16s} {s:>6,} -> {tname:16s} "
          f"({ts:,} at {tloc}; field {field:,}) priced {priced:.2f} real {real:.2f}{flag}")
print(f"\ndecisions whose REAL ratio was below the CR-5 0.7 disaster floor: {bad}")
