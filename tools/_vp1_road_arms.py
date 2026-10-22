"""VP-1 "The Emperor's Designs", S14b part 3 (`docs/VP1_DESIGNS_SPEC.md` §9
Part 3) — the three road arms, each on the three benchmark seeds, through the
real driver (Mode A, mock parser), every seed reported with its reason
(seeded paths, not laws):

    VP1-RH  the Rhine           tools/playtest_scripts/sf_vp1_rh.json
    VP1-CS  the System          tools/playtest_scripts/sf_vp1_cs.json  (+ --decline-until-latch Britain)
    VP1-TH  the Crowns of Italy tools/playtest_scripts/sf_vp1_th.json

A child wrapper counts, per end turn, the designs' store and THE DECISIVE
PEACE's six conditions (`imperial_designs.decisive_peace_reading`) and the
turn the stamp lands, so a seed that never stamps names the condition that
stayed false. Read-only on the tree.

    python tools/_vp1_road_arms.py [--arms RH,CS,TH] [--seeds historical,austerlitz,marengo]
                                   [--jobs 3] [--out DIR] [--record tools/_vp1_road_arms_final.json]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "tools" / "playtest_scripts"
SEEDS = ("historical", "austerlitz", "marengo")
COMMON = ["--turns", "40", "--objection", "insist", "--diplomacy", "accept",
          "--declare-war", "proceed"]
ARMS = {
    "RH": {"script": "sf_vp1_rh.json", "road": "rhine",
           "argv": COMMON + ["--settlement", "decline", "--client-petition", "grant",
                             "--decline-from", "Austria"]},
    "CS": {"script": "sf_vp1_cs.json", "road": "system",
           "argv": COMMON + ["--decline-from", "Portugal,PapalStates,Naples,Austria,Russia",
                             "--decline-until-latch", "Britain"]},
    "TH": {"script": "sf_vp1_th.json", "road": "crowns",
           "argv": COMMON + ["--settlement", "decline", "--client-petition", "grant",
                             "--decline-from", "Austria,Naples"]},
}

CHILD = r"""
import json, os, runpy, sys
sys.path.insert(0, {root!r})
from backend.game_logic import imperial_designs as ID
OUT = {out!r}
_tick, _stamp = ID.tick, ID.stamp_decisive_peace
def _row(world, turn, extra):
    reading = ID.decisive_peace_reading(world)
    state = ID._state(world)
    row = {{"turn": int(turn), "road": state.get("road"),
           "fulfilled": dict(state.get("fulfilled") or {{}}),
           "terms": {{c: (t or {{}}).get("manner") for c, t in (state.get("terms") or {{}}).items()}},
           "ready": bool(reading.get("ready")), "conds": reading.get("conditions"),
           "court": reading.get("court"), "manner": reading.get("manner")}}
    row.update(extra)
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, default=str) + "\n")
def _counted_stamp(world, turn):
    rec = _stamp(world, turn)
    try:
        _row(world, turn, {{"stamped": rec is not None,
                           "cause_line": (rec or {{}}).get("cause_line", "")}})
    except Exception as exc:
        with open(OUT, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({{"turn": int(turn), "probe_error": repr(exc)}}) + "\n")
    return rec
ID.stamp_decisive_peace = _counted_stamp
sys.argv = [{driver!r}] + {argv!r}
runpy.run_path({driver!r}, run_name="__main__")
"""


def run_one(arm: str, seed: str, out: Path) -> dict:
    spec = ARMS[arm]
    name = f"VP1-{arm}-{seed}"
    probe = out / f"{name}.probe.jsonl"
    if probe.exists():
        probe.unlink()
    argv = ["--name", name, "--fresh", "--out", str(out / "arms"), "--llm", "mock",
            "--script", str(SCRIPTS / spec["script"]), "--seed", seed] + spec["argv"]
    child = CHILD.format(root=str(ROOT), out=str(probe),
                         driver=str(ROOT / "tools" / "playtest_driver.py"), argv=argv)
    env = dict(os.environ)
    env.update({"PYTHONHASHSEED": "0", "LLM_MODE": "mock",
                "INK_IRON_SAVE_DIR": str(out / "_saves" / name), "PYTHONIOENCODING": "utf-8"})
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED"):
        env.pop(key, None)
    (out / "arms").mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
        fh.write(child)
        path = fh.name
    try:
        with open(out / "arms" / f"{name}.log", "w", encoding="utf-8") as log:
            proc = subprocess.run([sys.executable, path], cwd=str(ROOT), env=env,
                                  stdout=log, stderr=subprocess.STDOUT, text=True)
    finally:
        os.unlink(path)
    rows = []
    if probe.exists():
        rows = [json.loads(line) for line in probe.read_text(encoding="utf-8").splitlines() if line.strip()]
    return summarise(arm, seed, rows, proc.returncode, out / "arms" / name / "digest.md")


def summarise(arm: str, seed: str, rows: list, code: int, digest: Path) -> dict:
    stamped = next((r for r in rows if r.get("stamped")), None)
    last = rows[-1] if rows else {}
    fell = ""
    if digest.exists():
        for line in digest.read_text(encoding="utf-8").splitlines():
            if "ENDING — THE FALL OF THE EMPIRE" in line:
                fell = line.strip("- ").strip()[:200]
                break
    if stamped:
        reason = f"stamped on turn {stamped['turn']}: {stamped.get('cause_line', '')}"
    else:
        failing = {}
        for r in rows:
            for k, v in (r.get("conds") or {}).items():
                if not v:
                    failing[k] = failing.get(k, 0) + 1
        worst = sorted(failing.items(), key=lambda kv: (-kv[1], kv[0]))
        reason = ("never stamped — the conditions false at the most end turns: "
                  + ", ".join(f"{k} ({n})" for k, n in worst[:4]))
        if fell:
            reason += f"; {fell}"
    return {"arm": f"VP1-{arm}", "seed": seed, "exit": int(code), "end_turns": len(rows),
            "stamped_turn": int(stamped["turn"]) if stamped else -1,
            "fulfilled": last.get("fulfilled") or {}, "terms": last.get("terms") or {},
            "reason": reason}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="RH,CS,TH")
    ap.add_argument("--seeds", default=",".join(SEEDS))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "tools" / "playtest_runs" / "vp1_road_arms"))
    ap.add_argument("--record", default="")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(a, s) for a in args.arms.split(",") if a for s in args.seeds.split(",") if s]
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = list(pool.map(lambda j: run_one(j[0], j[1], out), jobs))
    for r in results:
        print(f"{r['arm']:7s} {r['seed']:10s} stamped={r['stamped_turn']:>3}  {r['reason'][:200]}")
    if args.record:
        record = {"_part": "S14b part 3 — VP-1's road arms, per seed (seeded paths, not laws)",
                  "arms": {k: dict(v, script=f"tools/playtest_scripts/{v['script']}") for k, v in ARMS.items()},
                  "results": results,
                  "done_when": any(r["stamped_turn"] >= 0 for r in results)}
        Path(args.record).write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("wrote", args.record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
