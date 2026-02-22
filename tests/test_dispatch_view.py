"""
Test suite for Dispatch Re-read Screen backend (Session A)

Tests:
- last_morning_dispatch stored on WorldState after build_morning_dispatch()
- last_morning_dispatch serialization roundtrip (to_dict -> from_dict)
- GET /dispatch returns stored dispatch
- GET /dispatch returns empty dict when no dispatch built yet
- No-float enforcement on dispatch endpoint response
"""

import json
import math
import pytest

from backend.models.world_state import WorldState
from backend.game_logic.dispatch import build_morning_dispatch


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a standard WorldState for testing."""
    return WorldState(player_nation="France")


def _assert_no_floats(obj, path="root"):
    """Recursively assert no float values exist in the data structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            _assert_no_floats(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _assert_no_floats(v, f"{path}[{i}]")
    elif isinstance(obj, float):
        pytest.fail(f"Float found at {path}: {obj}")
    elif isinstance(obj, bool):
        pass  # bools are fine


# ════════════════════════════════════════════════════════════════════════════════
# TEST: last_morning_dispatch stored after build
# ════════════════════════════════════════════════════════════════════════════════

def test_dispatch_stored_on_world():
    """build_morning_dispatch() stores the dispatch dict on world.last_morning_dispatch."""
    world = _make_world()
    assert world.last_morning_dispatch == {}

    dispatch = build_morning_dispatch(world)

    assert world.last_morning_dispatch is dispatch
    assert world.last_morning_dispatch != {}
    assert "turn" in world.last_morning_dispatch
    assert "situation" in world.last_morning_dispatch
    assert "marshals" in world.last_morning_dispatch
    assert "intelligence" in world.last_morning_dispatch
    assert "berthier_note" in world.last_morning_dispatch


# ════════════════════════════════════════════════════════════════════════════════
# TEST: Serialization roundtrip
# ════════════════════════════════════════════════════════════════════════════════

def test_dispatch_serialization_roundtrip():
    """last_morning_dispatch survives to_dict -> from_dict."""
    world = _make_world()
    build_morning_dispatch(world)

    data = world.to_dict()
    assert "last_morning_dispatch" in data
    assert data["last_morning_dispatch"]["turn"] == int(world.current_turn)

    restored = WorldState.from_dict(data)
    assert restored.last_morning_dispatch == world.last_morning_dispatch


def test_dispatch_serialization_empty():
    """Empty dispatch (no build yet) survives serialization."""
    world = _make_world()
    assert world.last_morning_dispatch == {}

    data = world.to_dict()
    assert data["last_morning_dispatch"] == {}

    restored = WorldState.from_dict(data)
    assert restored.last_morning_dispatch == {}


def test_dispatch_serialization_backward_compat():
    """Old saves without last_morning_dispatch field load cleanly."""
    world = _make_world()
    data = world.to_dict()
    del data["last_morning_dispatch"]

    restored = WorldState.from_dict(data)
    assert restored.last_morning_dispatch == {}


# ════════════════════════════════════════════════════════════════════════════════
# TEST: GET /dispatch endpoint
# ════════════════════════════════════════════════════════════════════════════════

def test_dispatch_endpoint_returns_stored():
    """GET /dispatch returns the stored dispatch when one exists."""
    from fastapi.testclient import TestClient
    from backend.main import app, game_state

    world = game_state["world"]
    build_morning_dispatch(world)

    client = TestClient(app)
    response = client.get("/dispatch")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "dispatch" in data
    assert data["dispatch"]["turn"] == int(world.current_turn)
    assert "situation" in data["dispatch"]
    assert "marshals" in data["dispatch"]


def test_dispatch_endpoint_empty_when_no_build():
    """GET /dispatch returns empty dict when no dispatch has been built."""
    from fastapi.testclient import TestClient
    from backend.main import app, game_state

    world = game_state["world"]
    world.last_morning_dispatch = {}

    client = TestClient(app)
    response = client.get("/dispatch")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["dispatch"] == {}


# ════════════════════════════════════════════════════════════════════════════════
# TEST: No-float enforcement
# ════════════════════════════════════════════════════════════════════════════════

def test_dispatch_no_floats():
    """Dispatch dict contains no float values (Godot crashes on floats)."""
    world = _make_world()
    dispatch = build_morning_dispatch(world)
    _assert_no_floats(dispatch)


def test_dispatch_no_floats_with_tactical_events():
    """Dispatch with tactical events also has no floats."""
    world = _make_world()
    events = [
        {"type": "attrition", "message": "Ney lost troops", "severity": "warning",
         "nation": "France", "region": "Paris"},
        {"type": "construction_complete", "message": "Stables built",
         "severity": "good", "nation": "France", "region": "Paris"},
    ]
    dispatch = build_morning_dispatch(world, tactical_events=events)
    _assert_no_floats(dispatch)
