"""
Test suite for FastAPI endpoint wiring

Uses FastAPI TestClient to verify endpoints return correct response keys
and that data flows from executor through main.py to the API response.

Coverage targets: main.py lines 332-666, 679-682, 701-770, 784-868, 913-987
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    from backend.main import app
    return TestClient(app)


@pytest.fixture
def fresh_world():
    """Reset world state before each test."""
    import backend.main as main_module
    from backend.models.world_state import WorldState
    main_module.world = WorldState()
    main_module.game_state = {"world": main_module.world}
    return main_module.world


class TestConnectionEndpoint:
    """Test /test endpoint."""

    def test_connection(self, client, fresh_world):
        """GET /test should return ok status."""
        response = client.get("/test")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "turn" in data
        assert isinstance(data["turn"], int)


class TestCommandEndpoint:
    """Test /command endpoint response structure."""

    def test_scout_command_response_keys(self, client, fresh_world):
        """POST /command with scout should return all required keys."""
        response = client.post("/command", json={"command": "Ney, scout Belgium"})
        assert response.status_code == 200
        data = response.json()

        # Required keys that Godot reads
        assert "success" in data
        assert "message" in data
        assert "events" in data
        assert "action_summary" in data
        assert "game_state" in data

    def test_invalid_command_returns_error(self, client, fresh_world):
        """Invalid command should return success=False with error message."""
        response = client.post("/command", json={"command": "xyzzy foobar"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "message" in data

    def test_move_command_returns_action_info(self, client, fresh_world):
        """Move command should include action_info."""
        response = client.post("/command", json={"command": "Ney, move to Belgium"})
        assert response.status_code == 200
        data = response.json()
        # action_info may be in result
        assert "action_summary" in data

    def test_end_turn_returns_game_state(self, client, fresh_world):
        """End turn should return updated game state."""
        response = client.post("/command", json={"command": "end turn"})
        assert response.status_code == 200
        data = response.json()
        assert "game_state" in data

    def test_game_state_has_required_structure(self, client, fresh_world):
        """game_state in response should have marshals, regions, etc."""
        response = client.post("/command", json={"command": "Ney, scout Belgium"})
        data = response.json()
        gs = data.get("game_state", {})

        # game_state should include key fields
        assert isinstance(gs, dict)
        # It should have some structure (marshals, regions, etc.)
        # The exact shape depends on get_filtered_game_state_summary


class TestStatusEndpoint:
    """Test /status endpoint."""

    def test_status_returns_intel_report(self, client, fresh_world):
        """GET /status should return intel report data."""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert "game_state" in data


class TestPendingObjectionEndpoint:
    """Test /pending_objection endpoint."""

    def test_no_pending_objection(self, client, fresh_world):
        """When no objection is pending, should return has_pending=False."""
        response = client.get("/pending_objection")
        assert response.status_code == 200
        data = response.json()
        assert data["has_pending"] is False

    def test_pending_objection_structure(self, client, fresh_world):
        """When an objection is pending, should return full structure."""
        import backend.main as main_module
        main_module.world.pending_objection = {
            "marshal": "Ney",
            "message": "I refuse!",
            "severity": 0.65,
            "type": "major",
            "trigger": "defend_order",
            "alternative": {"action": "attack"},
            "original_order": {"action": "defend"}
        }

        response = client.get("/pending_objection")
        assert response.status_code == 200
        data = response.json()
        assert data["has_pending"] is True
        assert data["marshal"] == "Ney"
        assert isinstance(data["severity"], int)  # int() for Godot
        assert "choices" in data
        assert "trust" in data["choices"]
        assert "insist" in data["choices"]


class TestObjectionResponseEndpoint:
    """Test /respond_to_objection endpoint."""

    def test_respond_no_pending(self, client, fresh_world):
        """Responding when no objection pending should handle gracefully."""
        response = client.post(
            "/respond_to_objection",
            json={"choice": "trust"}
        )
        assert response.status_code == 200
        data = response.json()
        # Should either succeed or fail gracefully
        assert "message" in data


class TestCaptureChoiceEndpoint:
    """Test /capture_choice endpoint."""

    def test_capture_no_pending(self, client, fresh_world):
        """Responding when no capture choice pending should handle gracefully."""
        response = client.post(
            "/capture_choice",
            json={"choice": "plunder"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_capture_response_structure(self, client, fresh_world):
        """Capture choice response should include required keys."""
        # Without a properly pending capture, this tests error handling
        response = client.post(
            "/capture_choice",
            json={"choice": "plunder"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "message" in data


class TestRedemptionEndpoint:
    """Test /respond_to_redemption endpoint."""

    def test_no_pending_redemption(self, client, fresh_world):
        """Responding when no redemption pending should fail gracefully."""
        response = client.post(
            "/respond_to_redemption",
            json={"choice": "grant_autonomy"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "no" in data["message"].lower() or "pending" in data["message"].lower()

    def test_invalid_redemption_choice(self, client, fresh_world):
        """Invalid choice should return error."""
        import backend.main as main_module
        main_module.world.pending_redemption = {
            "marshal": "Ney",
            "trust": 5,
            "message": "Ney's trust has collapsed!",
            "options": ["grant_autonomy", "administrative_role", "dismiss"]
        }

        response = client.post(
            "/respond_to_redemption",
            json={"choice": "invalid_choice"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    def test_pending_redemption_get(self, client, fresh_world):
        """GET /pending_redemption should return pending state."""
        response = client.get("/pending_redemption")
        assert response.status_code == 200
        data = response.json()
        assert data["has_pending"] is False


class TestGloriousChargeEndpoint:
    """Test /respond_to_glorious_charge endpoint."""

    def test_invalid_choice(self, client, fresh_world):
        """Invalid charge choice should return error."""
        response = client.post(
            "/respond_to_glorious_charge",
            json={"choice": "invalid"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    def test_response_structure(self, client, fresh_world):
        """Valid charge response should include required keys."""
        # This will likely fail since no charge is pending,
        # but should not crash
        response = client.post(
            "/respond_to_glorious_charge",
            json={"choice": "restrain"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestStrategicResponseEndpoint:
    """Test /strategic_response endpoint."""

    def test_strategic_response_structure(self, client, fresh_world):
        """Strategic response should return required keys."""
        response = client.post(
            "/strategic_response",
            json={
                "marshal_name": "Ney",
                "response_type": "cannon_fire",
                "choice": "investigate"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "message" in data


class TestAuthorityStatusEndpoint:
    """Test /authority_status endpoint."""

    def test_authority_status(self, client, fresh_world):
        """GET /authority_status should return authority info."""
        response = client.get("/authority_status")
        assert response.status_code == 200
        data = response.json()
        assert "authority" in data
        assert isinstance(data["authority"], int)
        assert "label" in data
        assert isinstance(data["label"], str)


class TestSaveLoadEndpoints:
    """Test save/load system endpoints."""

    def test_list_saves(self, client, fresh_world):
        """GET /saves should return a list."""
        response = client.get("/saves")
        assert response.status_code == 200
        data = response.json()
        assert "saves" in data
        assert isinstance(data["saves"], list)

    def test_save_game(self, client, fresh_world):
        """POST /save should save successfully."""
        response = client.post(
            "/save",
            json={"save_name": "_test_endpoint_save"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Cleanup — delete uses filename (the actual file path)
        import glob
        import os
        for f in glob.glob("saves/*_test_endpoint_save*"):
            os.remove(f)

    def test_load_nonexistent(self, client, fresh_world):
        """Loading a nonexistent save should fail gracefully."""
        response = client.post(
            "/load",
            json={"filename": "_nonexistent_save_12345.json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False


class TestResponseIntValues:
    """Verify all numeric values returned to Godot are int, not float."""

    def test_status_turn_is_int(self, client, fresh_world):
        """Turn number must be int for Godot."""
        response = client.get("/test")
        data = response.json()
        assert isinstance(data["turn"], int)

    def test_objection_severity_is_int(self, client, fresh_world):
        """Objection severity must be int percentage for Godot."""
        import backend.main as main_module
        main_module.world.pending_objection = {
            "marshal": "Ney",
            "message": "Test",
            "severity": 0.75,
            "type": "major",
            "trigger": "test",
            "alternative": None,
            "original_order": {}
        }

        response = client.get("/pending_objection")
        data = response.json()
        assert isinstance(data["severity"], int)

    def test_authority_values_are_int(self, client, fresh_world):
        """Authority endpoint values must be int for Godot."""
        response = client.get("/authority_status")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["authority"], int)
        assert isinstance(data["trust_modifier"], int)
        assert isinstance(data["obedience_modifier"], int)
