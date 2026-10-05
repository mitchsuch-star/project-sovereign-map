#!/usr/bin/env python
"""The driven client session — UI/UX C6's delegate evidence (economy gate,
October 5, 2026; `docs/SCORE_FINISH_SPEC.md` §6.8).

Starts a backend on an UNUSED port with its own save directory (never the
player's 8005, never the real `saves/` — the Mode B rule in
`docs/PLAYTESTING.md`), runs `tools/mode_c_driven_session.gd` headless against
it (the real `main.tscn`, the real APIClient, every advertised key pushed into
the viewport as an engine event, N turns played through four roads), stops
the backend, and writes `<out>/modec.json` plus the two logs.

    .venv/Scripts/python.exe tools/mode_c_driven_session.py \
        --godot "C:\\...\\Godot_v4.4.1-stable_win64.exe" --out <dir> [--turns 5]

No operating-system input is sent and no window is opened, so it is safe
beside a running game. What it cannot see is in the result's `cannot_see`.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import socket
import subprocess
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT = ROOT / "godot-client" / "project-sovereign"
SCRIPT = ROOT / "tools" / "mode_c_driven_session.gd"
DEFAULT_PORT = 8023


def _free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def _python() -> str:
    venv = ROOT / ".venv" / "Scripts" / "python.exe"
    return str(venv) if venv.exists() else sys.executable


def run(godot: str, out: pathlib.Path, turns: int = 5, port: int = DEFAULT_PORT) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    while not _free(port):
        port += 1
    saves = out / "saves"
    saves.mkdir(exist_ok=True)
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    env.update({
        "SOVEREIGN_PORT": str(port),
        "INK_IRON_SAVE_DIR": str(saves),
        "LLM_MODE": "mock",
        "SOVEREIGN_SEED": "historical",
        "SOVEREIGN_SCENARIO": "",
        "SOVEREIGN_SMOKE_START": "",
        "SOVEREIGN_MAP": "europe",
        "DEBUG_MODE": "false",
        "PYTHONHASHSEED": "0",
    })
    result: dict = {"port": port}
    t0 = time.time()
    with (out / "backend.log").open("w", encoding="utf-8") as blog:
        backend = subprocess.Popen(
            [_python(), "-m", "backend.main"], cwd=str(ROOT), env=env,
            stdout=blog, stderr=subprocess.STDOUT,
        )
        try:
            up = False
            for _ in range(240):
                if backend.poll() is not None:
                    break
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{port}/test", timeout=2) as r:
                        if r.status == 200:
                            up = True
                            break
                except Exception:
                    time.sleep(0.5)
            result["backend_up"] = up
            if not up:
                result["error"] = "the backend did not answer /test"
                return result
            spec = out / "spec.json"
            target = out / "modec.json"
            if target.exists():
                target.unlink()
            spec.write_text(json.dumps({"out": str(target), "turns": turns}), encoding="utf-8")
            genv = dict(env)
            genv["MODEC_SPEC"] = str(spec)
            proc = subprocess.run(
                [godot, "--headless", "--path", str(PROJECT), "--script", str(SCRIPT)],
                cwd=str(ROOT), env=genv, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=900,
            )
            log = proc.stdout + proc.stderr
            (out / "godot.log").write_text(log, encoding="utf-8")
            result["godot_exit"] = proc.returncode
            result["script_errors"] = log.count("SCRIPT ERROR")
            if target.exists():
                result["session"] = json.loads(target.read_text(encoding="utf-8"))
            else:
                result["error"] = "the session wrote no result"
        finally:
            backend.terminate()
            try:
                backend.wait(timeout=20)
            except subprocess.TimeoutExpired:
                backend.kill()
    result["seconds"] = round(time.time() - t0, 1)
    return result


def summary(result: dict) -> str:
    s = result.get("session") or {}
    checks = s.get("checks") or []
    failed = s.get("failed_checks") or []
    lines = [
        f"port {result.get('port')} · godot exit {result.get('godot_exit')} · "
        f"SCRIPT ERROR {result.get('script_errors')} · {result.get('seconds')}s",
        f"checks {len(checks) - len(failed)} of {len(checks)} pass; "
        f"turns played {s.get('turns_played')}; blocked {s.get('blocked')}",
    ]
    for name in failed:
        lines.append(f"  FAIL {name}")
    if result.get("error") or s.get("error"):
        lines.append(f"  ERROR {result.get('error') or s.get('error')}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--godot", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--turns", type=int, default=5)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()
    out = pathlib.Path(args.out).resolve()
    result = run(args.godot, out, args.turns, args.port)
    (out / "result.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(summary(result))
    return 0 if result.get("session") else 1


if __name__ == "__main__":
    raise SystemExit(main())
