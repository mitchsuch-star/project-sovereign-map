"""
Deep Audit Session 9: Hardening fix tests.

Tests for:
- Atomic save writes (temp file + rename)
- Corrupt enum deserialization (bad Stance → defaults NEUTRAL)
- Coalition deepcopy (nested members not shared)
- DiplomaticRepresentative round-trip serialization
- Trust.set() usage (encapsulated access)
- Self-relationship no-op guard
"""

import json
from unittest.mock import patch

from backend.models.marshal import Marshal, Stance
from backend.models.world_state import WorldState
from backend.models.trust import Trust
from backend.models.diplomat import DiplomaticRepresentative
from backend.save_manager import save_game


# ============================================================================
# FIX 1: ATOMIC SAVE WRITES
# ============================================================================

class TestAtomicSaveWrites:
    """Verify save_game uses atomic write pattern (temp + rename)."""

    def test_save_creates_valid_file(self, tmp_path):
        """Basic save produces readable JSON."""
        world = WorldState()
        filepath = tmp_path / "test_save.json"
        result = save_game(world, save_name="Test", filepath=filepath)

        assert result["success"] is True
        assert filepath.exists()

        with open(filepath, 'r') as f:
            data = json.load(f)
        assert "metadata" in data
        assert "world_state" in data

    def test_save_no_temp_file_remains(self, tmp_path):
        """Temp file is cleaned up after successful save."""
        world = WorldState()
        filepath = tmp_path / "test_save.json"
        save_game(world, save_name="Test", filepath=filepath)

        tmp_file = filepath.with_suffix('.tmp')
        assert not tmp_file.exists()

    def test_save_cleans_temp_on_failure(self, tmp_path):
        """Temp file is removed if json.dump fails."""
        world = WorldState()
        filepath = tmp_path / "test_save.json"

        with patch('backend.save_manager.json.dump', side_effect=TypeError("mock error")):
            result = save_game(world, save_name="Test", filepath=filepath)

        assert result["success"] is False
        tmp_file = filepath.with_suffix('.tmp')
        assert not tmp_file.exists()
        assert not filepath.exists()


# ============================================================================
# FIX 2: ENUM DESERIALIZATION GUARD
# ============================================================================

class TestEnumDeserializationGuard:
    """Corrupt Stance values should default to NEUTRAL, not crash."""

    def test_valid_stance_deserializes(self):
        """Normal stance values still work."""
        marshal = Marshal("Ney", "Paris", 20000, "aggressive")
        marshal.stance = Stance.AGGRESSIVE
        data = marshal.to_dict()

        restored = Marshal.from_dict(data)
        assert restored.stance == Stance.AGGRESSIVE

    def test_corrupt_stance_defaults_to_neutral(self):
        """Invalid stance value falls back to NEUTRAL."""
        marshal = Marshal("Ney", "Paris", 20000, "aggressive")
        data = marshal.to_dict()
        data["stance"] = "INVALID_GARBAGE_VALUE"

        restored = Marshal.from_dict(data)
        assert restored.stance == Stance.NEUTRAL

    def test_empty_stance_defaults_to_neutral(self):
        """Empty string stance falls back to NEUTRAL."""
        marshal = Marshal("Ney", "Paris", 20000, "aggressive")
        data = marshal.to_dict()
        data["stance"] = ""

        restored = Marshal.from_dict(data)
        assert restored.stance == Stance.NEUTRAL


# ============================================================================
# FIX 3: COALITION DEEPCOPY
# ============================================================================

class TestCoalitionDeepcopy:
    """Coalition from_dict must deepcopy nested structures."""

    def test_coalition_members_not_shared(self):
        """Modifying deserialized coalition members doesn't affect original data."""
        world = WorldState()
        world.active_coalition = {
            "name": "Third Coalition",
            "members": ["Austria", "Prussia", "Russia"],
            "leader": "Austria",
            "posture": "aggressive",
        }
        data = world.to_dict()

        # Deserialize
        restored = WorldState.from_dict(data)

        # Modify the restored coalition's members list
        restored.active_coalition["members"].append("Britain")

        # Original data should be unchanged
        assert "Britain" not in data["active_coalition"]["members"]
        assert len(data["active_coalition"]["members"]) == 3

    def test_brewing_coalition_not_shared(self):
        """Modifying deserialized brewing coalition doesn't affect original data."""
        world = WorldState()
        world.coalition_brewing = {
            "nations": ["Austria", "Prussia"],
            "turns_remaining": 3,
        }
        data = world.to_dict()

        restored = WorldState.from_dict(data)
        restored.coalition_brewing["nations"].append("Russia")

        assert "Russia" not in data["coalition_brewing"]["nations"]


# ============================================================================
# FIX 4: DIPLOMATIC REPRESENTATIVE ROUND-TRIP
# ============================================================================

class TestDiplomaticRepresentativeRoundTrip:
    """DiplomaticRepresentative must survive to_dict/from_dict."""

    def test_basic_round_trip(self):
        """All fields preserved through serialization."""
        rep = DiplomaticRepresentative(
            name="Talleyrand",
            nation="France",
            personality="schemer",
            skill=10,
            trust=55,
            biography="The survivor of Versailles.",
        )
        data = rep.to_dict()
        restored = DiplomaticRepresentative.from_dict(data)

        assert restored.name == "Talleyrand"
        assert restored.nation == "France"
        assert restored.personality == "schemer"
        assert restored.skill == 10
        assert restored.trust == 55
        assert restored.biography == "The survivor of Versailles."

    def test_defaults_on_missing_fields(self):
        """from_dict handles missing fields gracefully."""
        data = {"name": "Unknown Rep"}
        restored = DiplomaticRepresentative.from_dict(data)

        assert restored.name == "Unknown Rep"
        assert restored.nation == "Unknown"
        assert restored.personality == "loyalist"
        assert restored.skill == 5
        assert restored.trust == 65
        assert restored.biography == ""

    def test_skill_is_int(self):
        """Skill is always int, even if stored as float."""
        data = {
            "name": "Test",
            "nation": "Austria",
            "personality": "hawk",
            "skill": 7.5,
            "trust": 65,
        }
        restored = DiplomaticRepresentative.from_dict(data)
        assert isinstance(restored.skill, int)
        assert restored.skill == 7


# ============================================================================
# FIX 5: TRUST.SET() ENCAPSULATION
# ============================================================================

class TestTrustEncapsulation:
    """Trust.set() should be used instead of direct _value access."""

    def test_trust_set_clamps_high(self):
        """Trust.set() clamps to 100."""
        t = Trust(50)
        t.set(150)
        assert t.value == 100

    def test_trust_set_clamps_low(self):
        """Trust.set() clamps to 0."""
        t = Trust(50)
        t.set(-20)
        assert t.value == 0

    def test_trust_set_exact(self):
        """Trust.set() sets exact value within range."""
        t = Trust(50)
        t.set(15)
        assert t.value == 15


# ============================================================================
# FIX 6: SELF-RELATIONSHIP GUARD
# ============================================================================

class TestSelfRelationshipGuard:
    """modify_relationship with self should be a no-op."""

    def test_self_relationship_returns_zero(self):
        """Modifying relationship with self returns 0 change."""
        marshal = Marshal("Ney", "Paris", 20000, "aggressive")
        result = marshal.modify_relationship("Ney", 5)
        assert result == 0

    def test_self_relationship_not_stored(self):
        """Self-relationship is not stored in relationships dict."""
        marshal = Marshal("Ney", "Paris", 20000, "aggressive")
        marshal.modify_relationship("Ney", 5)
        assert "Ney" not in marshal.relationships

    def test_other_relationship_still_works(self):
        """Normal relationship modification still works."""
        marshal = Marshal("Ney", "Paris", 20000, "aggressive")
        result = marshal.modify_relationship("Davout", 1)
        assert result == 1
        assert marshal.get_relationship("Davout") == 1
