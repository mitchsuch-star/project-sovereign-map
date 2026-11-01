"""RE-3 "Affairs of State" — the reach re-measured on the live tree (ERR-3;
`docs/RECURRING_EVENTS_SPEC.md` §16 "RE-3", §12c, §14). The driver arms the
S14c sweep record is composed from, run with the moments' trace and the
affairs' dial, plus the two families RE-3 adds (the treaty road and the six
hand-played DD-B saves as `--from-save` starts):

    .venv/Scripts/python.exe tools/_affairs_measure.py run --out DIR [--jobs 3]
        [--families commanded,accept,reach_aar,saves] [--affair decline]
    .venv/Scripts/python.exe tools/_affairs_measure.py record --out DIR
        --sweep DIR --road DIR --road-accept DIR [--record tools/_s14c_sweep_final.json]

`run` writes DIR/<family>/arms/<ARM>/{meta.json, digest.md, …} — the layout
`tools/_s14c_sweep_record.py` reads (`arms/*/meta.json`, the trace in
`meta.moments_trace`). The commanded arms are `tools/score_run.py`'s own
(`ARMS[name]["argv"]`, the nine the pacing pin names), each with
`--moments-trace --affair decline` (the affairs answered on arrival); the
accept arms add `--moment accept --affair accept`; REACH-AAR is the treaty
road; the saves are the six hand-played boards (local, gitignored — a
machine without them records none). `record` composes the sweep record from
this directory and the sweep's and the road arms' (run by their own tools:
`tools/ai_v_sweep.py --all --out DIR`, `tools/_vp1_road_arms.py --out DIR
--driver-flags "--affair lapse"`, and again with `--driver-flags "--moment
accept --affair accept"` for Road I answered).

A 40-turn arm takes about half a minute; the whole run is minutes. Seeded
paths, not laws: every reach is reported per arm.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PY = str(ROOT / ".venv" / "Scripts" / "python.exe") if os.name == "nt" else sys.executable
DRIVER = ROOT / "tools" / "playtest_driver.py"
SCRIPTS = ROOT / "tools" / "playtest_scripts"
RUNS = ROOT / "tools" / "playtest_runs"

COMMANDED = ("FC", "OP", "DL", "CMD-H", "CMD-A", "CMD-M", "FLD", "LAW", "VOLTE")
ACCEPT = ("CMD-H", "CMD-A", "CMD-M")
# The six hand-played DD-B boards at turn 21 (`docs/RECURRING_EVENTS_SPEC.md`
# §1 "The hand-played boards"); `--turns 20` carries each to the Verdict's eve.
SAVES = {f"DDB-{day}-{road}": RUNS / f"dd_b_2026_10_{day}" / road / "saves" / "autosave.json"
         for day in ("24", "25") for road in ("conquest", "diplomacy", "sea")}
SAVE_TURNS = 20


def _score_arms() -> dict:
    import importlib.util
    spec = importlib.util.spec_from_file_location("_score_run", ROOT / "tools" / "score_run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ARMS


def _env(arms_dir: Path) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["LLM_MODE"] = "mock"
    env["INK_IRON_SAVE_DIR"] = str(arms_dir / "_saves")
    env["PYTHONIOENCODING"] = "utf-8"
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED",
                "PYTHONDONTWRITEBYTECODE"):
        env.pop(key, None)
    return env


def run_arm(arms_dir: Path, name: str, argv: list) -> dict:
    arms_dir.mkdir(parents=True, exist_ok=True)
    cmd = [PY, str(DRIVER), "--name", name, "--fresh", "--out", str(arms_dir), "--llm", "mock"] + list(argv)
    t0 = time.time()
    with (arms_dir / f"{name}.log").open("w", encoding="utf-8") as fh:
        proc = subprocess.run(cmd, cwd=str(ROOT), env=_env(arms_dir), stdout=fh,
                              stderr=subprocess.STDOUT, text=True)
    meta = arms_dir / name / "meta.json"
    status = ""
    if meta.exists():
        try:
            status = json.loads(meta.read_text(encoding="utf-8")).get("status", "")
        except Exception:
            status = "unreadable-meta"
    return {"arm": name, "exit": proc.returncode, "status": status,
            "seconds": round(time.time() - t0, 1), "cmd": cmd[2:]}


def plan(out: Path, families: list, affair: str) -> list:
    arms = _score_arms()
    jobs = []
    if "commanded" in families:
        for name in COMMANDED:
            jobs.append((out / "commanded" / "arms", name,
                         list(arms[name]["argv"]) + ["--moments-trace", "--affair", affair]))
    if "accept" in families:
        for name in ACCEPT:
            jobs.append((out / "accept" / "arms", f"{name}-ACCEPT",
                         list(arms[name]["argv"]) + ["--moments-trace", "--moment", "accept",
                                                     "--affair", "accept"]))
    if "reach_aar" in families:
        jobs.append((out / "reach_aar" / "arms", "REACH-AAR",
                     list(arms["REACH-AAR"]["argv"]) + ["--moments-trace", "--affair", affair]))
    if "saves" in families:
        for name, save in SAVES.items():
            if not save.exists():
                print(f"  ! {name}: {save} is not on this machine — skipped")
                continue
            jobs.append((out / "saves" / "arms", name,
                         ["--from-save", str(save), "--turns", str(SAVE_TURNS),
                          "--moments-trace", "--affair", affair]))
    return jobs


def cmd_run(args) -> int:
    out = Path(args.out).resolve()
    families = [f.strip() for f in args.families.split(",") if f.strip()]
    jobs = plan(out, families, args.affair)
    # the long arms first, so the pool's tail is short
    jobs.sort(key=lambda j: ("--turns" not in j[2] or int(j[2][j[2].index("--turns") + 1]) < 30, j[1]))
    record = {"started": time.strftime("%Y-%m-%dT%H:%M"), "jobs": args.jobs, "affair": args.affair,
              "arms": {}}
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = {pool.submit(run_arm, d, n, a): n for d, n, a in jobs}
        for fut in futures:
            res = fut.result()
            record["arms"][res["arm"]] = res
            print(f"  {res['arm']:<14} exit {res['exit']} status {res.get('status', '')!s:<16} {res['seconds']}s",
                  flush=True)
    (out / "run.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    bad = [n for n, r in record["arms"].items() if r["exit"] != 0]
    print(f"{len(record['arms'])} arms, {len(bad)} failed" + (f": {', '.join(bad)}" if bad else ""))
    return 1 if bad else 0


def cmd_record(args) -> int:
    out = Path(args.out).resolve()
    cmd = [PY, str(ROOT / "tools" / "_s14c_sweep_record.py"),
           "--sweep", args.sweep, "--commanded", str(out / "commanded"),
           "--accept", str(out / "accept"), "--road", args.road, "--road-accept", args.road_accept,
           "--reach-aar", str(out / "reach_aar"), "--saves", str(out / "saves")]
    if args.record:
        cmd += ["--out", args.record]
    print(" ".join(cmd[2:]))
    return subprocess.run(cmd, cwd=str(ROOT), env=_env(out)).returncode


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--out", required=True)
    r.add_argument("--jobs", type=int, default=3)
    r.add_argument("--families", default="commanded,accept,reach_aar,saves")
    r.add_argument("--affair", default="decline", choices=["decline", "lapse"],
                   help="the dial on the non-accept arms (the accept arms always accept)")
    c = sub.add_parser("record")
    c.add_argument("--out", required=True, help="this tool's `run --out`")
    c.add_argument("--sweep", required=True, help="`tools/ai_v_sweep.py --all --out DIR`")
    c.add_argument("--road", required=True, help="`tools/_vp1_road_arms.py --out DIR --driver-flags \"--affair lapse\"`")
    c.add_argument("--road-accept", required=True,
                   help="`tools/_vp1_road_arms.py --arms RH --out DIR --driver-flags \"--moment accept --affair accept\"`")
    c.add_argument("--record", default="")
    args = ap.parse_args()
    return cmd_run(args) if args.cmd == "run" else cmd_record(args)


if __name__ == "__main__":
    raise SystemExit(main())
