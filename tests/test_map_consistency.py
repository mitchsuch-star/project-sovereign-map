"""
Verify Godot map.gd region data matches backend region.py.

GDScript can't import Python, so this test catches drift between the two.
"""

import os
import re
import pytest

from backend.models.region import REGIONS_DATA


MAP_GD_PATH = os.path.join(
    os.path.dirname(__file__), "..",
    "godot-client", "project-sovereign", "scenes", "map.gd"
)


@pytest.fixture
def map_gd_content():
    """Read map.gd content once per test session."""
    with open(MAP_GD_PATH, encoding="utf-8") as f:
        return f.read()


def test_godot_region_positions_match_backend(map_gd_content):
    """All regions in REGIONS_DATA must appear in map.gd REGION_POSITIONS."""
    for region_name in REGIONS_DATA:
        assert f'"{region_name}"' in map_gd_content, (
            f"Region '{region_name}' missing from map.gd"
        )


def test_map_gd_has_no_hardcoded_connections(map_gd_content):
    """map.gd must NOT re-hardcode REGION_CONNECTIONS — adjacency comes from `/map_topology` (§3.2).

    Drift prevention: this must catch the obvious const name and sneakier
    renamed / inline adjacency tables such as `CONNECTIONS_BY_REGION = {
    "Paris": [...] }` or `connections["Paris"] = [...]`. See
    docs/SCALE_READINESS_PLAN.md §3.2.
    """
    region_names = "|".join(re.escape(name) for name in sorted(REGIONS_DATA))
    hardcoded_patterns = [
        r'const\s+REGION_CONNECTIONS\b',
        rf'"(?:{region_names})"\s*:\s*\[',
        rf'\[\s*"(?:{region_names})"\s*\]\s*=\s*\[',
    ]
    assert not re.search(
        "|".join(f"(?:{pattern})" for pattern in hardcoded_patterns),
        map_gd_content,
    ), (
        "map.gd re-introduced hardcoded adjacency data. "
        "Adjacency must come from backend /map_topology (§3.2). "
        "Update backend/models/region.py REGIONS_DATA instead."
    )


def test_no_extra_regions_in_godot(map_gd_content):
    """map.gd should not have regions absent from REGIONS_DATA."""
    positions_match = re.search(
        r'const REGION_POSITIONS\s*=\s*\{(.*?)\}',
        map_gd_content,
        re.DOTALL
    )
    assert positions_match, "Could not find REGION_POSITIONS in map.gd"
    positions_block = positions_match.group(1)

    gd_regions = set(re.findall(r'"(\w+)"', positions_block))
    backend_regions = set(REGIONS_DATA.keys())

    extra = gd_regions - backend_regions
    assert not extra, f"map.gd has regions not in region.py: {extra}"


# ════════════════════════════════════════════════════════════════════════════════
# ADJACENCY GRAPH INTEGRITY
# ════════════════════════════════════════════════════════════════════════════════


def test_adjacency_graph_is_connected():
    """All regions must be reachable from any starting region via adjacency."""
    start = next(iter(REGIONS_DATA))
    visited = set()
    queue = [start]
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        for neighbor in REGIONS_DATA[current]["adjacent"]:
            if neighbor not in visited:
                queue.append(neighbor)
    unreachable = set(REGIONS_DATA.keys()) - visited
    assert not unreachable, f"Regions not reachable from {start}: {unreachable}"


def test_adjacency_is_bilateral():
    """If A lists B as adjacent, B must also list A."""
    for name, data in REGIONS_DATA.items():
        for neighbor in data["adjacent"]:
            assert neighbor in REGIONS_DATA, f"{name} lists unknown region {neighbor}"
            assert name in REGIONS_DATA[neighbor]["adjacent"], (
                f"{name} lists {neighbor} as adjacent, but {neighbor} does not list {name}"
            )


def test_no_self_adjacency():
    """No region should list itself as adjacent."""
    for name, data in REGIONS_DATA.items():
        assert name not in data["adjacent"], f"{name} lists itself as adjacent"


def test_regions_adjacency_is_bidirectional():
    """Cross-cutting drift guard: iterates REGIONS_DATA and collects EVERY
    asymmetric adjacency edge (A lists B, B does not list A) in a single
    failure message instead of bailing on the first mismatch.

    Distinct from `test_adjacency_is_bilateral` (which asserts pair-by-pair):
    this variant reports the complete set so an author can triage a batch of
    edits in one pass. Following the audit contract, the test does NOT
    auto-fix REGIONS_DATA — it only reports the asymmetries so the user can
    decide which side is authoritative.
    """
    asymmetries: list[str] = []
    for name, data in REGIONS_DATA.items():
        for neighbor in data["adjacent"]:
            if neighbor not in REGIONS_DATA:
                asymmetries.append(
                    f"{name} -> {neighbor} (neighbor missing from REGIONS_DATA)"
                )
                continue
            if name not in REGIONS_DATA[neighbor]["adjacent"]:
                asymmetries.append(f"{name} -> {neighbor} but {neighbor} does NOT -> {name}")
    assert not asymmetries, (
        "REGIONS_DATA adjacency is not bidirectional. Asymmetric edges:\n  "
        + "\n  ".join(asymmetries)
    )
