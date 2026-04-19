"""
Scale Readiness Phase 1: Nation config completeness tests.

Ensures every nation with a capital has complete runtime coverage across
roster surfaces plus gold/AP/authority resolution. Catches drift when
adding new nations under the fallback-default contract.
"""

from backend.models.region import NATION_CAPITALS
from backend.nation_config import (
    RUNTIME_NATIONS,
    build_default_nation_actions,
    build_default_nation_authority,
    build_default_nation_gold,
    validate_runtime_nation_support,
)
from backend.models.diplomat import STARTING_DIPLOMATS
from backend.models.world_state import WorldState


class TestNationConfigCompleteness:
    """Every nation with a capital must have full runtime coverage."""

    def test_all_capital_nations_have_gold_resolution(self):
        resolved = build_default_nation_gold("France")
        for nation in NATION_CAPITALS:
            assert nation in resolved, (
                f"{nation} in NATION_CAPITALS but missing from resolved nation gold"
            )

    def test_all_capital_nations_have_action_resolution(self):
        resolved = build_default_nation_actions("__test_player__")
        for nation in NATION_CAPITALS:
            assert nation in resolved, (
                f"{nation} in NATION_CAPITALS but missing from resolved action budget"
            )

    def test_all_capital_nations_have_authority_resolution(self):
        resolved = build_default_nation_authority("__test_player__")
        for nation in NATION_CAPITALS:
            assert nation in resolved, (
                f"{nation} in NATION_CAPITALS but missing from resolved authority"
            )

    def test_all_capital_nations_have_diplomat(self):
        for nation in NATION_CAPITALS:
            assert nation in STARTING_DIPLOMATS, (
                f"{nation} has a capital but no starting diplomat"
            )

    def test_all_capital_nations_have_marshals(self):
        world = WorldState()
        marshal_nations = {m.nation for m in world.marshals.values()}
        for nation in NATION_CAPITALS:
            assert nation in marshal_nations, (
                f"{nation} has a capital but no marshals in default setup"
            )

    def test_validate_runtime_support_passes_current_roster(self):
        errors = validate_runtime_nation_support(NATION_CAPITALS.keys())
        assert errors == [], f"Current roster fails validation: {errors}"

    def test_runtime_nations_matches_capitals(self):
        assert set(RUNTIME_NATIONS) == set(NATION_CAPITALS.keys())

    def test_all_config_surfaces_consistent(self):
        surfaces = {
            "NATION_CAPITALS": set(NATION_CAPITALS.keys()),
            "STARTING_DIPLOMATS": set(STARTING_DIPLOMATS.keys()),
            "RUNTIME_NATIONS": set(RUNTIME_NATIONS),
            "RESOLVED_GOLD": set(build_default_nation_gold("France").keys()),
            "RESOLVED_ACTIONS": set(build_default_nation_actions("__test_player__").keys()),
            "RESOLVED_AUTHORITY": set(build_default_nation_authority("__test_player__").keys()),
        }
        reference = surfaces["NATION_CAPITALS"]
        mismatches = []
        for name, nations in surfaces.items():
            if nations != reference:
                missing = reference - nations
                extra = nations - reference
                parts = []
                if missing:
                    parts.append(f"missing {missing}")
                if extra:
                    parts.append(f"extra {extra}")
                mismatches.append(f"{name}: {', '.join(parts)}")
        assert not mismatches, (
            "Config surfaces inconsistent:\n" + "\n".join(mismatches)
        )
