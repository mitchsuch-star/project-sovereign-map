"""Tests for the Slice 1 adjacency deriver in build_region_key_from_psd.py.

Pins the pure ``derive_adjacency`` / ``apply_adjacency_to_registry`` contract on
tiny synthetic lookups, plus a guard that the shipped europe.json carries a
symmetric, validator-clean adjacency graph.

Plan reference: docs/MAP_IMPLEMENTATION_PLAN.md Slice 1.
"""
from __future__ import annotations

import json
from array import array
from pathlib import Path

import pytest

from tools import build_region_key_from_psd as brk
from tools import validate_province_map as vpm


REPO_ROOT = Path(__file__).resolve().parents[1]
EUROPE_REGISTRY = (
    REPO_ROOT
    / "godot-client"
    / "project-sovereign"
    / "assets"
    / "maps"
    / "europe.json"
)

# Province color-keys used across the synthetic grids. Any distinct positive
# ints work; 0 is the sentinel (no_province_color) for these fixtures.
A, B, C = 1, 2, 3
SENTINEL = 0


def _grid(rows: list[list[int]]) -> tuple[array, int, int]:
    """Flatten a 2D list of color-keys into (flat array, width, height)."""
    height = len(rows)
    width = len(rows[0])
    flat = array("I")
    for row in rows:
        assert len(row) == width
        flat.extend(row)
    return flat, width, height


def _derive(rows, **kw):
    flat, w, h = _grid(rows)
    return brk.derive_adjacency(flat, w, h, {A, B, C}, SENTINEL, **kw)


# ---------------------------------------------------------------------------
# derive_adjacency: land / sea / dead-zone / isolation classification.
# ---------------------------------------------------------------------------


def test_thin_moat_is_a_land_edge():
    # A and B separated by a 1px sentinel moat (<= land_gap_max).
    land, sea = _derive([[A, A, SENTINEL, B, B]])
    assert land == {(A, B)}
    assert sea == {}


def test_directly_touching_is_a_land_edge():
    # No moat at all (gap 0) still counts as land-adjacent.
    land, sea = _derive([[A, A, B, B]])
    assert land == {(A, B)}
    assert sea == {}


def test_wide_gap_is_a_sea_candidate_not_land():
    # 50px sentinel gap sits in the sea window [41, 400].
    row = [A, A] + [SENTINEL] * 50 + [B, B]
    land, sea = _derive([row])
    assert land == set()
    assert sea == {(A, B): 50}


def test_dead_zone_gap_produces_no_edge():
    # A 20px gap is in the ignored 16-40px dead zone: neither land nor sea.
    row = [A, A] + [SENTINEL] * 20 + [B, B]
    land, sea = _derive([row])
    assert land == set()
    assert sea == {}


def test_gap_beyond_sea_window_is_ignored():
    # Farther than sea_gap_max: two provinces across the open ocean, no candidate.
    row = [A, A] + [SENTINEL] * 500 + [B, B]
    land, sea = _derive([row])
    assert land == set()
    assert sea == {}


def test_isolated_blob_has_no_edges():
    # A lone province in a sea of sentinel touches nobody.
    rows = [
        [SENTINEL, SENTINEL, SENTINEL, SENTINEL],
        [SENTINEL, A, A, SENTINEL],
        [SENTINEL, A, A, SENTINEL],
        [SENTINEL, SENTINEL, SENTINEL, SENTINEL],
    ]
    land, sea = _derive(rows)
    assert land == set()
    assert sea == {}


def test_intervening_province_blocks_a_direct_edge():
    # A | C | B in a row: A-C and B-C are edges; A-B is not (C is between them).
    # Pairs are normalized to (lo, hi), so C-B is stored as (B, C).
    land, _sea = _derive([[A, A, C, C, B, B]])
    assert land == {(A, C), (B, C)}
    assert (A, B) not in land


def test_vertical_adjacency_is_detected():
    # A stacked above B (column scan) with a 1px horizontal moat between them.
    rows = [
        [A, A],
        [SENTINEL, SENTINEL],
        [B, B],
    ]
    land, sea = _derive(rows)
    assert land == {(A, B)}


def test_land_on_one_axis_suppresses_a_sea_candidate_on_another():
    # A and B touch closely on the left column (land) but are far apart across
    # the sentinel on the top row. Land must win; no sea candidate survives.
    rows = [
        [A] + [SENTINEL] * 50 + [B],
        [A] + [SENTINEL] * 50 + [SENTINEL],
        [B] + [SENTINEL] * 50 + [SENTINEL],
    ]
    land, sea = _derive(rows)
    assert (A, B) in land
    assert sea == {}


def test_pairs_are_normalized_and_symmetric():
    # Whichever order the scan encounters them, the pair key is (lo, hi).
    land, _ = _derive([[B, B, SENTINEL, A, A]])
    assert land == {(A, B)}  # not (B, A)


def test_tunable_gap_thresholds_reclassify_edges():
    row = [A, A] + [SENTINEL] * 20 + [B, B]
    # Default: 20px is dead-zone -> nothing.
    assert _derive([row]) == (set(), {})
    # Widen land window to swallow it.
    land, sea = _derive([row], land_gap_max=25)
    assert land == {(A, B)} and sea == {}
    # Or open the sea window down to it.
    land, sea = _derive([row], sea_gap_min=10, sea_gap_max=30)
    assert land == set() and sea == {(A, B): 20}


# ---------------------------------------------------------------------------
# apply_adjacency_to_registry: registry write-back.
# ---------------------------------------------------------------------------


def _mini_registry():
    return {
        "no_province_color": [0, 0, 0],
        "regions": {
            "A": {"lookup_color": [0, 0, 1]},   # key 1
            "B": {"lookup_color": [0, 0, 2]},   # key 2
            "Island": {"lookup_color": [0, 0, 3]},  # key 3
        },
    }


def test_apply_writes_symmetric_adjacency_and_sea_candidates():
    registry = _mini_registry()
    # A-B share a thin moat; Island sits across a 50px sea gap from B.
    row = [1, 1, SENTINEL, 2, 2] + [SENTINEL] * 50 + [3, 3]
    flat, w, h = _grid([row])
    brk.apply_adjacency_to_registry(registry, flat, w, h)

    regs = registry["regions"]
    assert regs["A"]["adjacent"] == ["B"]
    assert regs["B"]["adjacent"] == ["A"]
    assert regs["Island"]["adjacent"] == []  # only a sea candidate, no land

    sea = registry["sea_candidates"]
    assert {"a": "B", "b": "Island", "gap": 50} in sea
    assert registry["adjacency_derivation"]["land_edges"] == 1
    assert registry["adjacency_derivation"]["sea_candidates"] == len(sea)


def test_apply_result_passes_the_validator():
    registry = _mini_registry()
    row = [1, 1, SENTINEL, 2, 2] + [SENTINEL] * 50 + [3, 3]
    flat, w, h = _grid([row])
    brk.apply_adjacency_to_registry(registry, flat, w, h)

    findings = vpm.validate_adjacency(registry)
    assert [f for f in findings if f.severity == vpm.ERROR] == []
    # The island (no land edges) is flagged as a warning, not an error.
    isolated = [f for f in findings if f.code == "ISOLATED_PROVINCE"]
    assert [f.detail["region"] for f in isolated] == ["Island"]


# ---------------------------------------------------------------------------
# Shipped registry guard (Slice 1 completion pin).
# ---------------------------------------------------------------------------


def test_shipped_europe_registry_has_valid_symmetric_adjacency():
    if not EUROPE_REGISTRY.exists():
        pytest.skip("europe.json not present (binary map assets are local-only)")
    data = json.loads(EUROPE_REGISTRY.read_text(encoding="utf-8"))
    regions = data["regions"]

    # Every province declares an adjacency list (auto-derived in Slice 1).
    assert all("adjacent" in entry for entry in regions.values())

    # No structural graph errors: every target exists and every edge is mutual.
    findings = vpm.validate_adjacency(data)
    errors = [f for f in findings if f.severity == vpm.ERROR]
    assert errors == [], [f.message for f in errors]

    # Hand-review artifacts are present for Slice 2.
    assert "sea_candidates" in data
    assert data["adjacency_derivation"]["land_edges"] > 0
