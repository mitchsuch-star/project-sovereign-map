"""
Scale Readiness Phase 1: Nation config completeness tests.

Ensures every nation with a capital has matching entries across all config
surfaces (gold, AP, authority, diplomats, marshals). Catches drift when
adding new nations.
"""

from backend.models.region import NATION_CAPITALS
from backend.nation_config import (
    DEFAULT_NATION_GOLD, BASE_NATION_ACTIONS, DEFAULT_NATION_AUTHORITY,
    RUNTIME_NATIONS, validate_runtime_nation_support,
)
from backend.models.diplomat import STARTING_DIPLOMATS
from backend.models.world_state import WorldState


class TestNationConfigCompleteness:
    """Every nation with a capital must have all config surfaces wired."""

    def test_all_capital_nations_have_gold_config(self):
        for nation in NATION_CAPITALS:
            assert nation in DEFAULT_NATION_GOLD, (
                f"{nation} in NATION_CAPITALS but missing from DEFAULT_NATION_GOLD"
            )

    def test_all_capital_nations_have_action_config(self):
        for nation in NATION_CAPITALS:
            assert nation in BASE_NATION_ACTIONS, (
                f"{nation} in NATION_CAPITALS but missing from BASE_NATION_ACTIONS"
            )

    def test_all_capital_nations_have_authority_config(self):
        for nation in NATION_CAPITALS:
            assert nation in DEFAULT_NATION_AUTHORITY, (
                f"{nation} in NATION_CAPITALS but missing from DEFAULT_NATION_AUTHORITY"
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
            "DEFAULT_NATION_GOLD": set(DEFAULT_NATION_GOLD.keys()),
            "BASE_NATION_ACTIONS": set(BASE_NATION_ACTIONS.keys()),
            "DEFAULT_NATION_AUTHORITY": set(DEFAULT_NATION_AUTHORITY.keys()),
            "STARTING_DIPLOMATS": set(STARTING_DIPLOMATS.keys()),
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
