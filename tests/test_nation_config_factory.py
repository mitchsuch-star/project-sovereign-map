"""
Scale Readiness §3.1: Nation Config Factory Pattern tests.

Locks in the new data-driven factories for marshals and diplomats, plus the
``DEFAULT_NATION_DEFAULTS`` fallback in ``nation_config.py``. A nation that
adds only a capital + diplomat (no gold / actions / authority override)
must validate and resolve via the defaults.
"""

from __future__ import annotations

from unittest.mock import patch

from backend.models.diplomat import (
    DIPLOMAT_DEFINITIONS,
    STARTING_DIPLOMATS,
    create_diplomat_from_data,
    create_starting_diplomats,
)
from backend.models.marshal import (
    ENEMY_MARSHALS_DATA,
    FRENCH_MARSHALS_DATA,
    Marshal,
    create_enemy_marshals,
    create_marshal_from_data,
    create_marshals_from_data,
    create_starting_marshals,
)
from backend.nation_config import (
    BASE_NATION_ACTIONS,
    DEFAULT_NATION_AUTHORITY,
    DEFAULT_NATION_DEFAULTS,
    DEFAULT_NATION_GOLD,
    build_default_nation_actions,
    build_default_nation_authority,
    build_default_nation_gold,
    validate_runtime_nation_support,
)


class TestMarshalFactory:
    def test_create_marshal_from_data_sets_all_fields(self):
        defn = {
            "name": "TestMarshal",
            "location": "Paris",
            "strength": 10000,
            "personality": "cautious",
            "nation": "France",
            "biography": "A test marshal.",
            "relationships": {"Other": 1},
        }
        m = create_marshal_from_data(defn)
        assert isinstance(m, Marshal)
        assert m.name == "TestMarshal"
        assert m.nation == "France"
        assert m.strength == 10000
        assert m.biography == "A test marshal."
        # relationships are applied by the roster factory, not the single-item one
        assert m.relationships == {}

    def test_create_marshals_from_data_applies_relationships(self):
        defs = [
            {"name": "A", "location": "Paris", "strength": 100, "personality": "cautious",
             "nation": "France", "relationships": {"B": 2}},
            {"name": "B", "location": "Lyon", "strength": 100, "personality": "cautious",
             "nation": "France", "relationships": {"A": -1}},
        ]
        marshals = create_marshals_from_data(defs)
        assert set(marshals.keys()) == {"A", "B"}
        assert marshals["A"].relationships == {"B": 2}
        assert marshals["B"].relationships == {"A": -1}

    def test_create_starting_marshals_preserves_expected_roster(self):
        marshals = create_starting_marshals()
        assert set(marshals.keys()) == {"Ney", "Davout", "Grouchy", "Drouot"}
        # Key invariants that downstream code relies on
        assert marshals["Ney"].cavalry is True
        assert marshals["Drouot"].artillery is True
        assert marshals["Davout"].skills["tactical"] == 9
        assert marshals["Ney"].relationships["Davout"] == -2

    def test_create_enemy_marshals_preserves_cross_nation_relationships(self):
        enemies = create_enemy_marshals()
        # Wellington ↔ Blucher devoted pairing
        assert enemies["Wellington"].relationships["Blucher"] == 2
        assert enemies["Blucher"].relationships["Wellington"] == 2
        # Austria ↔ Austria internal pairing
        assert enemies["ArchdukeCharles"].relationships["Schwarzenberg"] == 1
        # Intentional asymmetry preserved: Uxbridge never got an Austria link
        assert "ArchdukeCharles" not in enemies["Uxbridge"].relationships
        assert "Schwarzenberg" not in enemies["Uxbridge"].relationships

    def test_french_and_enemy_data_lists_cover_full_roster(self):
        names_french = {d["name"] for d in FRENCH_MARSHALS_DATA}
        names_enemy = {d["name"] for d in ENEMY_MARSHALS_DATA}
        assert names_french == {"Ney", "Davout", "Grouchy", "Drouot"}
        assert names_enemy == {
            "Wellington", "Uxbridge", "Blucher", "Gneisenau",
            "ArchdukeCharles", "Schwarzenberg", "Reynier",
        }


class TestDiplomatFactory:
    def test_create_diplomat_from_data_sets_nation(self):
        d = create_diplomat_from_data(
            "Testland",
            {"name": "Envoy", "personality": "dove", "skill": 5, "biography": "Keeps the peace."},
        )
        assert d.nation == "Testland"
        assert d.name == "Envoy"
        assert d.skill == 5
        assert d.biography == "Keeps the peace."

    def test_starting_diplomats_matches_definitions(self):
        assert set(STARTING_DIPLOMATS.keys()) == set(DIPLOMAT_DEFINITIONS.keys())
        for nation, defn in DIPLOMAT_DEFINITIONS.items():
            d = STARTING_DIPLOMATS[nation]
            assert d.name == defn["name"]
            assert d.personality == defn["personality"]
            assert d.skill == defn["skill"]
            assert d.nation == nation

    def test_create_starting_diplomats_returns_fresh_instances(self):
        batch_a = create_starting_diplomats()
        batch_b = create_starting_diplomats()
        for nation in batch_a:
            assert batch_a[nation] is not batch_b[nation]
            assert batch_a[nation].name == batch_b[nation].name


class TestDefaultNationDefaults:
    def test_default_nation_defaults_has_expected_keys(self):
        assert "gold" in DEFAULT_NATION_DEFAULTS
        assert "actions" in DEFAULT_NATION_DEFAULTS
        assert "authority" in DEFAULT_NATION_DEFAULTS

    def test_build_gold_uses_default_when_override_missing(self):
        # Simulate a nation that has no override: patch RUNTIME_NATIONS to include
        # a pretend nation and verify build_default_nation_gold falls back.
        with patch("backend.nation_config.RUNTIME_NATIONS", ("France", "Testland")):
            result = build_default_nation_gold("France")
        assert result["France"] == DEFAULT_NATION_GOLD["France"]
        assert result["Testland"] == DEFAULT_NATION_DEFAULTS["gold"]

    def test_build_actions_uses_default_when_override_missing(self):
        with patch("backend.nation_config.RUNTIME_NATIONS", ("France", "Testland")):
            result = build_default_nation_actions("France")
        assert result["Testland"] == DEFAULT_NATION_DEFAULTS["actions"]

    def test_build_authority_uses_default_when_override_missing(self):
        with patch("backend.nation_config.RUNTIME_NATIONS", ("France", "Testland")):
            result = build_default_nation_authority("France")
        assert result["Testland"] == DEFAULT_NATION_DEFAULTS["authority"]

    def test_validator_accepts_nation_with_only_capital_and_diplomat(self):
        """A nation with just capital + diplomat (no economy overrides) validates."""
        from backend.models.diplomat import DiplomaticRepresentative

        fake_capitals = {"France": "Paris", "Testland": "Test City"}
        fake_diplomats = {
            "France": STARTING_DIPLOMATS["France"],
            "Testland": DiplomaticRepresentative(
                name="Envoy", nation="Testland", personality="dove", skill=3,
            ),
        }
        with patch("backend.nation_config.NATION_CAPITALS", fake_capitals), \
             patch("backend.nation_config.STARTING_DIPLOMATS", fake_diplomats):
            errors = validate_runtime_nation_support(["France", "Testland"])
        assert errors == [], f"Unexpected errors: {errors}"

    def test_validator_still_rejects_missing_capital(self):
        """Removing capital + diplomat still errors even when defaults cover economy."""
        errors = validate_runtime_nation_support(["Atlantis"])
        assert any("missing capital mapping" in e for e in errors)
        assert any("missing diplomat config" in e for e in errors)

    def test_existing_roster_still_has_explicit_overrides(self):
        """Current 5 nations keep their explicit entries for clarity."""
        expected = {"France", "Britain", "Prussia", "Austria", "Saxony"}
        assert set(DEFAULT_NATION_GOLD.keys()) == expected
        assert set(BASE_NATION_ACTIONS.keys()) == expected
        assert set(DEFAULT_NATION_AUTHORITY.keys()) == expected
