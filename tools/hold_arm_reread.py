"""DD-0 S4 — re-read the HOLD arm alone (PRE_DEPLOY_PLAN.md §3.0 done-when:
"HOLD orders ≥ 17 of 20"), without a full `score_run` (which rewrites four
archive files and reads 112 items).

Drives the committed blind HOLD script (`tools/playtest_scripts/
score_hold_2026_10_05.json`, written blind October 5, 2026, never edited)
through `tools/playtest_driver.py` exactly as `score_run run` does (Mode A,
the mock parser, `--fresh`, 2 turns), then reads the digest with THE ONE
reader `tools/_score_probes.command_c3_hold_orders` — the same judge the
census uses — and prints the item's evidence line.

    .venv/Scripts/python.exe tools/hold_arm_reread.py [--out DIR] [--script PATH]

Exit code 0 always — a measurement; the done-when is read by a person.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

DEFAULT_SCRIPT = ROOT / "tools" / "playtest_scripts" / "score_hold_2026_10_05.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="run dir (default: a temp dir)")
    ap.add_argument("--script", default=str(DEFAULT_SCRIPT))
    ap.add_argument("--turns", type=int, default=2)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    run_dir = pathlib.Path(args.out) if args.out else pathlib.Path(tempfile.mkdtemp(prefix="hold_reread_"))
    arms_dir = run_dir / "arms"
    arms_dir.mkdir(parents=True, exist_ok=True)

    import score_run  # noqa: E402  (the runner's own driver call and Arm loader)
    py = score_run._python()
    cmd = [py, str(ROOT / "tools" / "playtest_driver.py"), "--name", "HOLD", "--fresh",
           "--out", str(arms_dir), "--llm", "mock", "--script", args.script,
           "--turns", str(args.turns)]
    env = score_run._env(arms_dir)
    env["LLM_MODE"] = "mock"
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        env.pop(key, None)
    log = arms_dir / "HOLD.log"
    with log.open("w", encoding="utf-8") as fh:
        proc = subprocess.run(cmd, cwd=str(ROOT), env=env, stdout=fh,
                              stderr=subprocess.STDOUT, text=True)
    print("driver exit", proc.returncode, "| run dir", run_dir)

    arms = score_run.load_arms(run_dir)
    script = json.loads(pathlib.Path(args.script).read_text(encoding="utf-8"))
    from _score_probes import command_c3_hold_orders
    res = command_c3_hold_orders(arms, {"hold_script": script, "run_dir": run_dir, "arms": arms})
    print(json.dumps(res, ensure_ascii=False, indent=1))
    # every order, one line each: the line, the reply's first words
    hold = arms.get("HOLD")
    if hold:
        cmds = {str(c.get("text", "")).strip().lower(): c for c in hold.kind("command")}
        for o in (script.get("hold") or {}).get("orders", []):
            c = cmds.get(o["line"].strip().lower())
            msg = str((c or {}).get("message", ""))[:110].replace("\n", " / ")
            print(f"   {o['line'][:60]!r:64} -> {msg!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
