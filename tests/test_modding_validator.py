"""
Tests for modding validation utilities.

Tests the validator functions that help modders create valid JSON files.
"""

import pytest
import json
from pathlib import Path

from backend.modding.validator import (
    validate_marshal,
    validate_region,
    validate_scenario,
    ValidationResult,
    ValidationError
)


# ============================================================================
# MARSHAL VALIDATION TESTS
# ============================================================================

class TestMarshalValidation:
    """Tests for validate_marshal function."""

    def test_valid_minimal_marshal(self):
        """Minimal valid marshal should pass."""
        data = {
            "name": "TestMarshal",
            "location": "Paris",
            "strength": 50000
        }
        result = validate_marshal(data)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_valid_full_marshal(self):
        """Full marshal with all fields should pass."""
        data = {
            "name": "Ney",
            "location": "Paris",
            "strength": 72000,
            "personality": "aggressive",
            "nation": "France",
            "movement_range": 2,
            "tactical_skill": 8,
            "skills": {
                "tactical": 7,
                "shock": 9,
                "defense": 4,
                "logistics": 5,
                "administration": 4,
                "command": 8
            },
            "ability": {
                "name": "Cavalry Charge",
                "description": "Can attack 2 regions away"
            },
            "cavalry": True,
            "morale": 80,
            "stance": "aggressive"
        }
        result = validate_marshal(data)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_required_fields(self):
        """Missing required fields should fail."""
        # Missing name
        result = validate_marshal({"location": "Paris", "strength": 50000})
        assert not result.is_valid
        assert any("name" in e.path for e in result.errors)

        # Missing location
        result = validate_marshal({"name": "Test", "strength": 50000})
        assert not result.is_valid
        assert any("location" in e.path for e in result.errors)

        # Missing strength
        result = validate_marshal({"name": "Test", "location": "Paris"})
        assert not result.is_valid
        assert any("strength" in e.path for e in result.errors)

    def test_invalid_personality(self):
        """Invalid personality should fail."""
        data = {
            "name": "Test",
            "location": "Paris",
            "strength": 50000,
            "personality": "reckless"  # Not a valid personality
        }
        result = validate_marshal(data)
        assert not result.is_valid
        assert any("personality" in e.path for e in result.errors)

    def test_invalid_stance(self):
        """Invalid stance should fail."""
        data = {
            "name": "Test",
            "location": "Paris",
            "strength": 50000,
            "stance": "retreating"  # Not a valid stance
        }
        result = validate_marshal(data)
        assert not result.is_valid
        assert any("stance" in e.path for e in result.errors)

    def test_negative_strength(self):
        """Negative strength should fail."""
        data = {
            "name": "Test",
            "location": "Paris",
            "strength": -1000
        }
        result = validate_marshal(data)
        assert not result.is_valid
        assert any("strength" in e.path for e in result.errors)

    def test_zero_strength_warning(self):
        """Zero strength should warn (not fail)."""
        data = {
            "name": "Test",
            "location": "Paris",
            "strength": 0
        }
        result = validate_marshal(data)
        assert result.is_valid  # Zero is technically valid
        assert any("strength" in w.path for w in result.warnings)

    def test_unknown_nation_warning(self):
        """Unknown nation should warn (not fail)."""
        data = {
            "name": "Test",
            "location": "Paris",
            "strength": 50000,
            "nation": "Mordor"  # Unknown nation
        }
        result = validate_marshal(data)
        assert result.is_valid  # Unknown nation is allowed (modders can add nations)
        assert any("nation" in w.path for w in result.warnings)

    def test_high_movement_range_warning(self):
        """Very high movement range should warn."""
        data = {
            "name": "Test",
            "location": "Paris",
            "strength": 50000,
            "movement_range": 5  # Very high
        }
        result = validate_marshal(data)
        assert result.is_valid
        assert any("movement_range" in w.path for w in result.warnings)

    def test_invalid_skills(self):
        """Invalid skill names should warn."""
        data = {
            "name": "Test",
            "location": "Paris",
            "strength": 50000,
            "skills": {
                "tactical": 7,
                "magic": 10  # Not a valid skill
            }
        }
        result = validate_marshal(data)
        assert result.is_valid  # Unknown skills warn, don't fail
        assert any("magic" in w.path for w in result.warnings)

    def test_not_object(self):
        """Non-object marshal should fail."""
        result = validate_marshal("not an object")
        assert not result.is_valid
        assert any("Must be an object" in e.message for e in result.errors)


# ============================================================================
# REGION VALIDATION TESTS
# ============================================================================

class TestRegionValidation:
    """Tests for validate_region function."""

    def test_valid_minimal_region(self):
        """Minimal valid region should pass."""
        data = {
            "name": "TestRegion",
            "adjacent_regions": ["Paris", "Lyon"]
        }
        result = validate_region(data)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_valid_full_region(self):
        """Full region with all fields should pass."""
        data = {
            "name": "TestCapital",
            "adjacent_regions": ["Province1", "Province2"],
            "income_value": 200,
            "is_capital": True,
            "controller": "France",
            "garrison_strength": 5000
        }
        result = validate_region(data)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_required_fields(self):
        """Missing required fields should fail."""
        # Missing name
        result = validate_region({"adjacent_regions": ["Paris"]})
        assert not result.is_valid
        assert any("name" in e.path for e in result.errors)

        # Missing adjacent_regions
        result = validate_region({"name": "Test"})
        assert not result.is_valid
        assert any("adjacent_regions" in e.path for e in result.errors)

    def test_empty_adjacent_regions_warning(self):
        """Empty adjacent_regions should warn (isolated region)."""
        data = {
            "name": "TestRegion",
            "adjacent_regions": []
        }
        result = validate_region(data)
        assert result.is_valid  # Technically valid
        assert any("isolated" in w.message for w in result.warnings)

    def test_negative_income(self):
        """Negative income should fail."""
        data = {
            "name": "TestRegion",
            "adjacent_regions": ["Paris"],
            "income_value": -100
        }
        result = validate_region(data)
        assert not result.is_valid
        assert any("income_value" in e.path for e in result.errors)

    def test_negative_garrison(self):
        """Negative garrison should fail."""
        data = {
            "name": "TestRegion",
            "adjacent_regions": ["Paris"],
            "garrison_strength": -100
        }
        result = validate_region(data)
        assert not result.is_valid
        assert any("garrison_strength" in e.path for e in result.errors)


# ============================================================================
# SCENARIO VALIDATION TESTS
# ============================================================================

class TestScenarioValidation:
    """Tests for validate_scenario function."""

    def test_valid_minimal_scenario(self):
        """Minimal valid scenario should pass."""
        data = {"player_nation": "France"}
        result = validate_scenario(data)
        assert result.is_valid

    def test_valid_full_scenario(self):
        """Full scenario with marshals and regions should pass."""
        data = {
            "player_nation": "France",
            "current_turn": 1,
            "gold": 2000,
            "regions": {
                "Paris": {
                    "name": "Paris",
                    "adjacent_regions": ["Lyon"],
                    "is_capital": True
                },
                "Lyon": {
                    "name": "Lyon",
                    "adjacent_regions": ["Paris"]
                }
            },
            "marshals": {
                "Ney": {
                    "name": "Ney",
                    "location": "Paris",
                    "strength": 72000
                }
            }
        }
        result = validate_scenario(data)
        assert result.is_valid

    def test_marshal_location_not_region(self):
        """Marshal in non-existent region should fail."""
        data = {
            "player_nation": "France",
            "regions": {
                "Paris": {
                    "name": "Paris",
                    "adjacent_regions": []
                }
            },
            "marshals": {
                "Ney": {
                    "name": "Ney",
                    "location": "Belgium",  # Not defined in regions
                    "strength": 72000
                }
            }
        }
        result = validate_scenario(data)
        assert not result.is_valid
        assert any("Belgium" in e.message for e in result.errors)

    def test_nonexistent_adjacent_region(self):
        """Adjacent region that doesn't exist should fail."""
        data = {
            "player_nation": "France",
            "regions": {
                "Paris": {
                    "name": "Paris",
                    "adjacent_regions": ["London"]  # London not defined
                }
            }
        }
        result = validate_scenario(data)
        assert not result.is_valid
        assert any("London" in e.message for e in result.errors)

    def test_nonbidirectional_adjacency_warning(self):
        """Non-bidirectional adjacency should warn."""
        data = {
            "player_nation": "France",
            "regions": {
                "Paris": {
                    "name": "Paris",
                    "adjacent_regions": ["Lyon"]  # Paris -> Lyon
                },
                "Lyon": {
                    "name": "Lyon",
                    "adjacent_regions": []  # Lyon does NOT have Paris
                }
            }
        }
        result = validate_scenario(data, check_adjacency=True)
        assert result.is_valid  # Warnings don't fail validation
        assert any("non-bidirectional" in w.message for w in result.warnings)

    def test_name_key_mismatch_warning(self):
        """Marshal/region name not matching key should warn."""
        data = {
            "player_nation": "France",
            "marshals": {
                "Ney": {
                    "name": "Michel Ney",  # Doesn't match key "Ney"
                    "location": "Paris",
                    "strength": 72000
                }
            }
        }
        result = validate_scenario(data)
        assert result.is_valid  # Just a warning
        assert any("doesn't match internal name" in w.message for w in result.warnings)

    def test_negative_gold(self):
        """Negative gold should fail."""
        data = {
            "player_nation": "France",
            "gold": -500
        }
        result = validate_scenario(data)
        assert not result.is_valid
        assert any("gold" in e.path for e in result.errors)

    def test_scenario_from_file(self, tmp_path):
        """Loading scenario from file should work."""
        scenario_data = {
            "player_nation": "France",
            "gold": 1000
        }
        scenario_file = tmp_path / "test_scenario.json"
        scenario_file.write_text(json.dumps(scenario_data))

        result = validate_scenario(str(scenario_file))
        assert result.is_valid

    def test_scenario_file_not_found(self):
        """Missing file should fail."""
        result = validate_scenario("/nonexistent/scenario.json")
        assert not result.is_valid
        assert any("not found" in e.message for e in result.errors)

    def test_scenario_invalid_json(self, tmp_path):
        """Invalid JSON should fail."""
        scenario_file = tmp_path / "invalid.json"
        scenario_file.write_text("{ not valid }")

        result = validate_scenario(str(scenario_file))
        assert not result.is_valid
        assert any("Invalid JSON" in e.message for e in result.errors)

    def test_scenario_not_object(self):
        """Scenario must be object, not array."""
        result = validate_scenario([1, 2, 3])
        assert not result.is_valid
        assert any("JSON object" in e.message for e in result.errors)


# ============================================================================
# VALIDATION RESULT TESTS
# ============================================================================

class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_initial_state(self):
        """New result should be valid with no errors."""
        result = ValidationResult()
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_add_error(self):
        """Adding error should mark result as invalid."""
        result = ValidationResult()
        result.add_error("test.path", "Test error message")

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].path == "test.path"
        assert result.errors[0].message == "Test error message"
        assert result.errors[0].severity == "error"

    def test_add_warning(self):
        """Adding warning should not mark result as invalid."""
        result = ValidationResult()
        result.add_warning("test.path", "Test warning message")

        assert result.is_valid  # Warnings don't fail validation
        assert len(result.warnings) == 1
        assert result.warnings[0].severity == "warning"

    def test_merge(self):
        """Merging results should combine errors and warnings."""
        result1 = ValidationResult()
        result1.add_error("path1", "Error 1")
        result1.add_warning("path1", "Warning 1")

        result2 = ValidationResult()
        result2.add_error("path2", "Error 2")

        result1.merge(result2)

        assert len(result1.errors) == 2
        assert len(result1.warnings) == 1
        assert not result1.is_valid


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
