"""Row FR, Session FR-2 — find 12's measure: does a bombardment farm the war score?

`docs/WEAK_SPOT_FINDS_SPEC.md` §3, the rule AS AMENDED at FR-2's Plan Mode and
written before any run (the plan `sharded-forging-rose.md`, approved November 23,
2026):

    Seeds historical / austerlitz / marengo; forty turns; the commanded script
    (`commanded_full40.json`) with `--diplomacy accept`. Both arms commission
    Marmont on turn 1 (France starts 1805 with no gun commander).
      Arm A (guns silent): each turn Marmont marches one province toward the
        nearest enemy corps France can see; he never fires.
      Arm B (guns firing): the same, but when a seen enemy corps is within range
        he bombards the largest such corps twice instead of marching.
    It is a FARM if, on two of the three seeds, either:
      (a) arm B's battle points reach the cap (+15) in some war at least two
          turns before arm A's do in that war, or reach it where arm A's never do;
      (b) in arm B, the war score France earned per 1,000 of its own dead is more
          than twice as high from salvos as from won battles.
    If a farm: the smallest of three fixes that ends it by the same rule —
      F1 a salvo needs 5,000 dead (five times a battle's 1,000) before it writes
         a battle; F2 a salvo's battle scores 1 point, not 3; F3 a salvo's dead
         count but it writes no battle —
    chosen by re-scoring (a) and (b) from arm B's own record under each fix,
    then confirmed by re-running both arms with it.

The driver arm is `tools/playtest_driver.py --battery silent|fire
--trace-war-score` (in-process, Mode A). Run ALONE — no backend, test or deck
edit lands under the tree it reads while it runs (run it from a frozen copy).

    .venv/Scripts/python.exe tools/_fr2_farm_measure.py [--arms A,B] [--jobs 3]
        [--seam MODULE:NAME=EXPR ...] [--out tools/_fr2_farm_2026_11_23.json]
        [--tree <frozen copy>]

THIS PARENT RUNS PLAIN (never `-X utf8`): the children print cp1252.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
ME = "France"
SEEDS = ("historical", "austerlitz", "marengo")
ARMS = {"A": "silent", "B": "fire"}
CAP = 15
PER_WIN = 3
FIXES = {
    "F1": {"label": "a salvo needs 5,000 dead to write a battle", "floor": 5000, "score": PER_WIN},
    "F2": {"label": "a salvo's battle scores 1 point, not 3", "floor": 0, "score": 1},
    "F3": {"label": "a salvo's dead count but it writes no battle", "floor": None, "score": 0},
}


def _run(tree: pathlib.Path, run_dir: pathlib.Path, arm: str, seed: str, seams: list) -> dict:
    if str(tree) not in sys.path:
        sys.path.insert(0, str(tree))
    from tools import score_run as SR
    arms_dir = run_dir / arm
    arms_dir.mkdir(parents=True, exist_ok=True)
    name = f"{arm}-{seed}"
    argv = ["--script", str(tree / "tools" / "playtest_scripts" / "commanded_full40.json"),
            "--turns", "40", "--diplomacy", "accept", "--seed", seed,
            "--battery", ARMS[arm], "--trace-war-score"]
    for spec in seams:
        argv += ["--seam", spec]
    print(f"[fr2] {name} ...", flush=True)
    result = SR._run_driver(tree, arms_dir, name, argv)
    if result["exit"] != 0:
        raise SystemExit(f"[fr2] {name} failed: {result}")
    rows = [json.loads(line) for line in (arms_dir / name / "digest.jsonl")
            .read_text(encoding="utf-8").splitlines() if line.strip()]
    wars = [r for r in rows if r.get("kind") == "fr2_war"]
    salvos = [r for r in rows if r.get("kind") == "fr2_salvo"]
    ledgers = [r for r in rows if r.get("kind") == "ledger"]
    print(f"[fr2] {name} done in {result.get('seconds')} s", flush=True)
    return {"wars": wars, "salvos": salvos, "seconds": result.get("seconds"),
            "provinces": int(ledgers[-1]["provinces"]) if ledgers else None}


def _first_cap(wars: list) -> dict:
    """{nation: the first turn France's battle points read +CAP}."""
    out = {}
    for w in wars:
        for nation, parts in (w.get("wars") or {}).items():
            if int(parts.get("battles", 0)) >= CAP and nation not in out:
                out[nation] = int(w["turn"])
    return out


def _rows(wars: list) -> list:
    return [r for w in wars for r in (w.get("new_rows") or [])]


def _rate(points: int, dead: int) -> float:
    return points / (max(1, dead) / 1000.0)


def _b_reading(run_b: dict, fix: dict | None = None) -> dict:
    """(b): war score per 1,000 French dead, salvos against won battles, in arm B."""
    salvos = [s for s in run_b["salvos"] if s.get("fired", True)]
    rows = _rows(run_b["wars"])
    me_won = [r for r in rows if not r["salvo"] and r["winner"] == ME]
    salvo_dead = sum(int(s.get("fr_dead", 0)) for s in salvos)
    written = [s for s in salvos if s.get("row_written")]
    if fix is None:
        salvo_points = PER_WIN * len(written)
    elif fix["floor"] is None:
        salvo_points = 0
    else:
        salvo_points = fix["score"] * sum(
            1 for s in written if int(s.get("fr_dead", 0)) + int(s.get("en_dead", 0)) >= fix["floor"])
    battle_points = PER_WIN * len(me_won)
    battle_dead = sum(int(r["fr_dead"]) for r in me_won)
    salvo_rate, battle_rate = _rate(salvo_points, salvo_dead), _rate(battle_points, battle_dead)
    return {"salvos": len(salvos), "salvo_rows": len(written), "salvo_points": salvo_points,
            "salvo_fr_dead": salvo_dead, "battles_won": len(me_won), "battle_points": battle_points,
            "battle_fr_dead": battle_dead, "salvo_rate": round(salvo_rate, 2),
            "battle_rate": round(battle_rate, 2),
            "holds": salvo_points > 0 and salvo_rate > 2 * battle_rate}


def _rescored_caps(run_b: dict, fix: dict) -> dict:
    """Arm B's first-cap turns re-scored with France's salvo rows under `fix`
    (the decay and the ten-turn window as the game applies them)."""
    sys.path.insert(0, str(ROOT))
    from backend.game_logic.diplomacy import _decay_battle_score
    rows = _rows(run_b["wars"])
    # each salvo row inherits its salvo's dead (the floor reads them)
    out = {}
    for w in run_b["wars"]:
        turn = int(w["turn"])
        for nation in (w.get("wars") or {}):
            if nation in out:
                continue
            live = [r for r in rows if r["nation"] == nation and turn - int(r["turn"]) <= 10
                    and int(r["turn"]) <= turn]
            raw, kept = 0, []
            for r in live:
                if r["winner"] not in (ME, nation):
                    continue                    # the record scores neither side
                ours = r["winner"] == ME
                if r["salvo"]:
                    if fix["floor"] is None:
                        continue
                    if int(r["fr_dead"]) + int(r["en_dead"]) < fix["floor"]:
                        continue
                    pts = fix["score"]
                else:
                    pts = PER_WIN
                raw += pts if ours else -pts
                kept.append({"turn": int(r["turn"])})
            decayed = _decay_battle_score(int(raw), kept, turn) if kept else 0
            if int(max(-CAP, min(CAP, decayed))) >= CAP:
                out[nation] = turn
    return out


def _a_reading(caps_a: dict, caps_b: dict) -> dict:
    ahead = {n: {"A": caps_a.get(n), "B": t} for n, t in caps_b.items()
             if caps_a.get(n) is None or caps_a[n] - t >= 2}
    return {"caps_A": caps_a, "caps_B": caps_b, "ahead": ahead, "holds": bool(ahead)}


def score(runs: dict) -> dict:
    seeds = {}
    for seed in SEEDS:
        a, b = runs.get(("A", seed)), runs.get(("B", seed))
        if a is None or b is None:
            continue
        reading = {"a": _a_reading(_first_cap(a["wars"]), _first_cap(b["wars"])),
                   "b": _b_reading(b),
                   "provinces": {"A": a["provinces"], "B": b["provinces"]}}
        reading["farm"] = reading["a"]["holds"] or reading["b"]["holds"]
        fixes = {}
        for key, fix in FIXES.items():
            fa = _a_reading(_first_cap(a["wars"]), _rescored_caps(b, fix))
            fb = _b_reading(b, fix)
            fixes[key] = {"a": fa["holds"], "b": fb["holds"], "farm": fa["holds"] or fb["holds"],
                          "b_reading": fb, "caps_B": fa["caps_B"]}
        reading["fixes"] = fixes
        seeds[seed] = reading
    farm_seeds = [s for s, r in seeds.items() if r["farm"]]
    verdict = {"farm": len(farm_seeds) >= 2, "farm_seeds": farm_seeds}
    ends = {}
    for key in FIXES:
        still = [s for s, r in seeds.items() if r["fixes"][key]["farm"]]
        ends[key] = {"farm_seeds": still, "ends_it": len(still) < 2}
    verdict["fixes"] = ends
    verdict["smallest_fix"] = next((k for k in FIXES if ends[k]["ends_it"]), None)
    return {"seeds": seeds, "verdict": verdict}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="A,B")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--seam", action="append", default=[])
    ap.add_argument("--tree", default=str(ROOT))
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_fr2_farm_2026_11_23.json"))
    args = ap.parse_args()
    tree = pathlib.Path(args.tree).resolve()
    run_dir = tree / "tools" / "playtest_runs" / ("fr2_farm" + (f"_{args.tag}" if args.tag else ""))
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    jobs = [(arm, seed) for arm in arms for seed in SEEDS]
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = dict(zip(jobs, pool.map(lambda j: _run(tree, run_dir, j[0], j[1], args.seam), jobs)))
    record = {"_note": ("Row FR, Session FR-2 — find 12's measure (docs/WEAK_SPOT_FINDS_SPEC.md §3, "
                        "the rule as amended at FR-2's Plan Mode, written before any run): arm A the "
                        "guns silent, arm B the guns firing twice a turn, on the band's three seeds "
                        "over forty turns. Written by tools/_fr2_farm_measure.py."),
              "seams": args.seam, "tree": str(tree),
              "seconds": {f"{a}-{s}": r["seconds"] for (a, s), r in results.items()},
              **score(results)}
    pathlib.Path(args.out).write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(record["verdict"], indent=1))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
