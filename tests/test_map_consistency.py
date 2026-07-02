"""
Map-contract consistency tests (Map Slice 5: migrated to Europe).

The game's map is the 126-province Europe world built from europe.json — the
SAME registry the Godot renderer reads — so the adjacency-graph integrity
checks below run against the Europe game map via `create_europe_regions()`.

The legacy map.gd placeholder guards retired with the Slice 7 Godot cutover
(see the note at the bottom of this file).
"""

import pytest

from backend.models.region import create_europe_regions


@pytest.fixture(scope="module")
def europe_regions():
    """The 126-province Europe game map (name-keyed Region objects)."""
    return create_europe_regions()


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


# The legacy placeholder renderer guards that used to live here (map.gd
# REGION_POSITIONS vs REGIONS_DATA, no-hardcoded-connections, no-extra-regions)
# retired with the Slice 7 Godot cutover: map.gd is now the Europe game map
# (extends europe_map.gd — registry-anchored positions, no position table).
# Their successors are the map.gd source pins in tests/test_map_slice7_cutover.py.
