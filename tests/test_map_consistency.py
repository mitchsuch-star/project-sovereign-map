"""
Map-contract consistency tests (Map Slice 5: migrated to Europe).

The game's map is the 126-province Europe world built from europe.json — the
SAME registry the Godot renderer reads — so the adjacency-graph integrity
checks below run against the Europe game map via `create_europe_regions()`.

The map.gd checks guard the 19-region placeholder renderer, which remains the
live frontend until the Slice 7 Godot cutover retires it (these checks retire
with it). GDScript can't import Python, so they catch drift between the two.
"""

import os
import re
import pytest

from backend.models.region import REGIONS_DATA, create_europe_regions


MAP_GD_PATH = os.path.join(
    os.path.dirname(__file__), "..",
    "godot-client", "project-sovereign", "scenes", "map.gd"
)


@pytest.fixture(scope="module")
def europe_regions():
    """The 126-province Europe game map (name-keyed Region objects)."""
    return create_europe_regions()


@pytest.fixture
def map_gd_content():
    """Read map.gd content once per test session."""
    with open(MAP_GD_PATH, encoding="utf-8") as f:
        return f.read()


# ════════════════════════════════════════════════════════════════════════════════
# ADJACENCY GRAPH INTEGRITY — the Europe game map (Map Slice 5)
# ════════════════════════════════════════════════════════════════════════════════


def test_europe_adjacency_graph_is_connected(europe_regions):
    """All 126 provinces must be reachable from any start via adjacency
    (the hand-authored sea links join the island components to the mainland)."""
    start = next(iter(europe_regions))
    visited = set()
    queue = [start]
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        for neighbor in europe_regions[current].adjacent_regions:
            if neighbor not in visited:
                queue.append(neighbor)
    unreachable = set(europe_regions.keys()) - visited
    assert not unreachable, f"Provinces not reachable from {start}: {unreachable}"


def test_europe_adjacency_is_bilateral(europe_regions):
    """If A lists B as adjacent, B must also list A."""
    for name, region in europe_regions.items():
        for neighbor in region.adjacent_regions:
            assert neighbor in europe_regions, f"{name} lists unknown province {neighbor}"
            assert name in europe_regions[neighbor].adjacent_regions, (
                f"{name} lists {neighbor} as adjacent, but {neighbor} does not list {name}"
            )


def test_europe_no_self_adjacency(europe_regions):
    """No province should list itself as adjacent."""
    for name, region in europe_regions.items():
        assert name not in region.adjacent_regions, f"{name} lists itself as adjacent"


def test_europe_no_duplicate_adjacency_entries(europe_regions):
    """Adjacency lists carry no repeated neighbours (Slice 2 de-dupe-on-save)."""
    for name, region in europe_regions.items():
        assert len(region.adjacent_regions) == len(set(region.adjacent_regions)), (
            f"{name} has duplicate adjacency entries"
        )


def test_europe_adjacency_is_bidirectional_batch_report(europe_regions):
    """Cross-cutting drift guard: collects EVERY asymmetric adjacency edge
    (A lists B, B does not list A) in a single failure message instead of
    bailing on the first mismatch, so an author can triage a batch of edits
    in one pass. Does NOT auto-fix — reports only.
    """
    asymmetries: list[str] = []
    for name, region in europe_regions.items():
        for neighbor in region.adjacent_regions:
            if neighbor not in europe_regions:
                asymmetries.append(
                    f"{name} -> {neighbor} (neighbor missing from the Europe map)"
                )
                continue
            if name not in europe_regions[neighbor].adjacent_regions:
                asymmetries.append(f"{name} -> {neighbor} but {neighbor} does NOT -> {name}")
    assert not asymmetries, (
        "Europe adjacency is not bidirectional. Asymmetric edges:\n  "
        + "\n  ".join(asymmetries)
    )


# ════════════════════════════════════════════════════════════════════════════════
# LEGACY PLACEHOLDER RENDERER GUARDS — retire with the Slice 7 Godot cutover
# ════════════════════════════════════════════════════════════════════════════════


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
