"""
Drift-prevention test for SCALE_READINESS_PLAN §3.3 (centralize nation colors).

`utils.gd` is the single source of truth for nation color literals. This
test catches files that redefine nation colors locally — a drift pattern
that historically left `map.gd`, `war_detail_popup.gd`, and
`war_status_panel.gd` with three near-identical copies.

Only files under `godot-client/project-sovereign/` are scanned. `utils.gd`
is the allowed location for nation color literals.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest


GODOT_ROOT = (
    Path(__file__).resolve().parent.parent
    / "godot-client"
    / "project-sovereign"
)

UTILS_PATH = GODOT_ROOT / "scripts" / "utils.gd"

# Nations that have authored color entries. Anything in this list found in
# a `Color(...)` literal outside utils.gd is treated as drift.
NATION_NAMES = [
    "France",
    "Britain",
    "Prussia",
    "Austria",
    "Saxony",
    "Russia",
    "Spain",
    "Neutral",
]

# Roles that map to nation colors via alternate naming (e.g. "enemy default"
# is a fallback for nation color lookups — same drift category).
NATION_ROLE_TOKENS = ["ENEMY_DEFAULT", "COLOR_FRANCE"]

# Regex matches "Nation": Color(...) pairs — the exact drift we're blocking.
NATION_COLOR_PAIR = re.compile(
    r'"(?P<nation>[A-Z][A-Za-z]+)"\s*:\s*Color\s*\(',
)


def _iter_gdscript_files():
    for path in GODOT_ROOT.rglob("*.gd"):
        if path.resolve() == UTILS_PATH.resolve():
            continue
        yield path


def test_utils_defines_expected_nations():
    """utils.gd NATION_COLORS must cover every authored nation in the scenario."""
    content = UTILS_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"const\s+NATION_COLORS\s*=\s*\{(?P<body>.*?)\}",
        content,
        re.DOTALL,
    )
    assert match, "utils.gd is missing the NATION_COLORS constant"
    body = match.group("body")

    from backend.models.region import NATION_CAPITALS

    missing = [n for n in NATION_CAPITALS if f'"{n}"' not in body]
    assert not missing, (
        f"utils.gd NATION_COLORS missing scenario nations: {missing}"
    )


def test_no_nation_color_dicts_outside_utils():
    """No .gd file outside utils.gd may define a nation → Color(...) mapping."""
    offenders: list[tuple[str, int, str]] = []

    for path in _iter_gdscript_files():
        text = path.read_text(encoding="utf-8")
        for match in NATION_COLOR_PAIR.finditer(text):
            nation = match.group("nation")
            if nation not in NATION_NAMES:
                continue
            line_no = text.count("\n", 0, match.start()) + 1
            offenders.append((str(path.relative_to(GODOT_ROOT)), line_no, nation))

    assert not offenders, (
        "Nation color literals found outside utils.gd — use Utils.NATION_COLORS "
        "instead (see SCALE_READINESS_PLAN §3.3):\n"
        + "\n".join(f"  {p}:{ln}  \"{n}\": Color(..." for p, ln, n in offenders)
    )


def test_no_duplicate_colorframe_constants():
    """Deprecated per-nation color constants must not reappear outside utils.gd."""
    offenders: list[tuple[str, int, str]] = []

    for path in _iter_gdscript_files():
        text = path.read_text(encoding="utf-8")
        for token in NATION_ROLE_TOKENS:
            pattern = re.compile(rf"\bconst\s+{re.escape(token)}\b")
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                offenders.append(
                    (str(path.relative_to(GODOT_ROOT)), line_no, token)
                )

    assert not offenders, (
        "Per-nation color constants must live in utils.gd (§3.3):\n"
        + "\n".join(f"  {p}:{ln}  const {t}" for p, ln, t in offenders)
    )
