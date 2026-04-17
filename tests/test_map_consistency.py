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


def test_godot_connections_match_backend_adjacency(map_gd_content):
    """Adjacency in map.gd REGION_CONNECTIONS must match region.py."""
    # Extract REGION_CONNECTIONS block from GDScript
    connections_match = re.search(
        r'const REGION_CONNECTIONS\s*=\s*\{(.*?)\}',
        map_gd_content,
        re.DOTALL
    )
    assert connections_match, "Could not find REGION_CONNECTIONS in map.gd"
    connections_block = connections_match.group(1)

    # Parse each region's adjacency list from GDScript
    gd_adjacency = {}
    for match in re.finditer(r'"(\w+)":\s*\[(.*?)\]', connections_block):
        region_name = match.group(1)
        neighbors_str = match.group(2)
        neighbors = [n.strip().strip('"') for n in neighbors_str.split(",") if n.strip()]
        gd_adjacency[region_name] = sorted(neighbors)

    # Compare with backend REGIONS_DATA
    for name, data in REGIONS_DATA.items():
        backend_adj = sorted(data["adjacent"])
        gd_adj = sorted(gd_adjacency.get(name, []))
        assert backend_adj == gd_adj, (
            f"Adjacency mismatch for '{name}': "
            f"backend={backend_adj}, map.gd={gd_adj}"
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
