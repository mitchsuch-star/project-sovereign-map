"""Why a debased AI corps does not drill to heal — a read-only diagnosis of
the P4.9 rung (the AI drill fix, Sept 27, 2026). For every AI evaluation of a
marshal below HEAL_MORALE_BELOW it records which rung answered and, when the
heal rung was reached, the first gate that declined it (the nearest at-war
corps and its reach, for the threat gate).

    .venv/Scripts/python.exe tools/_ai_drill_diag.py [--arm commanded|sim] [--seed historical]
        [--lever NAME=0|1 ...]

Prints DIAG=<json>. Changes nothing in the game.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import random
import runpy
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
DRIVER = ROOT / "tools" / "playtest_driver.py"


def child(arm: str, levers: list) -> None:
    sys.path.insert(0, str(ROOT))
    os.chdir(ROOT)
    import backend.ai.enemy_ai as EA
    import backend.game_logic.combat as CB
    import backend.models.world_state as WS
    for spec in levers:
        name, _, value = spec.partition("=")
        mod = CB if hasattr(CB, name) and not hasattr(EA, name) else EA
        setattr(mod, name, bool(int(value)))

    heal_verdicts = {}   # (nation, marshal, turn) -> list of verdicts
    evals = []

    orig_heal = EA.EnemyAI._consider_heal_drill

    def verdict(self, marshal, nation, world, personality, current_region):
        from backend.commands.tactical_executor import drill_refusal
        from backend.game_logic.war_council import get_intent_frontier
        if not EA.AI_DRILLS_TO_HEAL:
            why = "lever"
        elif personality == "literal" and not EA.LITERALS_DRILL_TO_HEAL:
            why = "literal"
        elif int(marshal.morale) >= EA.HEAL_MORALE_BELOW:
            why = "morale"
        elif int(marshal.strength or 0) < EA.STUB_STRENGTH_FLOOR:
            why = "stub"
        elif self._corps_takes_no_ground(marshal):
            why = "no_ground"
        else:
            refused, short = drill_refusal(world, marshal, stance_gate=False)
            if refused:
                why = "refused:" + short
            else:
                threat = EA.drill_reach_threat(world, marshal)
                if threat is not None:
                    dist = world.get_distance(marshal.location, threat.location)
                    why = f"threat:{threat.nation}:{threat.name}@{dist}"
                elif current_region and self._supply_pressure_move(marshal, nation, world, current_region):
                    why = "supply"
                elif get_intent_frontier(world, nation):
                    why = "frontier"
                elif self._find_defensive_reinforcement_position(marshal, nation, world):
                    why = "p74"
                else:
                    why = "HEAL"
        key = (nation, marshal.name, int(world.current_turn))
        heal_verdicts.setdefault(key, []).append(why)
        return orig_heal(self, marshal, nation, world, personality, current_region)

    EA.EnemyAI._consider_heal_drill = verdict

    orig_eval = EA.EnemyAI._evaluate_marshal

    def evaluate(self, marshal, nation, world):
        morale = int(getattr(marshal, "morale", 100) or 0)
        action, prio = orig_eval(self, marshal, nation, world)
        if morale < EA.HEAL_MORALE_BELOW:
            evals.append({
                "turn": int(world.current_turn), "nation": nation, "marshal": marshal.name,
                "personality": EA.get_effective_ai_personality(marshal, world),
                "morale": morale, "strength": int(marshal.strength or 0),
                "location": marshal.location,
                "action": (action or {}).get("action") if isinstance(action, dict) else None,
                "priority": prio,
            })
        return action, prio

    EA.EnemyAI._evaluate_marshal = evaluate

    drills = []
    orig_apply = WS.WorldState._apply_drill_morale

    def apply(self, marshal):
        gain = orig_apply(self, marshal)
        drills.append({"turn": int(self.current_turn), "nation": marshal.nation,
                       "marshal": marshal.name, "gain": int(gain)})
        return gain

    WS.WorldState._apply_drill_morale = apply

    if arm == "sim":
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.turn_manager import TurnManager
        world = WS.WorldState.from_scenario(str(SCENARIO))
        executor = CommandExecutor()
        tm = TurnManager(world, executor=executor)
        game_state = {"world": world, "executor": executor}
        for turn in range(40):
            random.seed(10_000 + turn)
            tm.end_turn(game_state)
    else:
        out_dir = tempfile.mkdtemp(prefix="ai_drill_diag_")
        sys.argv = [str(DRIVER), "--name", "ai_drill_diag", "--turns", "40",
                    "--script", str(ROOT / "tools" / "playtest_scripts" / "commanded_full40.json"),
                    "--diplomacy", "accept", "--out", out_dir]
        try:
            runpy.run_path(str(DRIVER), run_name="__main__")
        except SystemExit:
            pass

    player = "France"
    first = {}
    for r in evals:
        if r["nation"] == player:
            continue
        first.setdefault((r["nation"], r["marshal"], r["turn"]), r)
    rows = []
    for key, r in sorted(first.items(), key=lambda kv: (kv[0][2], kv[0][0], kv[0][1])):
        v = heal_verdicts.get(key)
        r = dict(r)
        r["heal"] = v[0] if v else "not_reached"
        rows.append(r)
    reasons = collections.Counter()
    for r in rows:
        tag = r["heal"].split(":")[0] if not r["heal"].startswith("refused") else r["heal"]
        reasons[(r["personality"], tag if r["heal"] != "not_reached" else f"pre-empted:P{r['priority']}:{r['action']}")] += 1
    rep = {
        "debased_ai_marshal_turns": len(rows),
        "by_personality_reason": {f"{p}|{t}": c for (p, t), c in sorted(reasons.items(), key=lambda kv: -kv[1])},
        "rows": rows,
        "ai_drills_completed": [d for d in drills if d["nation"] != player],
    }
    print("DIAG=" + json.dumps(rep))


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        child(sys.argv[2], sys.argv[3:])
        return 0
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="commanded")
    ap.add_argument("--seed", default="historical")
    ap.add_argument("--lever", action="append", default=[])
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = args.seed
    env["LLM_MODE"] = "mock"
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(key, None)
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", args.arm, *args.lever]
    proc = subprocess.run(cmd, env=env, cwd=str(ROOT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=3600)
    lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("DIAG=")]
    if proc.returncode != 0 or not lines:
        raise SystemExit(f"failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    rep = json.loads(lines[-1][len("DIAG="):])
    print("debased AI marshal-turns:", rep["debased_ai_marshal_turns"])
    for k, v in rep["by_personality_reason"].items():
        print(f"   {v:4d}  {k}")
    print("AI drills completed:", rep["ai_drills_completed"])
    if args.out:
        Path(args.out).write_text(json.dumps(rep, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
