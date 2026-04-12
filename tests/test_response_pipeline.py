"""
R4 Response Pipeline — Characterization + Enforcement tests.

Tests for build_base_response() and _build_result_response() helpers,
plus integration tests verifying all POST endpoints include standard
response fields (diplomatic top-bar, popup passthroughs, notifications).

Session 4 of Architecture Refactoring Plan.
"""

import pytest
from fastapi.testclient import TestClient


# ════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    from backend.main import app
    return TestClient(app)


@pytest.fixture
def fresh_world():
    """Reset world state before each test and return the world."""
    import backend.main as main_module
    from backend.models.world_state import WorldState
    main_module.world = WorldState(player_nation="France")
    main_module.game_state = {"world": main_module.world}
    return main_module.world


@pytest.fixture
def main_module():
    """Access to main module for direct function calls."""
    import backend.main as m
    return m


# ════════════════════════════════════════════════════════════════════════════
# REQUIRED KEYS — structural contract for all gameplay responses
# ════════════════════════════════════════════════════════════════════════════

# Keys that MUST appear in every gameplay POST response
BASE_REQUIRED_KEYS = {
    "success", "message", "game_state", "action_summary",
}

# Diplomatic top-bar keys — MUST appear in every gameplay response
DIPLOMATIC_TOPBAR_KEYS = {
    "diplomatic_points", "max_diplomatic_points",
    "talleyrand_state", "talleyrand_mission_summary",
    "threat_level", "coalition_brewing",
    "coalition_brewing_turns", "pending_envoy_count",
}

# Popup passthrough keys — MUST appear (value may be None)
POPUP_KEYS = {
    "coalition_popup", "diplomatic_sabotage",
    "vassal_rebellion_imminent",
    "diplomatic_objection", "incoming_proposal",
    "alliance_paradox_popup",
}

ALL_STANDARD_KEYS = BASE_REQUIRED_KEYS | DIPLOMATIC_TOPBAR_KEYS | POPUP_KEYS | {"active_wars"}


# ════════════════════════════════════════════════════════════════════════════
# UNIT TESTS: build_base_response()
# ════════════════════════════════════════════════════════════════════════════

class TestBuildBaseResponse:
    """Unit tests for the centralized response builder."""

    def test_includes_all_required_keys(self, fresh_world, main_module):
        """Builder must include every standard key."""
        response = main_module.build_base_response(fresh_world)
        for key in ALL_STANDARD_KEYS:
            assert key in response, f"Missing required key: {key}"

    def test_success_default_true(self, fresh_world, main_module):
        response = main_module.build_base_response(fresh_world)
        assert response["success"] is True

    def test_success_false(self, fresh_world, main_module):
        response = main_module.build_base_response(fresh_world, success=False)
        assert response["success"] is False

    def test_message_passthrough(self, fresh_world, main_module):
        response = main_module.build_base_response(fresh_world, message="Test message")
        assert response["message"] == "Test message"

    def test_events_default_empty_list(self, fresh_world, main_module):
        response = main_module.build_base_response(fresh_world)
        assert response["events"] == []

    def test_events_passthrough(self, fresh_world, main_module):
        events = [{"type": "combat", "text": "Battle!"}]
        response = main_module.build_base_response(fresh_world, events=events)
        assert response["events"] == events

    def test_extra_fields_merged(self, fresh_world, main_module):
        response = main_module.build_base_response(
            fresh_world, battle_report={"winner": "France"}, custom_key=42)
        assert response["battle_report"] == {"winner": "France"}
        assert response["custom_key"] == 42

    def test_game_state_present(self, fresh_world, main_module):
        response = main_module.build_base_response(fresh_world)
        assert isinstance(response["game_state"], dict)
        assert "turn" in response["game_state"]

    def test_action_summary_present(self, fresh_world, main_module):
        response = main_module.build_base_response(fresh_world)
        assert isinstance(response["action_summary"], dict)

    def test_all_numeric_fields_are_int(self, fresh_world, main_module):
        """Golden Rule #2: All numbers to Godot must be int."""
        response = main_module.build_base_response(fresh_world)
        int_fields = ["diplomatic_points", "max_diplomatic_points",
                      "threat_level", "pending_envoy_count"]
        for field in int_fields:
            assert isinstance(response[field], int), f"{field} must be int, got {type(response[field])}"

    def test_coalition_brewing_false_by_default(self, fresh_world, main_module):
        response = main_module.build_base_response(fresh_world)
        assert response["coalition_brewing"] is False
        assert response["coalition_brewing_turns"] is None

    def test_coalition_brewing_true_when_active(self, fresh_world, main_module):
        fresh_world.coalition_brewing = {"turns_remaining": 3, "members": []}
        response = main_module.build_base_response(fresh_world)
        assert response["coalition_brewing"] is True
        assert response["coalition_brewing_turns"] == 3

    def test_popup_keys_all_none_when_no_popups(self, fresh_world, main_module):
        """All popup keys should be present with None value when no popups are set."""
        response = main_module.build_base_response(fresh_world)
        for key in POPUP_KEYS:
            assert key in response, f"Missing popup key: {key}"
            assert response[key] is None, f"Popup key {key} should be None, got {response[key]}"

    def test_popup_passthrough_included(self, fresh_world, main_module):
        """When a popup is set on world, it should appear in response."""
        fresh_world.coalition_popup = {"type": "test_coalition"}
        response = main_module.build_base_response(fresh_world)
        assert response["coalition_popup"] == {"type": "test_coalition"}
        # Should be cleared from world after reading
        assert fresh_world.coalition_popup is None

    def test_active_wars_always_included(self, fresh_world, main_module):
        response = main_module.build_base_response(fresh_world)
        assert "active_wars" in response

    def test_notifications_included_when_pending(self, fresh_world, main_module):
        """Notifications should be included when pending."""
        fresh_world.notifications.add({"id": "test_notif", "text": "Test!", "priority": "NORMAL"})
        response = main_module.build_base_response(fresh_world)
        assert "notifications" in response
        assert len(response["notifications"]) > 0

    def test_no_notifications_key_when_none_pending(self, fresh_world, main_module):
        """Notifications key should not appear when nothing is pending."""
        response = main_module.build_base_response(fresh_world)
        assert "notifications" not in response

    def test_talleyrand_state_label(self, fresh_world, main_module):
        """Talleyrand state should be a trust label string."""
        response = main_module.build_base_response(fresh_world)
        assert response["talleyrand_state"] in ["Divine Right", "Commanding", "Respected", "Questionable", "Emperor in Name Only", "UNKNOWN"]

    def test_talleyrand_mission_summary_default(self, fresh_world, main_module):
        response = main_module.build_base_response(fresh_world)
        assert isinstance(response["talleyrand_mission_summary"], str)


class TestBuildResultResponse:
    """Tests for _build_result_response() — executor result → API response."""

    def test_strips_new_state(self, fresh_world, main_module):
        """new_state (circular refs) must be stripped from executor results."""
        result = {"success": True, "message": "Done", "new_state": fresh_world}
        response = main_module._build_result_response(result, fresh_world)
        assert "new_state" not in response

    def test_preserves_executor_fields(self, fresh_world, main_module):
        """Executor-specific fields (state, choices, etc.) must pass through."""
        result = {
            "success": True,
            "message": "Objection!",
            "state": "awaiting_player_choice",
            "marshal": "Ney",
            "choices": ["trust", "insist"],
        }
        response = main_module._build_result_response(result, fresh_world)
        assert response["state"] == "awaiting_player_choice"
        assert response["marshal"] == "Ney"
        assert response["choices"] == ["trust", "insist"]

    def test_includes_standard_keys(self, fresh_world, main_module):
        """Result response must include all standard keys."""
        result = {"success": True, "message": "Done"}
        response = main_module._build_result_response(result, fresh_world)
        for key in ALL_STANDARD_KEYS:
            assert key in response, f"Missing standard key: {key}"

    def test_includes_diplomatic_topbar(self, fresh_world, main_module):
        """Result response must include diplomatic top-bar fields."""
        result = {"success": True, "message": "Done"}
        response = main_module._build_result_response(result, fresh_world)
        for key in DIPLOMATIC_TOPBAR_KEYS:
            assert key in response, f"Missing diplomatic key: {key}"

    def test_executor_success_overrides_default(self, fresh_world, main_module):
        result = {"success": False, "message": "Failed"}
        response = main_module._build_result_response(result, fresh_world)
        assert response["success"] is False

    def test_executor_events_preserved(self, fresh_world, main_module):
        result = {"success": True, "message": "Done",
                  "events": [{"type": "combat"}]}
        response = main_module._build_result_response(result, fresh_world)
        assert response["events"] == [{"type": "combat"}]


# ════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS: Endpoint response shapes
# ════════════════════════════════════════════════════════════════════════════

class TestCommandEndpointDiplomaticFields:
    """Verify /command responses include diplomatic top-bar fields."""

    def test_scout_has_diplomatic_fields(self, client, fresh_world):
        response = client.post("/command", json={"command": "Ney, scout Belgium"})
        data = response.json()
        for key in DIPLOMATIC_TOPBAR_KEYS:
            assert key in data, f"/command scout missing: {key}"

    def test_empty_command_has_diplomatic_fields(self, client, fresh_world):
        response = client.post("/command", json={"command": ""})
        data = response.json()
        for key in DIPLOMATIC_TOPBAR_KEYS:
            assert key in data, f"/command empty missing: {key}"

    def test_empty_command_has_popup_keys(self, client, fresh_world):
        response = client.post("/command", json={"command": ""})
        data = response.json()
        for key in POPUP_KEYS:
            assert key in data, f"/command empty missing popup key: {key}"

    def test_invalid_command_has_diplomatic_fields(self, client, fresh_world):
        response = client.post("/command", json={"command": "xyzzy foobar"})
        data = response.json()
        for key in DIPLOMATIC_TOPBAR_KEYS:
            assert key in data, f"/command invalid missing: {key}"

    def test_game_over_has_diplomatic_fields(self, client, fresh_world):
        fresh_world.game_over = True
        fresh_world.victory = False
        response = client.post("/command", json={"command": "Ney, attack"})
        data = response.json()
        for key in DIPLOMATIC_TOPBAR_KEYS:
            assert key in data, f"/command game_over missing: {key}"


class TestOtherEndpointDiplomaticFields:
    """Verify non-/command POST endpoints include diplomatic top-bar fields."""

    def test_respond_to_objection_has_diplomatic_fields(self, client, fresh_world):
        """Objection response should include diplomatic fields (previously missing)."""
        # Set up a pending objection
        fresh_world.pending_objection = {
            "marshal": "Ney",
            "message": "Test objection",
            "severity": 0.5,
            "type": "major",
            "trigger": "reckless_attack",
            "original_order": {"action": "attack"},
        }
        response = client.post("/respond_to_objection", json={"choice": "trust"})
        data = response.json()
        for key in DIPLOMATIC_TOPBAR_KEYS:
            assert key in data, f"/respond_to_objection missing: {key}"

    def test_capture_choice_has_diplomatic_fields(self, client, fresh_world):
        """Capture choice should include diplomatic fields (previously missing)."""
        # Set up pending capture choice
        fresh_world.pending_capture_choice = {
            "region": "Belgium",
            "marshal": "Ney",
        }
        response = client.post("/capture_choice", json={"choice": "plunder"})
        data = response.json()
        # Even error responses should have diplomatic fields
        for key in DIPLOMATIC_TOPBAR_KEYS:
            assert key in data, f"/capture_choice missing: {key}"

    def test_respond_to_redemption_no_pending_has_diplomatic_fields(self, client, fresh_world):
        """Redemption 'no pending' response should include diplomatic fields."""
        response = client.post("/respond_to_redemption", json={"choice": "grant_autonomy"})
        data = response.json()
        for key in DIPLOMATIC_TOPBAR_KEYS:
            assert key in data, f"/respond_to_redemption missing: {key}"

    def test_glorious_charge_invalid_has_diplomatic_fields(self, client, fresh_world):
        """Glorious charge invalid choice should include diplomatic fields."""
        response = client.post("/respond_to_glorious_charge", json={"choice": "invalid"})
        data = response.json()
        for key in DIPLOMATIC_TOPBAR_KEYS:
            assert key in data, f"/respond_to_glorious_charge missing: {key}"

    def test_cancel_order_no_marshal_has_diplomatic_fields(self, client, fresh_world):
        """Cancel order with no marshal should include diplomatic fields."""
        response = client.post("/cancel_order", json={"marshal": ""})
        data = response.json()
        for key in DIPLOMATIC_TOPBAR_KEYS:
            assert key in data, f"/cancel_order missing: {key}"

    def test_diplomatic_dialogue_has_diplomatic_fields(self, client, fresh_world):
        """Diplomatic dialogue response should include diplomatic fields."""
        fresh_world.dialogue_manager.replace({
            "type": "incoming_proposal",
            "target_nation": "Prussia",
            "options": [{"label": "Accept", "value": "accept"}],
        })
        response = client.post("/respond_to_diplomatic_dialogue",
                               json={"choice": "accept"})
        data = response.json()
        for key in DIPLOMATIC_TOPBAR_KEYS:
            assert key in data, f"/respond_to_diplomatic_dialogue missing: {key}"

    def test_diplomatic_dialogue_safety_net_rejects_negative_result(self, client, fresh_world, main_module, monkeypatch):
        """Fallback proposal-result popup must not default rejected outcomes to ACCEPT."""
        fresh_world.dialogue_manager.replace({
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "options": [{"label": "Send", "action": "execute_proposal"}],
        })

        def _fake_handle(_choice, _game_state):
            fresh_world.dialogue_manager.pop()
            return {
                "success": True,
                "message": "Prussia has rejected our proposal.",
            }

        monkeypatch.setattr(main_module.executor, "handle_diplomatic_dialogue_response", _fake_handle)

        response = client.post("/respond_to_diplomatic_dialogue", json={"choice": 1})
        data = response.json()
        assert data["success"] is True
        assert data["proposal_result"] is not None
        assert data["proposal_result"]["outcome"] == "REJECT"
        assert data["proposal_result"]["target_nation"] == "Prussia"

    def test_conflict_alert_dismiss_does_not_spawn_proposal_result(self, client, fresh_world):
        """Local-planning dismissals must not leak into proposal-result popup fallback."""
        fresh_world.dialogue_manager.replace({
            "type": "conflict_alert",
            "target_nation": "Austria",
            "talleyrand_text": "This treaty conflicts with an existing alliance.",
            "options": [{"label": "Dismiss", "action": "dismiss"}],
            "context": {},
            "turn_created": int(fresh_world.current_turn),
            "blocking": False,
        })

        response = client.post("/respond_to_diplomatic_dialogue", json={"choice": 1})
        data = response.json()

        assert data["success"] is True
        assert data.get("proposal_result") is None
        assert fresh_world.proposal_result_popup is None

    def test_strategic_response_game_over_has_diplomatic_fields(self, client, fresh_world):
        """Strategic response game-over guard should include diplomatic fields."""
        fresh_world.game_over = True
        fresh_world.victory = False
        response = client.post("/strategic_response",
                               json={"marshal_name": "Ney", "response_type": "cannon_fire",
                                     "choice": "investigate"})
        data = response.json()
        for key in DIPLOMATIC_TOPBAR_KEYS:
            assert key in data, f"/strategic_response game_over missing: {key}"


class TestNotificationInclusion:
    """Verify notifications are included in responses when pending."""

    def test_command_includes_notifications(self, client, fresh_world):
        fresh_world.notifications.add({"id": "test", "text": "Test notification", "priority": "NORMAL"})
        response = client.post("/command", json={"command": "Ney, scout Belgium"})
        data = response.json()
        assert "notifications" in data

    def test_no_notifications_when_empty(self, client, fresh_world):
        response = client.post("/command", json={"command": "Ney, scout Belgium"})
        data = response.json()
        # notifications key may or may not be present when empty
        if "notifications" in data:
            assert isinstance(data["notifications"], list)


class TestPopupKeysPresence:
    """Verify popup keys are present in all gameplay responses."""

    def test_command_has_popup_keys(self, client, fresh_world):
        response = client.post("/command", json={"command": "Ney, scout Belgium"})
        data = response.json()
        for key in POPUP_KEYS:
            assert key in data, f"/command missing popup key: {key}"

    def test_objection_response_has_popup_keys(self, client, fresh_world):
        fresh_world.pending_objection = {
            "marshal": "Ney", "message": "Test", "severity": 0.5,
            "type": "major", "trigger": "reckless_attack",
            "original_order": {"action": "attack"},
        }
        response = client.post("/respond_to_objection", json={"choice": "trust"})
        data = response.json()
        for key in POPUP_KEYS:
            assert key in data, f"/respond_to_objection missing popup key: {key}"

    def test_capture_choice_has_popup_keys(self, client, fresh_world):
        fresh_world.pending_capture_choice = {"region": "Belgium", "marshal": "Ney"}
        response = client.post("/capture_choice", json={"choice": "plunder"})
        data = response.json()
        for key in POPUP_KEYS:
            assert key in data, f"/capture_choice missing popup key: {key}"


class TestActiveWarsPresence:
    """Verify active_wars is in all gameplay responses."""

    def test_command_has_active_wars(self, client, fresh_world):
        response = client.post("/command", json={"command": "Ney, scout Belgium"})
        data = response.json()
        assert "active_wars" in data

    def test_empty_command_has_active_wars(self, client, fresh_world):
        response = client.post("/command", json={"command": ""})
        data = response.json()
        assert "active_wars" in data

    def test_objection_response_has_active_wars(self, client, fresh_world):
        fresh_world.pending_objection = {
            "marshal": "Ney", "message": "Test", "severity": 0.5,
            "type": "major", "trigger": "reckless_attack",
            "original_order": {"action": "attack"},
        }
        response = client.post("/respond_to_objection", json={"choice": "trust"})
        data = response.json()
        assert "active_wars" in data
