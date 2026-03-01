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
