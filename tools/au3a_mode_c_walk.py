"""AU-3a the Mode C walk's runner (`docs/AUTHORITY_CURRENCY_SPEC.md` §5.3,
§5.5, §6.5), modeled on `tools/re5_mode_c_walk.py`.

    .venv/Scripts/python.exe tools/au3a_mode_c_walk.py --out <run> [--port 8007] [--godot PATH]
                                                       [--export docs/audits/au3a_mode_c_2026_11_05]

Starts a sandboxed backend (`uxr3_action_probe.start_backend`: the port asked
for or the next free one, never 8005; `<run>/saves` as its save directory; the
mock parser; the historical seed), stages the two crafted saves into that
directory (`tools/au3a_stage_saves.py`: the Remounts standing at authority 90;
the truce with Austria on its last turn, authority 88), runs the ONE engine with
`tools/au3a_mode_c_walk.gd` (the real `main.tscn` against that backend, the
window parked off the desktop), stops the backend, and writes `<run>/run.json`
- the walk's `walk.json`, the engine's SCRIPT ERROR census, the durations.
`--export` (default the audit folder; pass "" to skip) copies the frames,
`walk.json` and `run.json` there.

Rails: never two engines (refused while any Godot runs); the player's 8005 is
never touched.
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
WALK = REPO / "tools" / "au3a_mode_c_walk.gd"
STAGER = REPO / "tools" / "au3a_stage_saves.py"
GODOT_DEFAULT = (r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
                 r"\Godot_v4.4.1-stable_win64.exe")
EXPORT_DEFAULT = "docs/audits/au3a_mode_c_2026_11_05"
DECREE_FILE = "au3a_decree.json"
TEDEUM_FILE = "au3a_te_deum.json"
SCRIPT_ERROR_RX = re.compile(r"SCRIPT ERROR|Parse Error|Invalid call|Invalid access|Invalid get|"
                             r"Invalid set|Attempt to call|Nonexistent function", re.I)
ENGINE_ERROR_RX = re.compile(r"^\s*ERROR:", re.M)


def _godot_running() -> int:
    try:
        out = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=30,
                             stdin=subprocess.DEVNULL).stdout
    except Exception as exc:
        print(f"tasklist unreadable ({exc!r}); the one-engine rail cannot see a running Godot")
        return 0
    return sum(1 for line in out.splitlines() if "godot" in line.lower())


def _python() -> str:
    venv = REPO / ".venv" / "Scripts" / "python.exe"
    return str(venv) if venv.exists() else sys.executable


def main() -> int:
    # a redirected stdout on Windows is cp1252 and would raise on a note's
    # non-ASCII AFTER the walk ran and BEFORE the export
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--port", type=int, default=8007)
    ap.add_argument("--godot", default=os.environ.get("GODOT_BIN") or GODOT_DEFAULT)
    ap.add_argument("--export", default=EXPORT_DEFAULT)
    ap.add_argument("--timeout", type=int, default=1500)
    args = ap.parse_args()
    if not pathlib.Path(args.godot).is_file():
        raise SystemExit(f"no Godot at {args.godot}")
    n = _godot_running()
    if n:
        raise SystemExit(f"refused: {n} Godot process(es) already running - never two engines at once")
    run = pathlib.Path(args.out).resolve()
    frames = run / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    from tools.uxr3_action_probe import start_backend
    t0 = time.time()
    backend, port = start_backend(run, args.port)
    result = {"port": port, "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    try:
        # the two crafted saves, into the sandbox's own save directory:
        # chapter B (the Decree) and chapter D (the Te Deum)
        stage_env = {**os.environ, "PYTHONHASHSEED": "0", "LLM_MODE": "mock", "SOVEREIGN_SEED": "historical"}
        for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "PYTHONIOENCODING"):
            stage_env.pop(key, None)
        staged_ok = {}
        logs = []
        for chapter, name in (("b", DECREE_FILE), ("d", TEDEUM_FILE)):
            staged = subprocess.run([_python(), str(STAGER), "--chapter", chapter, "--out", str(run / "saves" / name)],
                                    cwd=str(REPO), capture_output=True, text=True, encoding="utf-8",
                                    errors="replace", timeout=900, env=stage_env)
            staged_ok[chapter] = staged.returncode == 0
            logs.append(f"=== chapter {chapter} ({name}) exit {staged.returncode} ===\n{staged.stdout}\n{staged.stderr}")
        (run / "stage.log").write_text("\n".join(logs), encoding="utf-8")
        result["staged"] = staged_ok
        env = dict(os.environ)
        env.pop("PYTHONIOENCODING", None)
        env.update({"SOVEREIGN_PORT": str(port), "AU3A_WALK_OUT": str(frames),
                    "AU3A_DECREE_SAVE": DECREE_FILE if staged_ok.get("b") else "",
                    "AU3A_TEDEUM_SAVE": TEDEUM_FILE if staged_ok.get("d") else ""})
        # the GUI build loses a redirected stdout, so the census reads the
        # engine's own log; ABSOLUTE, or the engine resolves it against the
        # project and dies at start (0xC0000005, November 5, 2026)
        argv = [args.godot, "--audio-driver", "Dummy", "--windowed", "--resolution", "1920x1080",
                "--log-file", str(run / "engine.log"),
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
        except Exception as exc:
            print(f"the backend did not stop ({exc!r}); killed")
            backend.kill()
    engine_log = run / "engine.log"
    log_text = engine_log.read_text(encoding="utf-8", errors="replace") if engine_log.is_file() else ""
    result["engine_log_bytes"] = len(log_text)
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
    # an empty engine log proves nothing: the census must have read the run
    return 0 if (result.get("engine_exit") == 0 and not result["script_errors"]
                 and result["engine_log_bytes"] > 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
