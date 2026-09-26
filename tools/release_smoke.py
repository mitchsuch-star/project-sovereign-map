"""Boot the FROZEN server and prove it plays (PB-1's done-when, the release build).

The March 2026 pipeline never ran the exe it built, which is how a server
that died at import shipped. This starts ``ink_iron_server.exe`` from the
bundle on a spare port with a throw-away save folder, waits for ``GET /test``,
checks the build stamp it reports, starts a campaign, types two orders and
ends a turn — then kills it. Exit 1 on any failure, with the server's own log
tail printed, so build.bat stops before the zip.

    python tools/release_smoke.py --dist deploy/dist/ink_iron_server
    python tools/release_smoke.py --dist <bundle> --port 8099 --expect-version 20260925-abcdef0123

With ``--anthropic-key-from-env`` the smoke also runs ONE hard phrasing
through the live parser using ``ANTHROPIC_API_KEY`` from the environment
(the release row's live-key smoke; costs under a cent). Nothing else in
this script touches the network beyond loopback.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

SERVER_EXE = "ink_iron_server.exe"
LOG_NAME = "server.log"
TRANSCRIPT_NAME = "transcript.jsonl"
# The environment a tester's launcher does NOT set — stripped so the smoke
# cannot pass on the developer's .env (a real key, DEBUG_MODE, a scenario).
STRIPPED_ENV = ("ANTHROPIC_API_KEY", "LLM_MODE", "DEBUG_MODE", "SOVEREIGN_SCENARIO",
                "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED", "PYTHONPATH")
# The orders every build must take on a fresh boot (the README's first two).
SMOKE_ORDERS = ("status", "Ney, attack Mack")
LIVE_ORDER = "Davout, see to it that the Austrians regret Swabia"


def smoke_env(work: Path, port: int, live_key: str | None = None) -> dict:
    """The frozen server's environment: the developer's own stripped, the
    smoke's sandbox set. Pure — tested directly."""
    env = {k: v for k, v in os.environ.items() if k not in STRIPPED_ENV}
    env.update({
        "SOVEREIGN_PORT": str(port),
        "INK_IRON_SAVE_DIR": str(work / "saves"),
        "INK_IRON_LOG_DIR": str(work / "logs"),
        "LLM_MODE": "anthropic" if live_key else "mock",
    })
    if live_key:
        env["ANTHROPIC_API_KEY"] = live_key
    return env


def _get(url: str, timeout: float = 5.0) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as resp:  # loopback only
        return json.loads(resp.read().decode("utf-8"))


def _post(url: str, body: dict, timeout: float = 120.0) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wait_for(url: str, seconds: float, proc: subprocess.Popen) -> dict | None:
    """Poll ``url`` until it answers or ``proc`` exits; None on either failure."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            return None  # the server died
        try:
            return _get(url, timeout=2.0)
        except (urllib.error.URLError, OSError, ValueError):
            time.sleep(0.5)
    return None


def _tail(path: Path, lines: int = 40) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "(no server log was written)"
    return "\n".join(text[-lines:])


def run_smoke(dist: Path, port: int, expect_version: str | None,
              live_key: str | None = None, boot_seconds: float = 90.0) -> int:
    exe = dist / SERVER_EXE
    if not exe.exists():
        print(f"[ERROR] {exe} not found - was the PyInstaller step skipped?")
        return 1

    work = Path(tempfile.mkdtemp(prefix="ink_iron_smoke_"))
    env = smoke_env(work, port, live_key)
    base = f"http://127.0.0.1:{port}"
    log_path = work / "logs" / LOG_NAME

    print(f"[INFO] smoke: starting {exe.name} on port {port} (saves+logs under {work})")
    # cwd = a folder that is NOT the repo, so an import that only works
    # beside the source tree fails here, the way it would on a tester's PC.
    proc = subprocess.Popen([str(exe)], cwd=str(work), env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    rc = 1
    try:
        test = wait_for(f"{base}/test", boot_seconds, proc)
        if test is None:
            print(f"[ERROR] the frozen server did not answer /test within {boot_seconds:.0f}s"
                  + (" (it exited)" if proc.poll() is not None else ""))
            return 1
        version = str(test.get("version", ""))
        print(f"[INFO] /test answered: build {version!r}, turn {test.get('turn')}, "
              f"gold {test.get('gold')}, smarter_parsing={test.get('smarter_parsing')}")
        if expect_version and version != expect_version:
            print(f"[ERROR] the server reports build {version!r}; this build is {expect_version!r}")
            return 1
        if version in ("", "dev", "unknown"):
            print(f"[ERROR] the frozen server carries no build stamp (reports {version!r})")
            return 1

        new_game = _post(f"{base}/new_game", {})
        if not new_game.get("success"):
            print(f"[ERROR] /new_game refused: {new_game.get('message')}")
            return 1
        turn0 = int(_get(f"{base}/test").get("turn", 0))
        for order in SMOKE_ORDERS:
            reply = _post(f"{base}/command", {"command": order})
            if not reply.get("success", False):
                print(f"[ERROR] {order!r} was refused: {reply.get('message')}")
                return 1
            print(f"[INFO] {order!r} -> ok ({str(reply.get('message', ''))[:70]!r}...)")
        end = _post(f"{base}/command", {"command": "end turn"})
        if not end.get("success", False):
            print(f"[ERROR] 'end turn' was refused: {end.get('message')}")
            return 1
        turn1 = int(_get(f"{base}/test").get("turn", 0))
        if turn1 != turn0 + 1:
            print(f"[ERROR] the turn did not advance ({turn0} -> {turn1})")
            return 1
        print(f"[INFO] a turn was played: {turn0} -> {turn1}")

        if live_key:
            cfg = _get(f"{base}/config/llm")
            reply = _post(f"{base}/command", {"command": LIVE_ORDER})
            mode = reply.get("parse_mode")
            print(f"[INFO] live-key smoke: key_status={cfg.get('key_status')!r}, "
                  f"parse_mode={mode!r}, success={reply.get('success')}")
            after = _get(f"{base}/config/llm")
            if after.get("key_status") in ("rejected", "no_model"):
                print(f"[ERROR] the live parser rejected the key: {after.get('key_status_text')}")
                return 1
            if mode not in ("anthropic", "live"):
                print("[ERROR] the hard phrasing never reached the live parser "
                      f"(parse_mode={mode!r}); check the key and the network")
                return 1

        if not log_path.exists() or log_path.stat().st_size == 0:
            print(f"[ERROR] no server log was written at {log_path}")
            return 1
        if not (work / "logs" / TRANSCRIPT_NAME).exists():
            print(f"[ERROR] no {TRANSCRIPT_NAME} was written beside the log")
            return 1
        print(f"[OK] the frozen server boots, plays and logs (build {version})")
        rc = 0
        return rc
    finally:
        if proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
        if rc != 0:
            print("--- server log tail ---")
            print(_tail(log_path))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dist", type=Path, required=True)
    ap.add_argument("--port", type=int, default=8099)
    ap.add_argument("--expect-version", default=None)
    ap.add_argument("--boot-seconds", type=float, default=90.0)
    ap.add_argument("--anthropic-key-from-env", action="store_true",
                    help="also run one live parse with ANTHROPIC_API_KEY from the environment")
    args = ap.parse_args(argv)
    live_key = os.environ.get("ANTHROPIC_API_KEY", "") if args.anthropic_key_from_env else None
    if args.anthropic_key_from_env and not live_key:
        print("[ERROR] --anthropic-key-from-env given but ANTHROPIC_API_KEY is empty")
        return 1
    return run_smoke(args.dist, args.port, args.expect_version, live_key or None,
                     args.boot_seconds)


if __name__ == "__main__":
    sys.exit(main())
