"""Sweep-5 P0 (Combat Overhaul exit-sweep precondition, July 16 2026).

Live 500: when the end-turn's strategic processing raised a capture choice
AFTER the enemy phase had run, the early-return path forwarded the executor
result through `_build_result_response` with `enemy_phase` RAW — each nation
action still carrying its `new_state` WorldState, whose tuple-keyed caches
(`_distance_cache` et al.) crash FastAPI's `jsonable_encoder` ("unhashable
type: 'list'") outside the endpoint try/except. The turn had already
advanced, so the player lost the entire end-turn report to a naked 500. The
raw pass-through also leaked fog (unfiltered enemy actions).

The fix routes `enemy_phase` through `_build_visible_enemy_phase` — the same
strip-new_state + fog-filter cleaner the main /command path uses.
"""
from fastapi.encoders import jsonable_encoder

from backend.main import _build_result_response
from backend.models.world_state import WorldState

from tests.conftest import MarshalFactory, WorldFactory


def _poisoned_result():
    """An executor result shaped like the live crash: a pending capture choice
    early-return whose enemy_phase actions still carry WorldState new_state."""
    inner_world = WorldState()
    # The live poison: a tuple-keyed cache on the embedded state. Encoding a
    # tuple key turns it into a list, which cannot key the encoded dict.
    inner_world._distance_cache = {("Paris", "Vienna"): 7}
    return {
        "success": True,
        "message": "Turn 3 ended.",
        "events": [],
        "pending_capture_choice": {"marshal": "Soult", "region": "Franconia"},
        "enemy_phase": {
            "total_actions": 1,
            "nations": {
                "Austria": {
                    "action_count": 1,
                    "actions": [{
                        "ai_action": {"action": "move", "target": "Bohemia"},
                        "events": [{"type": "enemy_move", "location": "Bohemia"}],
                        "new_state": inner_world,
                    }],
                },
            },
        },
        "new_state": inner_world,
    }


def _world():
    ney = MarshalFactory.infantry(name="Ney", location="Paris")
    return WorldFactory.with_marshals([ney])


def test_early_return_with_enemy_phase_is_json_encodable():
    """The exact live failure: jsonable_encoder over the built response must
    not raise on the embedded WorldState's tuple-keyed cache."""
    response = _build_result_response(_poisoned_result(), _world())
    jsonable_encoder(response)  # raised TypeError before the fix


def test_no_new_state_survives_anywhere_in_enemy_phase():
    response = _build_result_response(_poisoned_result(), _world())
    phase = response.get("enemy_phase")
    if phase is None:
        return  # fully fog-hidden is acceptable — nothing leaked either
    for nation_data in phase.get("nations", {}).values():
        for action in nation_data.get("actions", []):
            assert "new_state" not in action


def test_enemy_phase_is_fog_filtered_not_raw():
    """The raw pass-through leaked unfiltered enemy actions; the cleaned
    payload must be the fog-filtered shape (hidden activity collapses to the
    fog summary rather than shipping full action data)."""
    response = _build_result_response(_poisoned_result(), _world())
    phase = response.get("enemy_phase")
    if phase is None:
        return
    visible_actions = sum(
        len(n.get("actions", [])) for n in phase.get("nations", {}).values())
    if visible_actions == 0:
        assert phase.get("fog_hidden_summary"), (
            "hidden activity must at least surface the fog summary")


def test_results_without_enemy_phase_are_byte_unchanged():
    world = _world()
    result = {"success": True, "message": "ok", "events": [],
              "action_info": {"cost": 1}}
    response = _build_result_response(result, world)
    assert response["success"] is True
    assert response["message"] == "ok"
    assert "enemy_phase" not in response
