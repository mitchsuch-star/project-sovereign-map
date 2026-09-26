"""Write and read the build stamp (PB-4, the release build, Sept 25, 2026).

ONE stamp, two files, both derived from git at build time:

- ``deploy/build_stamp.json`` — ``{"version", "commit", "date", "dirty"}``.
  ``deploy/ink_iron.spec`` ships it inside the frozen server (PyInstaller's
  ``_MEIPASS``), where ``backend/build_info.py`` reads it; ``GET /test``
  reports it and the main menu and pause menu print it.
- ``<dist>/build_stamp.txt`` — the bare version string, beside launch.bat,
  which refuses to reuse a server on port 8005 whose ``/test`` version is
  not this one (a stale zip or a developer's source server would play a
  different game under this client).

    python tools/build_stamp.py                      # write the json, print the version
    python tools/build_stamp.py --txt <dist folder>  # copy the json's version into <dist>/build_stamp.txt
    python tools/build_stamp.py --read               # print the json's version and write nothing

The version is ``<yyyymmdd>-<short sha>``, ``+dirty`` when the working tree
has uncommitted changes — so a bug report names the exact build, and a build
cut from an uncommitted tree says so. The json is generated, never committed
(see .gitignore).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STAMP_JSON = REPO_ROOT / "deploy" / "build_stamp.json"
STAMP_TXT_NAME = "build_stamp.txt"


def _git(*args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True,
                             text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def build_stamp(now: _dt.datetime | None = None) -> dict:
    """The stamp as a dict — pure apart from the git reads."""
    now = now or _dt.datetime.now(_dt.timezone.utc)
    commit = _git("rev-parse", "--short=10", "HEAD") or "nogit"
    dirty = bool(_git("status", "--porcelain", "--untracked-files=no"))
    version = f"{now:%Y%m%d}-{commit}" + ("+dirty" if dirty else "")
    return {
        "version": version,
        "commit": _git("rev-parse", "HEAD") or "",
        "date": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dirty": dirty,
    }


def write_json(stamp: dict | None = None, path: Path | None = None) -> dict:
    # The module attribute is read at CALL time (a default bound at import
    # would ignore a test's patched location).
    path = path or STAMP_JSON
    stamp = stamp or build_stamp()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stamp, indent=2) + "\n", encoding="utf-8")
    return stamp


def read_json(path: Path | None = None) -> dict:
    path = path or STAMP_JSON
    return json.loads(path.read_text(encoding="utf-8"))


def write_txt(dist: Path, version: str) -> Path:
    dist.mkdir(parents=True, exist_ok=True)
    target = dist / STAMP_TXT_NAME
    # No trailing newline: launch.bat reads it with `set /p`.
    target.write_text(version, encoding="ascii")
    return target


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--txt", type=Path, default=None, metavar="DIST",
                    help="copy the json's version into DIST/build_stamp.txt (writes no json)")
    ap.add_argument("--read", action="store_true",
                    help="print the json's version and write nothing")
    args = ap.parse_args(argv)
    if args.read or args.txt is not None:
        try:
            version = str(read_json().get("version") or "")
        except (OSError, ValueError):
            print(f"[ERROR] no build stamp at {STAMP_JSON} - run tools/build_stamp.py first")
            return 1
        if not version:
            print(f"[ERROR] {STAMP_JSON} carries no version")
            return 1
        if args.txt is not None:
            target = write_txt(args.txt, version)
            print(f"[INFO] build stamp {version} -> {target}")
        else:
            print(version)
        return 0
    stamp = write_json()
    print(stamp["version"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
