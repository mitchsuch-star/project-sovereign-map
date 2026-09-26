"""Which build is this (PB-4, the release build, Sept 23 2026).

``deploy/build.bat`` writes ``build_stamp.json`` (date + commit) and
``ink_iron.spec`` ships it at the bundle root, so a player's bug report names
the exact build. ``/test`` reports it, the main menu prints it, and launch.bat
refuses to reuse a server whose stamp differs from the zip's own.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

STAMP_FILENAME = "build_stamp.json"
DEV_VERSION = "dev"


def build_version() -> str:
    """The stamped build version, ``"dev"`` from source, ``"unknown"`` if a
    frozen build lost its stamp."""
    if not getattr(sys, "frozen", False):
        return DEV_VERSION
    stamp = Path(getattr(sys, "_MEIPASS", ".")) / STAMP_FILENAME
    try:
        return str(json.loads(stamp.read_text(encoding="utf-8")).get("version") or "unknown")
    except (OSError, ValueError):
        return "unknown"
