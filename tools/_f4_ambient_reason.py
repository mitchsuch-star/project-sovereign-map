"""F4 — WHY the ambient 40-turn series is byte-identical under every lever.

Runs the same 40-turn ambient loop the BASELINE_SERIES pin runs (same seed,
same per-turn re-seed idiom), in a subprocess per arm, and reports what the
reward machinery DID on that board: every marshal's expectation steps, the
AI grant and rente actions taken (from the event log's dotation rows), the
grace clocks opened, and the collective petitions. If the old curve produced
grants that the new one does not (or vice versa) and the series still did not
move, the reason is that those grants never reached a threat-bearing decision
inside 40 turns — a fact about the harness, recorded rather than assumed.

    .venv/Scripts/python.exe tools/_f4_ambient_reason.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHILD = r"""
import json, random, sys, contextlib, io
sys.path.insert(0, r"{root}")
import backend.game_logic.dotation as D
import backend.game_logic.jealousy as J
D.EXPECTATION_RISES_ON_DEEDS = {R}
D.EXPECTATION_RISE_COOLDOWN_ACTIVE = {C}
J.THE_COLLECTIVE_PETITION_WAITS = {P}
D.THE_UNMET_BLOCK_WAITS = {U}
from backend.commands.executor import CommandExecutor
from backend.game_logic.turn_manager import TurnManager
from backend.models.world_state import WorldState
SC = r"{root}\godot-client\project-sovereign\assets\maps\europe_1805.json"
with contextlib.redirect_stdout(io.StringIO()):
    world = WorldState.from_scenario(SC)
    executor = CommandExecutor()
    tm = TurnManager(world, executor=executor)
    gs = {{"world": world, "executor": executor}}
    grants = []
    petitions = 0
    for turn in range(40):
        random.seed(10_000 + turn)
        tm.end_turn(gs)
        for ev in world.event_log[-80:]:
            t = str(ev.get("type", ""))
            if t in ("dotation_granted", "pension_granted", "estate_granted", "rente_granted") and ev.get("turn") == world.current_turn - 1:
                grants.append((int(ev.get("turn", -1)), ev.get("nation"), ev.get("marshal"), t))
    steps = {{}}
    for m in world.marshals.values():
        steps[m.name] = [m.nation, int(getattr(m, "expectation_steps", 0)), int(getattr(m, "battles_won", 0)), int(getattr(m, "pension", 0)), list(getattr(m, "dotation_regions", []))]
    types = {{}}
    for ev in world.event_log:
        t = str(ev.get("type", ""))
        if "dotation" in t or "pension" in t or "rente" in t or "fontainebleau" in t or "estate" in t:
            types[t] = types.get(t, 0) + 1
print("PAYLOAD=" + json.dumps({{"steps": steps, "grants": sorted(set(grants)), "types": types,
                              "fontainebleau_last_turn": getattr(world, "fontainebleau_last_turn", None),
                              "threat": int(world.threat_level)}}))
"""


def run(levers):
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    env.pop("SOVEREIGN_SCENARIO", None)
    env.pop("SOVEREIGN_MAP", None)
    env.pop("PYTHONIOENCODING", None)
    code = CHILD.format(root=str(ROOT), **levers)
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=900)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr[-3000:])
    line = [ln for ln in proc.stdout.splitlines() if ln.startswith("PAYLOAD=")][-1]
    return json.loads(line[len("PAYLOAD="):])


def main():
    arms = {"old curve (all down)": dict(R=False, C=False, P=False, U=False),
            "full tree": dict(R=True, C=True, P=True, U=True)}
    out = {}
    for name, levers in arms.items():
        p = run(levers)
        out[name] = p
        expecting = {k: v for k, v in p["steps"].items() if v[1] > 0}
        print(f"== {name}: threat end {p['threat']} | marshals with steps>0: {len(expecting)} | "
              f"event types: {p['types']} | fontainebleau_last_turn: {p['fontainebleau_last_turn']}")
        for k, v in sorted(expecting.items(), key=lambda kv: -kv[1][1])[:12]:
            print(f"   {k:14s} {v[0]:14s} steps={v[1]} wins={v[2]} pension={v[3]} estates={v[4]}")
        print("   grants:", p["grants"][:20])
    Path(ROOT / "tools" / "_f4_ambient_reason.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
