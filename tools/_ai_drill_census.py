"""Why the enemy AI almost never drills — a read-only census (SR-5r RF-2 recon,
September 27, 2026; asked by the user: "evaluate why they never drill in ai
maybe its an issue?").

Drill has two purposes in this game:
  * the one-shot shock bonus (`marshal.shock_bonus`, consumed by the next
    attack) — the P6 rung's only reason to drill;
  * morale restoration (`WorldState._apply_drill_morale`, +10, +15 with a
    training ground — the Aug 4, 2026 econ slice "drill restores morale":
    morale never moves in peacetime otherwise, so a corps rebuilt with green
    conscripts stays debased until it drills).
The P6 rung (`EnemyAI._evaluate_marshal`) asks only aggressive marshals (or
any marshal under an aggressive coalition posture) and never reads morale.

This census plays the ambient board (the M7 sim: every court AI, a passive
France, the per-turn re-seed) and a commanded arm, wraps
`EnemyAI._evaluate_marshal` and records, for every AI marshal-turn: the
court, the marshal, his effective AI personality, his morale, whether the
drill rung's own safety test would pass (`_consider_drill` with the
personality gate lifted), and the decision the AI actually took.

    .venv/Scripts/python.exe tools/_ai_drill_census.py [--arms sim,commanded]

Writes tools/_ai_drill_census.json. Changes nothing in the game.
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
ARMS = {
    "sim": {"mode": "sim", "seed": "historical"},
    "commanded": {"mode": "driver", "seed": "historical",
                  "script": "commanded_full40.json"},
}
LOW = 70  # "debased": below a veteran corps' comfort


def child(mode: str, seed: str, script: str) -> None:
    sys.path.insert(0, str(ROOT))
    os.chdir(ROOT)
    import backend.ai.enemy_ai as EA
    import backend.models.world_state as WS

    rows = []
    drills_completed = collections.Counter()

    orig_eval = EA.EnemyAI._evaluate_marshal

    def evaluate(self, marshal, nation, world):
        action, prio = orig_eval(self, marshal, nation, world)
        try:
            personality = EA.get_effective_ai_personality(marshal, world)
        except Exception:
            personality = str(getattr(marshal, "personality", "?"))
        # The rung's own safety verdict with the personality gate lifted: the
        # same function, called directly (it reads no personality).
        try:
            safe = orig_consider(self, marshal, world) is not None
        except Exception:
            safe = False
        rows.append({
            "turn": int(getattr(world, "current_turn", 0) or 0),
            "nation": nation,
            "marshal": marshal.name,
            "personality": personality,
            "morale": int(getattr(marshal, "morale", 0) or 0),
            "strength": int(getattr(marshal, "strength", 0) or 0),
            "drill_safe": bool(safe),
            "action": (action or {}).get("action") if isinstance(action, dict) else None,
            "priority": prio,
        })
        return action, prio

    orig_consider = EA.EnemyAI._consider_drill
    EA.EnemyAI._evaluate_marshal = evaluate

    orig_drill = WS.WorldState._apply_drill_morale

    def drill(self, marshal):
        drills_completed[getattr(marshal, "nation", "?")] += 1
        return orig_drill(self, marshal)

    WS.WorldState._apply_drill_morale = drill

    if mode == "sim":
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.turn_manager import TurnManager
        world = WS.WorldState.from_scenario(str(SCENARIO))
        executor = CommandExecutor()
        tm = TurnManager(world, executor=executor)
        game_state = {"world": world, "executor": executor}
        for turn in range(40):
            random.seed(10_000 + turn)  # the M7 per-turn re-seed idiom
            tm.end_turn(game_state)
    else:
        out_dir = tempfile.mkdtemp(prefix="ai_drill_")
        sys.argv = [str(DRIVER), "--name", "ai_drill", "--turns", "40",
                    "--script", str(ROOT / "tools" / "playtest_scripts" / script),
                    "--diplomacy", "accept", "--out", out_dir]
        try:
            runpy.run_path(str(DRIVER), run_name="__main__")
        except SystemExit:
            pass

    player = "France"
    # The AI evaluates a marshal once per ACTION it takes in a turn, so the raw
    # rows count evaluations. One row per marshal-turn: his FIRST evaluation
    # (the state he woke to), with every action he took that turn attached.
    first, actions = {}, collections.defaultdict(list)
    for r in rows:
        key = (r["nation"], r["marshal"], r["turn"])
        first.setdefault(key, r)
        actions[key].append(r["action"])
    for key, r in first.items():
        r["action"] = "drill" if "drill" in actions[key] else (actions[key][0] if actions[key] else None)
    ai = [r for r in first.values() if r["nation"] != player]
    by_pers = collections.Counter(r["personality"] for r in ai)
    drill_orders = collections.Counter(
        (r["nation"], r["personality"]) for r in ai if r["action"] == "drill")
    low = [r for r in ai if r["morale"] < LOW]
    low_safe = [r for r in low if r["drill_safe"]]
    low_safe_by = collections.Counter((r["personality"], r["action"]) for r in low_safe)
    per_marshal_low = collections.defaultdict(list)
    for r in low:
        per_marshal_low[f"{r['nation']}:{r['marshal']}"].append(r["morale"])
    rep = {
        "ai_marshal_turns": len(ai),
        "by_personality": dict(by_pers),
        "drill_orders_by_nation_personality": {f"{n}|{p}": c for (n, p), c in sorted(drill_orders.items())},
        "drills_completed_by_nation": dict(drills_completed),
        "below_70_marshal_turns": len(low),
        "below_70_and_drill_safe": len(low_safe),
        "below_70_and_drill_safe_by_personality_action": {
            f"{p}|{a}": c for (p, a), c in sorted(low_safe_by.items(), key=lambda kv: -kv[1])},
        "longest_debased_marshals": sorted(
            ((k, len(v), min(v)) for k, v in per_marshal_low.items()),
            key=lambda t: -t[1])[:12],
        "mean_ai_morale_by_turn_bucket": {
            f"{b}-{b + 9}": round(sum(r["morale"] for r in ai if b <= r["turn"] <= b + 9)
                                   / max(1, sum(1 for r in ai if b <= r["turn"] <= b + 9)), 1)
            for b in (1, 11, 21, 31)},
    }
    print("CENSUS=" + json.dumps(rep))


def run_arm(name: str, spec: dict) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = spec["seed"]
    env["LLM_MODE"] = "mock"
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(key, None)
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child",
           spec["mode"], spec["seed"], spec.get("script", "")]
    proc = subprocess.run(cmd, env=env, cwd=str(ROOT), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=3600)
    lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("CENSUS=")]
    if proc.returncode != 0 or not lines:
        raise SystemExit(f"arm {name} failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    return json.loads(lines[-1][len("CENSUS="):])


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        child(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
        return 0
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="all")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_ai_drill_census.json"))
    args = ap.parse_args()
    wanted = list(ARMS) if args.arms == "all" else args.arms.split(",")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {name: pool.submit(run_arm, name, ARMS[name]) for name in wanted}
        results = {name: fut.result() for name, fut in futures.items()}
    for name in wanted:
        print(f"== {name}")
        for k, v in results[name].items():
            print(f"   {k}: {v}")
    Path(args.out).write_text(json.dumps({"arms": results}, indent=1), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
