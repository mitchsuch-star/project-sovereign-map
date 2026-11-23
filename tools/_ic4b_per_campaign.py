"""Row IC, Session 4b — R-INITIATIVE per man and per campaign, from a measure
dump (`tools/_ic4b_measure.py --dump`): the plan's "report per man and per
campaign" when a bar is missed after the two rounds of weights.

    .venv/Scripts/python.exe tools/_ic4b_per_campaign.py DUMP.json [--out FILE]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import _ic4b_measure as MEAS  # noqa: E402


def per_campaign(runs: list) -> dict:
    out = {"by_seed": {}, "by_man": {}}
    for run in runs:
        seed = run["seed"]
        row = {}
        for snap in run["turns"]:
            rows = {r["marshal"]: r for r in snap["rows"] if not r.get("follows")}
            for name, info in snap["men"].items():
                r = rows.get(name)
                if r is None or name not in MEAS.MEN:
                    continue
                act = str(r.get("act") or "")
                if act in ("start", "asks") or r.get("action") in ("own_done", "own_ended"):
                    continue
                ch = info.get("chances") or {}
                if not (ch.get("attack") or ch.get("take") or ch.get("friend")) or info.get("goal_aim"):
                    continue
                if info.get("task") == "free":
                    continue
                took = MEAS._took(info, r, rows)
                cell = row.setdefault(name, [0, 0, info.get("task")])
                cell[0] += 1
                cell[1] += 1 if took else 0
                man = out["by_man"].setdefault(name, {"turns": 0, "taken": 0, "by_task": {}})
                man["turns"] += 1
                man["taken"] += 1 if took else 0
                t = man["by_task"].setdefault(str(info.get("task")), [0, 0])
                t[0] += 1
                t[1] += 1 if took else 0
        out["by_seed"][seed] = {n: {"chance_turns": c[0], "taken": c[1], "task": c[2]} for n, c in row.items()}
    for name, man in out["by_man"].items():
        man["share"] = round(man["taken"] / man["turns"], 3) if man["turns"] else None
        man["by_task"] = {k: {"turns": v[0], "taken": v[1], "share": round(v[1] / v[0], 3) if v[0] else None}
                          for k, v in man["by_task"].items()}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dump")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    runs = json.loads(pathlib.Path(args.dump).read_text(encoding="utf-8"))
    result = per_campaign(runs)
    text = json.dumps(result, indent=1)
    if args.out:
        pathlib.Path(args.out).write_text(text, encoding="utf-8")
    for name, man in result["by_man"].items():
        print(name, man["turns"], man["taken"], man["share"], man["by_task"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
