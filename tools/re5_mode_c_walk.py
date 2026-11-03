"""RE-5 the close — the Mode C walk's runner (`docs/RECURRING_EVENTS_SPEC.md`
§16 "RE-5", §16b; the record §26.1).

    .venv/Scripts/python.exe tools/re5_mode_c_walk.py --out <run> [--port 8007] [--godot PATH]
                                                      [--export docs/audits/re5_mode_c_2026_11_02]

Starts a sandboxed backend (`uxr3_action_probe.start_backend`: the port asked
for or the next free one, never 8005; `<run>/saves` as its save directory; the
mock parser; the historical seed), stages chapter B's crafted save into that
directory (`tools/re5_stage_saves.py`), runs the ONE engine with
`tools/re5_mode_c_walk.gd` (the real `main.tscn` against that backend, the
window parked off the desktop), stops the backend, and writes `<run>/run.json`
— the walk's `walk.json`, the engine's SCRIPT ERROR census, the durations.
`--export` copies the frames, `walk.json` and `run.json` to the audit folder.

Rails: never two engines (refused while any Godot runs); never while a
commit's hook runs; the player's 8005 is never touched.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
PROJECT = REPO / "godot-client" / "project-sovereign"
WALK = REPO / "tools" / "re5_mode_c_walk.gd"
STAGER = REPO / "tools" / "re5_stage_saves.py"
GODOT_DEFAULT = (r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
                 r"\Godot_v4.4.1-stable_win64.exe")
SAVE_FILE = "re5_withdrawal.json"
CHAPTER_A_FILE = "re5_chapter_a.json"
LAPSE_FILE = "re5_lapse.json"
OFFER_FILE = "re5_offer.json"
SCRIPT_ERROR_RX = re.compile(r"SCRIPT ERROR|Parse Error|Invalid call|Invalid access|Invalid get|"
                             r"Invalid set|Attempt to call|Nonexistent function", re.I)
ENGINE_ERROR_RX = re.compile(r"^\s*ERROR:", re.M)


def _godot_running() -> int:
    try:
        out = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=30,
                             stdin=subprocess.DEVNULL).stdout
    except Exception:
        return 0
    return sum(1 for line in out.splitlines() if "godot" in line.lower())


def _python() -> str:
    venv = REPO / ".venv" / "Scripts" / "python.exe"
    return str(venv) if venv.exists() else sys.executable


def main() -> int:
    # the summary prints the scenes' notes ("Read the letter ▸"); a redirected
    # stdout on Windows is cp1252 and would raise on them AFTER the walk ran
    # and BEFORE the export — the record is UTF-8, so is the summary
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--port", type=int, default=8007)
    ap.add_argument("--godot", default=os.environ.get("GODOT_BIN") or GODOT_DEFAULT)
    ap.add_argument("--export", default="")
    ap.add_argument("--timeout", type=int, default=1500)
    args = ap.parse_args()
    if not pathlib.Path(args.godot).is_file():
        raise SystemExit(f"no Godot at {args.godot}")
    n = _godot_running()
    if n:
        raise SystemExit(f"refused: {n} Godot process(es) already running — never two engines at once")
    run = pathlib.Path(args.out).resolve()
    frames = run / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    from tools.uxr3_action_probe import start_backend
    t0 = time.time()
    backend, port = start_backend(run, args.port)
    result = {"port": port, "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    try:
        # the two crafted saves, into the sandbox's own save directory:
        # chapter A (the live board at turn 6, the standing held) and
        # chapter B (the Host's letter standing before the Match)
        stage_env = {**os.environ, "PYTHONHASHSEED": "0", "LLM_MODE": "mock", "SOVEREIGN_SEED": "historical"}
        for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "PYTHONIOENCODING"):
            stage_env.pop(key, None)
        staged_ok = {}
        logs = []
        for chapter, name in (("a", CHAPTER_A_FILE), ("d", OFFER_FILE), ("c", LAPSE_FILE), ("b", SAVE_FILE)):
            staged = subprocess.run([_python(), str(STAGER), "--chapter", chapter, "--out", str(run / "saves" / name)],
                                    cwd=str(REPO), capture_output=True, text=True, encoding="utf-8",
                                    errors="replace", timeout=900, env=stage_env)
            staged_ok[chapter] = staged.returncode == 0
            logs.append(f"=== chapter {chapter} ({name}) exit {staged.returncode} ===\n{staged.stdout}\n{staged.stderr}")
        (run / "stage.log").write_text("\n".join(logs), encoding="utf-8")
        result["staged"] = staged_ok
        env = dict(os.environ)
        env.pop("PYTHONIOENCODING", None)
        env.update({"SOVEREIGN_PORT": str(port), "RE5_WALK_OUT": str(frames),
                    "RE5_CHAPTER_A_SAVE": CHAPTER_A_FILE if staged_ok.get("a") else "",
                    "RE5_WITHDRAWAL_SAVE": SAVE_FILE if staged_ok.get("b") else "",
                    "RE5_LAPSE_SAVE": LAPSE_FILE if staged_ok.get("c") else "",
                    "RE5_OFFER_SAVE": OFFER_FILE if staged_ok.get("d") else ""})
        argv = [args.godot, "--audio-driver", "Dummy", "--windowed", "--resolution", "1920x1080",
                "--path", str(PROJECT), "--script", str(WALK)]
        t1 = time.time()
        with (run / "godot.log").open("w", encoding="utf-8") as log:
            proc = subprocess.run(argv, cwd=str(PROJECT), env=env, stdout=log, stderr=subprocess.STDOUT,
                                  stdin=subprocess.DEVNULL, timeout=args.timeout)
        result["engine_exit"] = proc.returncode
        result["engine_s"] = round(time.time() - t1, 1)
    finally:
        backend.terminate()
        try:
            backend.wait(timeout=20)
        except Exception:
            backend.kill()
    log_text = (run / "godot.log").read_text(encoding="utf-8", errors="replace")
    result["script_errors"] = [ln.strip() for ln in log_text.splitlines() if SCRIPT_ERROR_RX.search(ln)]
    result["engine_errors"] = len(ENGINE_ERROR_RX.findall(log_text))
    walk_path = frames / "walk.json"
    result["walk"] = json.loads(walk_path.read_text(encoding="utf-8")) if walk_path.is_file() else None
    result["total_s"] = round(time.time() - t0, 1)
    (run / "run.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    walk = result["walk"] or {}
    print(f"engine exit {result.get('engine_exit')} in {result.get('engine_s')} s; "
          f"steps {len(walk.get('steps', []))}; errors {len(walk.get('errors', []))}; "
          f"script errors {len(result['script_errors'])}; final turn {walk.get('final_turn')}")
    for step in walk.get("steps", []):
        print(f"  T{step.get('turn'):>3} {step.get('step'):16s} {step.get('frame')}  {step.get('note')}")
    for err in walk.get("errors", []):
        print("  ERROR", err)
    if args.export:
        dest = pathlib.Path(args.export)
        (dest / "frames").mkdir(parents=True, exist_ok=True)
        for f in sorted(frames.glob("*.jpg")):
            shutil.copyfile(f, dest / "frames" / f.name)
        if walk_path.is_file():
            shutil.copyfile(walk_path, dest / "walk.json")
        shutil.copyfile(run / "run.json", dest / "run.json")
        print("exported ->", dest)
    return 0 if result.get("engine_exit") == 0 and not result["script_errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
