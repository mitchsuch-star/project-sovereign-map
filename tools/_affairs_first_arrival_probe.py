"""RE-1 (`docs/RECURRING_EVENTS_SPEC.md` §0b P8, §17b "the first affair about
T13 — UNVERIFIED until RE-1") — the look-ahead and the first arrival, measured
on the ten `SWEEP_SEEDS`.

Each seed boots the shipped 1805 campaign twice in a child process — the
CONTROL (the deck unarmed, as shipped) and the ARMED arm (the staged fixture
`tests/fixtures/affairs_block.json`'s `affairs` deck grafted onto the booted
block; the moments as shipped) — and plays the passive board
(`random.seed(10_000 + turn)` before each end turn, the series harness's own
loop) to turn TURNS with the moments' trace installed. Per seed the record
carries the moments' arrival turns on both arms (they must be identical — §7:
the moments are blind to affairs), the first affair delivered and its morning,
every occurrence row at the end, and the trace's verdict.

    .venv/Scripts/python.exe tools/_affairs_first_arrival_probe.py [--turns 20] [--jobs 4]

Writes tools/_affairs_first_arrival.json (committed; read by
tests/test_affairs_pacing.py). Seeded paths, not laws.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
FIXTURE = ROOT / "tests" / "fixtures" / "affairs_block.json"
OUT = ROOT / "tools" / "_affairs_first_arrival.json"
SWEEP_SEEDS = ["historical", "ulm", "austerlitz", "jena", "marengo",
               "eylau", "friedland", "wagram", "lodi", "rivoli"]

CHILD = r"""
import contextlib, copy, io, json, random, sys
from backend.commands.executor import CommandExecutor
from backend.game_logic import moments as MO
from backend.game_logic.turn_manager import TurnManager
from backend.models.world_state import WorldState
from tools._moments_trace import MomentsTrace
SEED, ARM, TURNS = {seed!r}, {arm!r}, {turns}
SCENARIO = r"{scenario}"
fixture = json.loads(open(r"{fixture}", encoding="utf-8").read())
with contextlib.redirect_stdout(io.StringIO()):
    world = WorldState.from_scenario(SCENARIO, seed=SEED)
    if ARM == "armed":
        world.moments["block"]["affairs"] = copy.deepcopy(fixture["affairs"])
    executor = CommandExecutor()
    tm = TurnManager(world, executor=executor)
    game_state = {{"world": world, "executor": executor}}
    trace = MomentsTrace(lambda: world).install()
    try:
        for turn in range(TURNS):
            random.seed(10_000 + turn)
            tm.end_turn(game_state)
    finally:
        trace.uninstall()
summary = trace.summary(world)
state = {{k: dict(v) for k, v in MO._state(world).items() if isinstance(v, dict)}}
moments = {{k: int(v.get("turn", 0)) for k, v in state.items() if "#" not in k and v.get("status") in ("fired", "answered", "lapsed")}}
affairs = {{k: {{"turn": int(v.get("turn", 0)), "status": str(v.get("status")), "reason": str(v.get("reason") or ""),
                "bind": v.get("bind"), "tier": v.get("tier")}} for k, v in state.items() if "#" in k}}
first = min(((v["turn"], k) for k, v in affairs.items() if v["status"] in ("fired", "answered", "lapsed", "withdrawn")), default=None)
runtime = dict(world.moments.get("affairs") or {{}})
runtime.pop("morning", None)
print("PROBE=" + json.dumps({{
    "seed": SEED, "arm": ARM, "last_turn": int(world.current_turn),
    "moments": moments, "affairs": affairs,
    "first_affair": {{"turn": first[0], "id": first[1]}} if first else None,
    "streaks": runtime.get("streaks") or {{}}, "due": runtime.get("due") or {{}},
    "judged": {{k: summary["judged"].get(k) for k in ("ceiling_breaches", "floor_breaches", "floors", "shown_equals_applied", "arrived", "passed")}},
    "errors": summary.get("errors") or [],
}}, default=str))
"""


def run_child(seed: str, arm: str, turns: int) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["LLM_MODE"] = "mock"
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SEED", "PYTHONIOENCODING",
              "PYTHONDONTWRITEBYTECODE"):
        env.pop(k, None)
    scenario = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
    code = CHILD.format(seed=seed, arm=arm, turns=int(turns), scenario=str(scenario), fixture=str(FIXTURE))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, timeout=3600)
    stdout = proc.stdout.decode("utf-8", errors="replace")
    if proc.returncode != 0:
        raise SystemExit(f"{seed}/{arm} failed:\n{stdout[-2000:]}\n"
                         f"{proc.stderr.decode('utf-8', errors='replace')[-3000:]}")
    line = [ln for ln in stdout.splitlines() if ln.startswith("PROBE=")][-1]
    return json.loads(line[len("PROBE="):])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=20)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--seeds", default=",".join(SWEEP_SEEDS))
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    seeds = [s.strip() for s in args.seeds.split(",") if s.strip()]
    jobs = [(seed, arm) for seed in seeds for arm in ("control", "armed")]
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = list(pool.map(lambda j: run_child(j[0], j[1], args.turns), jobs))
    from tools._s14c_sweep_record import deck_sha
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    record = {"_part": ("RE-1 — the look-ahead and the first arrival on the ten SWEEP_SEEDS, the "
                        "passive board to turn %d, the staged deck grafted on the shipped boot "
                        "(docs/RECURRING_EVENTS_SPEC.md §0b P8, §17b)" % args.turns),
              "turns": int(args.turns),
              # the staged deck's MECHANICAL identity (its display copy struck) — an
              # edit to the fixture's mechanics reds the pacing pins until re-measured
              "fixture_sha": deck_sha(fixture),
              "affairs": [e["id"] for e in fixture["affairs"]["deck"]],
              "seeds": {}}
    for (seed, arm), payload in zip(jobs, results):
        record["seeds"].setdefault(seed, {})[arm] = payload
    for seed, arms in record["seeds"].items():
        control, armed = arms["control"], arms["armed"]
        same = control["moments"] == armed["moments"]
        first = armed.get("first_affair")
        print(f"{seed:>11}: moments identical {str(same):5}  first affair "
              f"{(first or {}).get('id')} T{(first or {}).get('turn')}  rows {len(armed['affairs'])}"
              f"  breaches {len(armed['judged']['ceiling_breaches'])}/{len(armed['judged']['floor_breaches'])}",
              flush=True)
    Path(args.out).write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
