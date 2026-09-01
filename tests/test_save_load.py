"""
Tests for the Save/Load system (Phase 6).

Covers:
- File I/O (save creates file, load restores, autosave, list, delete)
- Roundtrip integrity (turn, gold, marshal state, region state, economy)
- Backward compatibility (missing metadata, unknown fields, missing fields)
- API endpoints (save, load, list, error cases)
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from backend.save_manager import (
    save_game, load_game, autosave, list_saves, delete_save,
    AUTOSAVE_FILENAME, FORMAT_VERSION,
)
from backend.models.world_state import WorldState
from backend.models.marshal import Stance


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_save_dir(tmp_path):
    """Use a temporary directory for saves during tests."""
    test_dir = tmp_path / "saves"
    test_dir.mkdir()
    with patch("backend.save_manager.SAVE_DIR", test_dir):
        yield test_dir


@pytest.fixture
def world():
    """Create a fresh WorldState for testing."""
    return WorldState(player_nation="France")


@pytest.fixture
def modified_world():
    """Create a WorldState with non-default values for roundtrip testing."""
    w = WorldState(player_nation="France")
    # Modify turn
    w.current_turn = 15
    # Modify gold
    w.nation_gold["France"] = 2500
    w.nation_gold["Britain"] = 900
    w.nation_gold["Prussia"] = 450
    # Modify a marshal
    ney = w.get_marshal("Ney")
    if ney:
        ney.strength = 50000
        ney.morale = 65
        ney.location = "Belgium"
        ney.trust._value = 82
        ney.stance = Stance.AGGRESSIVE
        ney.fortified = True
        ney.defense_bonus = 0.10
        ney.turns_fortified = 3
    # Modify a region
    paris = w.regions.get("Paris")
    if paris:
        paris.stability = 75
        paris.war_damage = 0.15
    # Economy state
    w.nation_bankruptcy_turns["Britain"] = 2
    w.admin_actions_remaining = 1
    return w


# ============================================================================
# FILE I/O TESTS
# ============================================================================

class TestSaveGameCreatesFile:
    """save_game creates a valid JSON file."""

    def test_save_creates_file(self, test_save_dir, world):
        result = save_game(world, save_name="Test Save")
        assert result["success"] is True
        assert "filepath" in result

        filepath = Path(result["filepath"])
        assert filepath.exists()

        # Verify JSON is valid
        with open(filepath, 'r') as f:
            data = json.load(f)
        assert "metadata" in data
        assert "world_state" in data
        assert data["metadata"]["save_name"] == "Test Save"
        assert data["metadata"]["format_version"] == FORMAT_VERSION
        assert data["metadata"]["turn"] == 1
        assert data["metadata"]["player_nation"] == "France"

    def test_save_with_custom_filepath(self, test_save_dir, world):
        custom_path = test_save_dir / "custom_save.json"
        result = save_game(world, save_name="Custom", filepath=custom_path)
        assert result["success"] is True
        assert custom_path.exists()

    def test_save_sanitizes_filename(self, test_save_dir, world):
        result = save_game(world, save_name="My Save / Test : 1")
        assert result["success"] is True
        filepath = Path(result["filepath"])
        assert filepath.exists()
        # No slashes or colons in filename
        assert "/" not in filepath.name
        assert ":" not in filepath.name


class TestLoadGameRestoresState:
    """load_game restores state from a saved file."""

    def test_load_restores_state(self, test_save_dir, world):
        # Save
        world.current_turn = 10
        world.nation_gold["France"] = 9999
        save_result = save_game(world, save_name="Roundtrip", filepath=test_save_dir / "test.json")
        assert save_result["success"]

        # Modify world to prove load works
        world.current_turn = 1
        world.nation_gold["France"] = 0

        # Load
        load_result = load_game(test_save_dir / "test.json")
        assert load_result["success"] is True
        assert load_result["world"] is not None
        assert load_result["world"].current_turn == 10
        assert load_result["world"].nation_gold["France"] == 9999

    def test_load_clears_transient_data(self, test_save_dir, world):
        # Set transient data
        world.battles_this_turn = [{"test": "battle"}]
        ney = world.get_marshal("Ney")
        if ney:
            ney.in_combat_this_turn = True

        save_game(world, save_name="Transient", filepath=test_save_dir / "transient.json")
        result = load_game(test_save_dir / "transient.json")

        assert result["success"]
        loaded_world = result["world"]
        # CONSCIOUS FLIP (REV-F1, Aug 31, 2026): `battles_this_turn` is now a
        # deliberate NON-clear too — the fifth. The glorious charge's V2-2
        # engagement gate reads it to refuse a second engagement of the same
        # pair in one turn, so wiping it here handed the player a free extra
        # 2x-damage charge for the price of a save and a load. Measured
        # through the typed command path; every other gate survived the round
        # trip, so nothing masked it.
        assert loaded_world.battles_this_turn == [{"test": "battle"}]
        loaded_ney = loaded_world.get_marshal("Ney")
        if loaded_ney:
            # CONSCIOUS FLIP (Aug 30, 2026 review): `in_combat_this_turn` is
            # now a deliberate NON-clear, the fourth in `load_game`'s list and
            # for the same reason as the first three. It is one of only two
            # exemptions the turn-end idle pass honours, so wiping it here
            # marked every marshal who had fought that turn as IDLE after a
            # mid-turn save/load — and `idle_turns` drives the jealousy
            # grievance threshold, the hostile-pair triggers and vindication
            # decay. It is serialized, restored by `from_dict`, and cleared at
            # the real turn boundary by `clear_turn_battles`.
            assert loaded_ney.in_combat_this_turn is True


class TestAutosave:
    """autosave creates/overwrites the autosave file."""

    def test_autosave_creates_file(self, test_save_dir, world):
        result = autosave(world)
        assert result["success"] is True
        assert (test_save_dir / AUTOSAVE_FILENAME).exists()

    def test_autosave_overwrites(self, test_save_dir, world):
        # First autosave at turn 1
        world.current_turn = 1
        autosave(world)

        # Second autosave at turn 5
        world.current_turn = 5
        autosave(world)

        # Only one autosave file should exist
        autosave_files = list(test_save_dir.glob("autosave*"))
        assert len(autosave_files) == 1

        # Should contain turn 5 data
        with open(test_save_dir / AUTOSAVE_FILENAME, 'r') as f:
            data = json.load(f)
        assert data["metadata"]["turn"] == 5


class TestListSaves:
    """list_saves returns all saves sorted newest first."""

    def test_list_saves_returns_all(self, test_save_dir, world):
        save_game(world, save_name="Save A", filepath=test_save_dir / "save_a.json")
        save_game(world, save_name="Save B", filepath=test_save_dir / "save_b.json")
        save_game(world, save_name="Save C", filepath=test_save_dir / "save_c.json")

        saves = list_saves()
        assert len(saves) == 3

        # Each entry has required fields
        for s in saves:
            assert "filename" in s
            assert "filepath" in s
            assert "metadata" in s

    def test_list_saves_sorted_newest_first(self, test_save_dir, world):
        import time
        save_game(world, save_name="Older", filepath=test_save_dir / "older.json")
        time.sleep(0.05)  # Small delay to ensure different timestamps
        save_game(world, save_name="Newer", filepath=test_save_dir / "newer.json")

        saves = list_saves()
        assert len(saves) == 2
        assert saves[0]["metadata"]["save_name"] == "Newer"
        assert saves[1]["metadata"]["save_name"] == "Older"

    def test_list_saves_empty_dir(self, test_save_dir):
        saves = list_saves()
        assert saves == []

    def test_list_saves_skips_corrupt_files(self, test_save_dir, world):
        # Create a valid save
        save_game(world, save_name="Valid", filepath=test_save_dir / "valid.json")
        # Create a corrupt file
        with open(test_save_dir / "corrupt.json", 'w') as f:
            f.write("not valid json {{{")

        saves = list_saves()
        assert len(saves) == 1
        assert saves[0]["metadata"]["save_name"] == "Valid"


class TestDeleteSave:
    """delete_save removes files (but not autosave)."""

    def test_delete_save_removes_file(self, test_save_dir, world):
        filepath = test_save_dir / "to_delete.json"
        save_game(world, save_name="Delete Me", filepath=filepath)
        assert filepath.exists()

        result = delete_save(filepath)
        assert result["success"] is True
        assert not filepath.exists()

    def test_delete_autosave_blocked(self, test_save_dir, world):
        autosave(world)
        filepath = test_save_dir / AUTOSAVE_FILENAME
        assert filepath.exists()

        result = delete_save(filepath)
        assert result["success"] is False
        assert "Cannot delete autosave" in result["message"]
        assert filepath.exists()  # Still there

    def test_delete_missing_file(self, test_save_dir):
        result = delete_save(test_save_dir / "nonexistent.json")
        assert result["success"] is False
        assert "not found" in result["message"].lower()


class TestLoadGameErrors:
    """load_game handles error cases gracefully."""

    def test_load_missing_file(self, test_save_dir):
        result = load_game(test_save_dir / "nonexistent.json")
        assert result["success"] is False
        assert result["world"] is None
        assert "not found" in result["message"].lower()

    def test_load_corrupt_json(self, test_save_dir):
        filepath = test_save_dir / "corrupt.json"
        with open(filepath, 'w') as f:
            f.write("not json!")

        result = load_game(filepath)
        assert result["success"] is False
        assert result["world"] is None
        assert "corrupt" in result["message"].lower()

    def test_load_missing_world_state(self, test_save_dir):
        filepath = test_save_dir / "no_world.json"
        with open(filepath, 'w') as f:
            json.dump({"metadata": {"save_name": "No World", "format_version": FORMAT_VERSION}}, f)

        result = load_game(filepath)
        assert result["success"] is False
        assert "no world_state" in result["message"].lower()


# ============================================================================
# ROUNDTRIP INTEGRITY TESTS
# ============================================================================

class TestRoundtripTurn:
    """Full roundtrip preserves turn number."""

    def test_preserves_turn(self, test_save_dir, modified_world):
        filepath = test_save_dir / "turn_test.json"
        save_game(modified_world, filepath=filepath)

        result = load_game(filepath)
        assert result["success"]
        assert result["world"].current_turn == 15


class TestRoundtripGold:
    """Full roundtrip preserves gold values."""

    def test_preserves_gold(self, test_save_dir, modified_world):
        filepath = test_save_dir / "gold_test.json"
        save_game(modified_world, filepath=filepath)

        result = load_game(filepath)
        assert result["success"]
        w = result["world"]
        assert w.nation_gold["France"] == 2500
        assert w.nation_gold["Britain"] == 900
        assert w.nation_gold["Prussia"] == 450


class TestRoundtripMarshalState:
    """Full roundtrip preserves marshal state."""

    def test_preserves_marshal(self, test_save_dir, modified_world):
        filepath = test_save_dir / "marshal_test.json"
        save_game(modified_world, filepath=filepath)

        result = load_game(filepath)
        assert result["success"]
        w = result["world"]
        ney = w.get_marshal("Ney")
        assert ney is not None
        assert ney.strength == 50000
        assert ney.morale == 65
        assert ney.location == "Belgium"
        assert int(ney.trust.value) == 82
        assert ney.stance == Stance.AGGRESSIVE
        assert ney.fortified is True
        assert ney.defense_bonus == pytest.approx(0.10, abs=0.001)
        assert ney.turns_fortified == 3


class TestRoundtripRegionState:
    """Full roundtrip preserves region state."""

    def test_preserves_region(self, test_save_dir, modified_world):
        filepath = test_save_dir / "region_test.json"
        save_game(modified_world, filepath=filepath)

        result = load_game(filepath)
        assert result["success"]
        w = result["world"]
        paris = w.regions.get("Paris")
        assert paris is not None
        assert paris.stability == 75
        assert paris.war_damage == pytest.approx(0.15, abs=0.001)
        assert paris.controller == "France"
        assert paris.terrain == "urban"
        assert paris.region_type == "capital"


class TestRoundtripEconomyState:
    """Full roundtrip preserves economy state."""

    def test_preserves_economy(self, test_save_dir, modified_world):
        filepath = test_save_dir / "economy_test.json"
        save_game(modified_world, filepath=filepath)

        result = load_game(filepath)
        assert result["success"]
        w = result["world"]
        assert w.nation_bankruptcy_turns.get("Britain") == 2
        assert w.admin_actions_remaining == 1


class TestRoundtripTransientData:
    """Transient per-turn data across a save/load round trip.

    Most of it is cleared; five fields are deliberate NON-clears, each
    documented at the site in `save_manager.load_game` with the mechanic it
    is load-bearing for.
    """

    def test_transient_cleared(self, test_save_dir, world):
        world.battles_this_turn = [{"type": "battle"}]
        ney = world.get_marshal("Ney")
        if ney:
            ney.in_combat_this_turn = True

        filepath = test_save_dir / "transient_test.json"
        save_game(world, filepath=filepath)
        result = load_game(filepath)

        assert result["success"]
        w = result["world"]
        # See the REV-F1 flip note in TestLoadGameRestoresState: the battle
        # record is restored, not wiped, so the charge's once-per-pair gate
        # survives a mid-turn save/load.
        assert w.battles_this_turn == [{"type": "battle"}]
        loaded_ney = w.get_marshal("Ney")
        if loaded_ney:
            # See the flip note in TestLoadGameRestoresState: the combat flag
            # is restored, not wiped, so the idle clock survives a mid-turn
            # save/load.
            assert loaded_ney.in_combat_this_turn is True


# ============================================================================
# BACKWARD COMPATIBILITY TESTS
# ============================================================================

class TestBackwardCompat:
    """Old/malformed save files still load."""

    def test_missing_metadata_rejected_as_old_format(self, test_save_dir, world):
        """Save file with no metadata key is rejected (defaults to format_version 1 < current)."""
        filepath = test_save_dir / "no_meta.json"
        data = {"world_state": world.to_dict()}
        with open(filepath, 'w') as f:
            json.dump(data, f)

        result = load_game(filepath)
        assert result["success"] is False
        assert "incompatible" in result["message"].lower()

    def test_old_format_version_rejected(self, test_save_dir, world):
        """Save with old format_version is rejected (13-region map incompatible)."""
        filepath = test_save_dir / "old_version.json"
        data = {
            "metadata": {"format_version": 0, "save_name": "Old"},
            "world_state": world.to_dict()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)

        result = load_game(filepath)
        assert result["success"] is False
        assert "incompatible" in result["message"].lower()

    def test_pre_cutover_v2_save_rejected_with_clear_message(self, test_save_dir, world):
        """DEF-2 (Map Slice 5): a 19-region-era save (format v2) fails with a
        clear versioned message — no crash, no silent load of stale region keys."""
        filepath = test_save_dir / "pre_cutover.json"
        data = {
            "metadata": {"format_version": 2, "save_name": "Pre-Cutover"},
            "world_state": world.to_dict()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)

        result = load_game(filepath)
        assert result["success"] is False
        assert result["world"] is None
        assert "incompatible" in result["message"].lower()
        # The message is versioned: names both the save's format and the current one.
        assert "v2" in result["message"]
        assert f"v{FORMAT_VERSION}" in result["message"]

    def test_extra_unknown_fields_ignored(self, test_save_dir, world):
        """Save file with extra keys still loads."""
        filepath = test_save_dir / "extra_fields.json"
        world_dict = world.to_dict()
        world_dict["some_future_field"] = "some_value"
        world_dict["another_new_thing"] = 42
        data = {
            "metadata": {"format_version": FORMAT_VERSION, "save_name": "Extra"},
            "world_state": world_dict
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)

        result = load_game(filepath)
        assert result["success"]
        # World loaded fine even with unknown fields

    def test_missing_world_state_fields_get_defaults(self, test_save_dir, world):
        """Missing fields in saved world_state get default values."""
        filepath = test_save_dir / "missing_fields.json"
        world_dict = world.to_dict()
        # Remove some fields that have defaults
        world_dict.pop("nation_bankruptcy_turns", None)
        world_dict.pop("admin_actions_remaining", None)
        world_dict.pop("gold_spent_this_turn", None)
        data = {
            "metadata": {"format_version": FORMAT_VERSION},
            "world_state": world_dict
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)

        result = load_game(filepath)
        assert result["success"]
        w = result["world"]
        # Fields should have their defaults
        assert isinstance(w.nation_bankruptcy_turns, dict)
        assert w.admin_actions_remaining >= 0


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

class TestApiEndpoints:
    """Test the save/load API endpoints via FastAPI test client."""

    @pytest.fixture
    def client(self, test_save_dir):
        """Create a FastAPI test client with patched save dir."""
        from fastapi.testclient import TestClient

        # Patch SAVE_DIR before importing app
        with patch("backend.save_manager.SAVE_DIR", test_save_dir):
            from backend.main import app, world
            client = TestClient(app)
            yield client, world

    def test_post_save_returns_success(self, client):
        test_client, world = client
        response = test_client.post("/save", json={"save_name": "API Test"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Game saved" in data["message"]

    def test_post_load_replaces_world(self, test_save_dir, world):
        """Load via load_game replaces world state."""
        filepath = test_save_dir / "load_test.json"
        with patch("backend.save_manager.SAVE_DIR", test_save_dir):
            save_game(world, save_name="Load Test", filepath=filepath)

        # Modify world
        world.current_turn = 99

        # Load
        with patch("backend.save_manager.SAVE_DIR", test_save_dir):
            result = load_game(filepath)
        assert result["success"] is True
        assert result["world"].current_turn == 1  # Original turn

    def test_get_saves_returns_list(self, client, test_save_dir):
        test_client, world = client

        with patch("backend.save_manager.SAVE_DIR", test_save_dir):
            save_game(world, save_name="List Test", filepath=test_save_dir / "list_test.json")

        response = test_client.get("/saves")
        assert response.status_code == 200
        data = response.json()
        assert "saves" in data
        assert isinstance(data["saves"], list)

    def test_post_load_bad_filename(self, client):
        test_client, world = client
        response = test_client.post("/load", json={"filename": "nonexistent.json"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()


# ============================================================================
# EXECUTOR INTEGRATION TESTS
# ============================================================================

class TestSaveLoadCommands:
    """Test save/load as in-game terminal commands."""

    def test_save_command_via_executor(self, test_save_dir, world):
        """'save' command creates a save file."""
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        game_state = {"world": world}

        parsed = {
            "success": True,
            "command": {
                "action": "meta_command",
                "raw_command": "save My Campaign",
                "marshal": None,
                "target": None,
                "confidence": 1.0,
            },
            "raw_input": "save My Campaign",
            "mode": "mock",
        }

        with patch("backend.save_manager.SAVE_DIR", test_save_dir):
            result = executor.execute(parsed, game_state)

        assert result["success"] is True
        assert "Game saved" in result["message"]

    def test_load_command_shows_saves(self, test_save_dir, world):
        """'load' command lists available saves."""
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        game_state = {"world": world}

        # Create a save first
        with patch("backend.save_manager.SAVE_DIR", test_save_dir):
            save_game(world, save_name="Test", filepath=test_save_dir / "test.json")

        parsed = {
            "success": True,
            "command": {
                "action": "meta_command",
                "raw_command": "load",
                "marshal": None,
                "target": None,
                "confidence": 1.0,
            },
            "raw_input": "load",
            "mode": "mock",
        }

        with patch("backend.save_manager.SAVE_DIR", test_save_dir):
            result = executor.execute(parsed, game_state)

        assert result["success"] is True
        assert "test.json" in result["message"]
        assert result.get("show_load_dialog") is True


class TestMockParserSaveLoad:
    """Test that mock parser correctly identifies save/load commands."""

    def test_save_parsed_as_meta_command(self):
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("save My Campaign")
        assert result.action == "meta_command"
        assert result.raw_command == "save My Campaign"

    def test_load_parsed_as_meta_command(self):
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("load")
        assert result.action == "meta_command"
        assert result.raw_command == "load"

    def test_save_without_name_parsed(self):
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("save")
        assert result.action == "meta_command"

    def test_load_game_not_confused_with_other_commands(self):
        """'load' should not be parsed as a military action."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("load")
        assert result.action == "meta_command"
        assert result.confidence == 1.0


# ============================================================================
# AUTOSAVE INTEGRATION TEST
# ============================================================================

class TestAutosaveIntegration:
    """Autosave fires at end of turn processing."""

    def test_autosave_called_in_end_turn(self, test_save_dir, world):
        """_execute_end_turn triggers autosave."""
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        game_state = {"world": world}

        with patch("backend.save_manager.SAVE_DIR", test_save_dir):
            result = executor._execute_end_turn({}, game_state)

        assert result["success"] is True
        # Autosave file should exist
        assert (test_save_dir / AUTOSAVE_FILENAME).exists()

        # Verify autosave content
        with open(test_save_dir / AUTOSAVE_FILENAME, 'r') as f:
            data = json.load(f)
        assert data["metadata"]["turn"] == world.current_turn
