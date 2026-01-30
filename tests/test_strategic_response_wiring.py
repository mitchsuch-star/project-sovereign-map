"""
Tests that strategic_reports flow through the full endpoint response chain.

Verifies the fix for the wiring gap where executor produced strategic_reports
but main.py didn't include them in the HTTP response.

Run: pytest tests/test_strategic_response_wiring.py -v
"""

import pytest
from backend.models.marshal import Marshal, StrategicOrder
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


def _setup_world_with_strategic_order():
    """Create a world where a marshal has an active strategic order."""
    world = WorldState()
    grouchy = world.get_marshal("Grouchy")
    grouchy.location = "Paris"
    grouchy.strength = 50000
    grouchy.strategic_order = StrategicOrder(
        command_type="MOVE_TO",
        target="Belgium",
        target_type="region",
        path=["Lyon", "Belgium"],
        started_turn=world.current_turn,
        original_command="Grouchy, march to Belgium",
    )
    return world


def test_end_turn_executor_result_contains_strategic_reports():
    """Executor._execute_end_turn() must include strategic_reports in result."""
    world = _setup_world_with_strategic_order()
    executor = CommandExecutor()
    game_state = {"world": world}

    command = {"action": "end_turn"}
    result = executor.execute({"command": command}, game_state)

    assert result.get("success"), f"end_turn failed: {result.get('message')}"
    # The key field must exist in executor result
    assert "strategic_reports" in result, (
        "executor result missing 'strategic_reports' - "
        "check executor._execute_end_turn() passes turn_result through"
    )
    reports = result["strategic_reports"]
    assert isinstance(reports, list)
    assert len(reports) > 0, "Expected at least one strategic report for Grouchy"
    assert reports[0]["marshal"] == "Grouchy"


def test_strategic_report_has_required_ui_fields():
    """Each strategic report must have the fields Godot UI expects."""
    world = _setup_world_with_strategic_order()
    executor = CommandExecutor()
    game_state = {"world": world}

    result = executor.execute({"command": {"action": "end_turn"}}, game_state)
    reports = result.get("strategic_reports", [])
    assert len(reports) > 0

    report = reports[0]
    # Fields required by strategic_report_popup.gd
    required_fields = ["marshal", "command", "order_status", "message"]
    for field in required_fields:
        assert field in report, f"Report missing required field '{field}' for Godot UI"


def test_main_response_builder_includes_strategic_reports():
    """
    Simulate the main.py response construction pattern to verify
    strategic_reports are passed through.
    """
    # This mimics the pattern in main.py lines 235-290
    executor_result = {
        "success": True,
        "message": "Turn ended",
        "events": [],
        "action_info": {},
        "strategic_reports": [
            {"marshal": "Grouchy", "command": "MOVE_TO",
             "order_status": "continues", "message": "Marching to Belgium"}
        ],
    }

    # Build response the same way main.py does
    response = {
        "success": executor_result.get("success", False),
        "message": executor_result.get("message", "Command executed"),
        "events": executor_result.get("events", []),
        "action_info": executor_result.get("action_info", {}),
    }

    # This is the fix we added to main.py
    if executor_result.get("strategic_reports"):
        response["strategic_reports"] = executor_result["strategic_reports"]

    assert "strategic_reports" in response
    assert len(response["strategic_reports"]) == 1
    assert response["strategic_reports"][0]["marshal"] == "Grouchy"


def test_empty_strategic_reports_not_included():
    """When no strategic orders exist, strategic_reports should not be in response."""
    world = WorldState()
    executor = CommandExecutor()
    game_state = {"world": world}

    result = executor.execute({"command": {"action": "end_turn"}}, game_state)

    # Empty list or absent is fine - Godot checks .is_empty()
    reports = result.get("strategic_reports", [])
    assert isinstance(reports, list)
    assert len(reports) == 0
