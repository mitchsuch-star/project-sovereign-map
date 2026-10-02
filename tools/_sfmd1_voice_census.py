"""SF-MD-1 "Every man his own voice" — the repeat census (October 2, 2026).

Drives the commanded 40-turn arm through the playtest driver, then reads
every battle record's `voice` (the player's commander) and `enemy_voice`
(the enemy's) off the run's jsonl and asks: does any man say the same line
twice within five of his own battles?

    python3 tools/_sfmd1_voice_census.py [--turns 40] [--out DIR]

Prints one line per speaker (battles, distinct lines, repeats-in-five) and
`CENSUS=` with the totals; exit 1 when any repeat is found.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT / "tools" / "playtest_driver.py"
SCRIPT = ROOT / "tools" / "playtest_scripts" / "commanded_full40.json"


def _speaker(line: str) -> str:
    return line.split(": ", 1)[0] if ": " in line else line


def census(jsonl: Path, window: int = 5):
    per = defaultdict(list)
    for raw in jsonl.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(raw)
        except ValueError:
            continue
        if rec.get("kind") != "battle":
            continue
        for key in ("voice", "enemy_voice"):
            line = rec.get(key)
            if line:
                per[_speaker(line)].append(line)
    report = {}
    repeats_total = 0
    for name, lines in sorted(per.items()):
        repeats = 0
        for i in range(len(lines)):
            frame = lines[max(0, i - window + 1): i + 1]
            if len(frame) != len(set(frame)):
                repeats += 1
        repeats_total += repeats
        report[name] = {"battles": len(lines), "distinct": len(set(lines)),
                        "repeats_in_five": repeats}
    return report, repeats_total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--out", default=str(ROOT / "tools" / "playtest_runs"))
    ap.add_argument("--name", default="sfmd1-voice-census")
    ap.add_argument("--jsonl", default="", help="census an existing run's jsonl instead")
    args = ap.parse_args()
    if args.jsonl:
        jsonl = Path(args.jsonl)
    else:
        env = dict(os.environ, PYTHONHASHSEED="0", LLM_MODE="mock",
                   SOVEREIGN_SEED="historical")
        env.pop("SOVEREIGN_SCENARIO", None)
        env.pop("SOVEREIGN_MAP", None)
        cmd = [sys.executable, str(DRIVER), "--script", str(SCRIPT), "--turns",
               str(args.turns), "--name", args.name, "--out", args.out, "--fresh"]
        proc = subprocess.run(cmd, env=env, cwd=str(ROOT), capture_output=True, text=True)
        if proc.returncode != 0:
            print(proc.stdout[-2000:])
            print(proc.stderr[-3000:])
            return 2
        run_dir = Path(args.out) / args.name
        candidates = sorted(run_dir.rglob("*.jsonl"))
        if not candidates:
            print(f"no jsonl under {run_dir}")
            return 2
        jsonl = candidates[-1]
    report, repeats = census(jsonl)
    for name, row in report.items():
        print(f"{name:22s} battles={row['battles']:3d} distinct={row['distinct']:3d} "
              f"repeats_in_five={row['repeats_in_five']}")
    print("CENSUS=" + json.dumps({"jsonl": str(jsonl), "speakers": len(report),
                                  "battles": sum(r["battles"] for r in report.values()),
                                  "repeats_in_five": repeats}))
    return 1 if repeats else 0


if __name__ == "__main__":
    raise SystemExit(main())
