"""Slice 2 (Map cutover) -- authored Europe registry data + validator checks.

Two concerns are pinned here:

  1. ``europe.json`` is the complete, validated 126-province source: every
     province has a real (non-placeholder, unique) historical name, a known
     1805 ``starting_controller``, a valid ``terrain`` / ``region_type``,
     symmetric adjacency, a coastal flag consistent with its sea links, and
     every nation has exactly one owned capital.
  2. The Slice-2 validator hardening: the new gameplay-field checks plus the
     M4 (omitted-vs-empty ``adjacent``) and M5 (duplicate adjacency entry)
     adjacency findings.

Plan reference: docs/MAP_IMPLEMENTATION_PLAN.md Slice 2.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tools import validate_province_map as vpm

REPO_ROOT = Path(__file__).resolve().parents[1]
EUROPE_REGISTRY = (
    REPO_ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe.json"
)
EUROPE_VISUAL = EUROPE_REGISTRY.with_name("europe_visual.png")
EUROPE_LOOKUP = EUROPE_REGISTRY.with_name("europe_lookup.png")

PLACEHOLDER = re.compile(r"^Region_\d+$")


@pytest.fixture(scope="module")
def europe() -> dict:
    return json.loads(EUROPE_REGISTRY.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Authored registry data.
# ---------------------------------------------------------------------------


def test_europe_has_126_provinces(europe):
    assert len(europe["regions"]) == 126


def test_every_province_is_fully_authored(europe):
    required = ("name", "starting_controller", "terrain", "region_type",
                "is_coastal", "is_capital", "adjacent")
    for name, entry in europe["regions"].items():
        for field in required:
            assert field in entry, f"{name} missing {field}"


def test_no_placeholder_names_remain(europe):
    for name, entry in europe["regions"].items():
        assert not PLACEHOLDER.match(entry["name"]), f"{name} still placeholder"


def test_province_names_are_unique(europe):
    names = [e["name"] for e in europe["regions"].values()]
    assert len(names) == len(set(names))


def test_all_terrains_and_region_types_valid(europe):
    for name, entry in europe["regions"].items():
        assert entry["terrain"] in vpm.VALID_TERRAINS, f"{name} {entry['terrain']}"
        assert entry["region_type"] in vpm.VALID_REGION_TYPES, name


def test_every_nation_owns_at_least_one_province(europe):
    owners = {e["starting_controller"] for e in europe["regions"].values()}
    assert owners  # discovered roster is non-empty
    counts = {o: 0 for o in owners}
    for e in europe["regions"].values():
        counts[e["starting_controller"]] += 1
    assert all(c >= 1 for c in counts.values())


def test_every_nation_has_exactly_one_owned_capital(europe):
    caps: dict[str, list[str]] = {}
    for name, entry in europe["regions"].items():
        if entry["is_capital"]:
            caps.setdefault(entry["starting_controller"], []).append(name)
    owners = {e["starting_controller"] for e in europe["regions"].values()}
    for nation in owners:
        assert len(caps.get(nation, [])) == 1, f"{nation}: {caps.get(nation)}"


def test_is_capital_matches_region_type_capital(europe):
    for name, entry in europe["regions"].items():
        assert entry["is_capital"] == (entry["region_type"] == "capital"), name


def test_adjacency_is_symmetric(europe):
    adj = {n: set(e.get("adjacent", [])) for n, e in europe["regions"].items()}
    for name, neighbours in adj.items():
        for other in neighbours:
            assert other in europe["regions"], f"{name} -> unknown {other}"
            assert name in adj[other], f"{name}->{other} not mirrored"


def test_sea_link_endpoints_are_coastal(europe):
    for pair in europe.get("sea_links", []):
        for idx in pair:
            key = f"Region_{idx:03d}"
            assert europe["regions"][key]["is_coastal"], f"{key} sea-link but inland"


def test_expected_capitals_owned_by_expected_nations(europe):
    # A representative spot-check of the discovered 1805 roster.
    expected = {
        "Paris": "France", "London": "Britain", "Madrid": "Spain",
        "Lisbon": "Portugal", "Vienna": "Austria", "Berlin": "Prussia",
        "Constantinople": "Ottoman", "Stockholm": "Sweden", "Copenhagen": "Denmark",
    }
    by_name = {e["name"]: e for e in europe["regions"].values()}
    for city, nation in expected.items():
        assert by_name[city]["starting_controller"] == nation
        assert by_name[city]["is_capital"]


def test_europe_registry_passes_validator_strict(europe):
    report = vpm.validate_all(EUROPE_REGISTRY, EUROPE_VISUAL, EUROPE_LOOKUP)
    assert report.errors == []
    assert report.warnings == []


# ---------------------------------------------------------------------------
# Validator hardening: gameplay-field checks.
# ---------------------------------------------------------------------------


def _gameplay_registry(regions: dict[str, dict], sea_links=None) -> dict:
    data = {
        "version": 2,
        "no_province_color": [0, 0, 0],
        "regions": {},
    }
    for i, (name, extra) in enumerate(regions.items()):
        entry = {"province_id": name.lower(), "lookup_color": [i + 1, i + 1, i + 1],
                 "anchor": [0, 0]}
        entry.update(extra)
        data["regions"][name] = entry
    if sea_links is not None:
        data["sea_links"] = sea_links
    return data


def _full(name, controller, cap=False, terrain="plains", rtype="town",
          coastal=False, adjacent=None):
    return {
        "name": name, "starting_controller": controller, "is_capital": cap,
        "terrain": terrain, "region_type": "capital" if cap else rtype,
        "is_coastal": coastal, "adjacent": adjacent if adjacent is not None else [],
    }


def test_gameplay_checks_skipped_without_starting_controller():
    data = _gameplay_registry({"A": {}, "B": {}})
    assert vpm.validate_gameplay_fields(data) == []


def test_gameplay_flags_placeholder_name():
    data = _gameplay_registry({"Region_000": _full("Region_000", "France", cap=True)})
    codes = [f.code for f in vpm.validate_gameplay_fields(data)]
    assert "PLACEHOLDER_NAME" in codes


def test_gameplay_flags_duplicate_name():
    data = _gameplay_registry({
        "R0": _full("Paris", "France", cap=True),
        "R1": _full("Paris", "France"),
    })
    codes = [f.code for f in vpm.validate_gameplay_fields(data)]
    assert "DUPLICATE_PROVINCE_NAME" in codes


def test_gameplay_flags_invalid_terrain_and_type():
    data = _gameplay_registry({
        "R0": _full("Paris", "France", cap=True, terrain="swamp"),
    })
    bad = _full("Lyon", "France")
    bad["region_type"] = "megacity"
    data["regions"]["R1"] = {"province_id": "r1", "lookup_color": [9, 9, 9],
                             "anchor": [0, 0], **bad}
    codes = [f.code for f in vpm.validate_gameplay_fields(data)]
    assert "INVALID_TERRAIN" in codes
    assert "INVALID_REGION_TYPE" in codes


def test_gameplay_flags_missing_field():
    entry = _full("Paris", "France", cap=True)
    del entry["terrain"]
    data = _gameplay_registry({"R0": entry})
    codes = [f.code for f in vpm.validate_gameplay_fields(data)]
    assert "MISSING_GAMEPLAY_FIELD" in codes


def test_gameplay_flags_nation_without_capital():
    data = _gameplay_registry({"R0": _full("Paris", "France")})
    codes = [f.code for f in vpm.validate_gameplay_fields(data)]
    assert "NATION_MISSING_CAPITAL" in codes


def test_gameplay_flags_nation_with_two_capitals():
    data = _gameplay_registry({
        "R0": _full("Paris", "France", cap=True),
        "R1": _full("Lyon", "France", cap=True),
    })
    codes = [f.code for f in vpm.validate_gameplay_fields(data)]
    assert "NATION_MULTIPLE_CAPITALS" in codes


def test_gameplay_flags_inland_sea_edge():
    data = _gameplay_registry(
        {
            "R0": _full("Paris", "France", cap=True, coastal=False),
            "R1": _full("Dover", "Britain", cap=True, coastal=True),
        },
        sea_links=[["R0", "R1"]],
    )
    codes = [f.code for f in vpm.validate_gameplay_fields(data)]
    assert "INLAND_SEA_EDGE" in codes


def test_gameplay_clean_registry_has_no_findings():
    data = _gameplay_registry(
        {
            "R0": _full("Paris", "France", cap=True, coastal=True, adjacent=["R1"]),
            "R1": _full("Dover", "Britain", cap=True, coastal=True, adjacent=["R0"]),
        },
        sea_links=[["R0", "R1"]],
    )
    assert vpm.validate_gameplay_fields(data) == []


# ---------------------------------------------------------------------------
# Validator hardening: M4 (omitted vs empty) and M5 (duplicate entry).
# ---------------------------------------------------------------------------


def _adj_registry(adjacency: dict[str, list | None]) -> dict:
    data = {"version": 2, "no_province_color": [0, 0, 0], "regions": {}}
    for i, (name, adj) in enumerate(adjacency.items()):
        entry = {"province_id": name.lower(), "lookup_color": [i + 1, i + 1, i + 1],
                 "anchor": [0, 0]}
        if adj is not None:  # None => omit the 'adjacent' key entirely
            entry["adjacent"] = list(adj)
        data["regions"][name] = entry
    return data


def test_m4_omitted_adjacent_is_not_isolated():
    # B has no 'adjacent' key at all -> "not yet authored", no ISOLATED warning
    # and no asymmetry demanded of it.
    data = _adj_registry({"A": ["B"], "B": None})
    findings = vpm.validate_adjacency(data)
    codes = [f.code for f in findings]
    assert "ISOLATED_PROVINCE" not in codes
    assert "ADJACENCY_ASYMMETRY" not in codes


def test_m4_explicit_empty_adjacent_is_isolated():
    # Explicit [] means "truly isolated" and is still warned (and asymmetric).
    data = _adj_registry({"A": ["B"], "B": []})
    findings = vpm.validate_adjacency(data)
    codes = [f.code for f in findings]
    assert "ISOLATED_PROVINCE" in codes
    assert "ADJACENCY_ASYMMETRY" in codes


def test_m5_duplicate_adjacency_entry_is_warning():
    data = _adj_registry({"A": ["B", "B"], "B": ["A"]})
    findings = vpm.validate_adjacency(data)
    dups = [f for f in findings if f.code == "DUPLICATE_ADJACENCY_ENTRY"]
    assert len(dups) == 1
    assert dups[0].severity == vpm.WARNING
    assert dups[0].detail == {"region": "A", "target": "B"}
    # the duplicate must not spuriously fire asymmetry (A<->B is symmetric)
    assert not [f for f in findings if f.code == "ADJACENCY_ASYMMETRY"]
