"""Row BA, BA-2 — the plan's loop pressed in the real client: the runner
(`docs/BATTLE_DIORAMA_SPEC.md` §15.12; November 15, 2026) — modeled on
tools/ui6_mode_c_walk.py.

    .venv/Scripts/python.exe tools/ba2_mode_c_walk.py --out <run> [--port 8006] [--godot PATH]
                                                      [--export docs/audits/ba2_mode_c_2026_11_15]

Starts a sandboxed backend (`uxr3_action_probe.start_backend`: the port asked
for or the next free one, never 8005; `<run>/saves` as its save directory; the
mock parser; the historical seed), runs the ONE engine with
`tools/ba2_mode_c_walk.gd` (the real `main.tscn` against that backend, the
window parked off the desktop), stops the backend, and writes `<run>/run.json`
— the walk's `walk.json`, the engine's SCRIPT ERROR census, the durations.
`--export` copies the frames, `walk.json` and `run.json` to the audit folder.

Rails: never two engines (refused while any Godot runs); the player's 8005 is
never touched. Exit 0 only when the engine ended cleanly, no script error was
logged and every step of the walk held.
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
WALK = REPO / "tools" / "ba2_mode_c_walk.gd"
GODOT_DEFAULT = (r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
                 r"\Godot_v4.4.1-stable_win64.exe")
EXPORT_DEFAULT = "docs/audits/ba2_mode_c_2026_11_15"
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


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--port", type=int, default=8006)
    ap.add_argument("--godot", default=os.environ.get("GODOT_BIN") or GODOT_DEFAULT)
    ap.add_argument("--export", default=EXPORT_DEFAULT)
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()
    if not pathlib.Path(args.godot).is_file():
        raise SystemExit(f"no Godot at {args.godot}")
    n = _godot_running()
    if n:
        raise SystemExit(f"refused: {n} Godot process(es) already running - never two engines at once")
    run = pathlib.Path(args.out).resolve()
    frames = run / "frames"
    if frames.is_dir():
        shutil.rmtree(frames)
    frames.mkdir(parents=True, exist_ok=True)
    from tools.uxr3_action_probe import start_backend
    t0 = time.time()
    backend, port = start_backend(run, args.port)
    result = {"port": port, "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    try:
        env = dict(os.environ)
        env.pop("PYTHONIOENCODING", None)
        env.update({"SOVEREIGN_PORT": str(port), "BA2_WALK_OUT": str(frames)})
        # the GUI build loses a redirected stdout, so the census reads the
        # engine's own log; ABSOLUTE, or the engine resolves it against the project
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
          f"results {len(walk.get('results', []))}; frames {len(walk.get('steps', []))}; "
          f"errors {len(walk.get('errors', []))}; script errors {len(result['script_errors'])}")
    for row in walk.get("results", []):
        print(f"  {'ok ' if row.get('ok') else 'BAD'} {row.get('step'):22s} {row.get('did')}\n"
              f"        -> {row.get('saw')}")
    for err in walk.get("errors", []):
        print("  ERROR", err)
    for line in result["script_errors"][:12]:
        print("  SCRIPT", line)
    passed = bool(result.get("engine_exit") == 0 and not result["script_errors"]
                  and result["engine_log_bytes"] > 0 and walk.get("results")
                  and not walk.get("errors"))
    if args.export and not passed:
        # a run that did not pass never replaces the record of record
        # (the review, November 15, 2026: BA2-X16); it stays in its run folder
        print("NOT exported — the run did not pass; the record stands as it was. Run folder:", run)
    elif args.export:
        dest = REPO / args.export if not pathlib.Path(args.export).is_absolute() else pathlib.Path(args.export)
        if (dest / "frames").is_dir():
            shutil.rmtree(dest / "frames")
        (dest / "frames").mkdir(parents=True, exist_ok=True)
        for f in sorted(frames.glob("*.jpg")):
            shutil.copyfile(f, dest / "frames" / f.name)
        if walk_path.is_file():
            shutil.copyfile(walk_path, dest / "walk.json")
        shutil.copyfile(run / "run.json", dest / "run.json")
        print("exported ->", dest)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
