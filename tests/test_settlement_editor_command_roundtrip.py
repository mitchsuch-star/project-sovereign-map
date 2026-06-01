"""Regression guard: settlement editor Submit-for-Review through the real
`/command` HTTP boundary (CommandRequest / FastAPI), not the executor directly.

The SC-5R-2 Tier-3 editor submits its authored package via
`api_client.send_structured_command`, which POSTs a structured
`propose_common_peace` body to `/command`. The body carries
`settlement_terms`, `selected_target_nation`, and `covered_enemy_participants`
at the top level.

The original `CommandRequest` model declared only command/action/target_nation/
war_id, so Pydantic silently dropped the settlement fields: the backend never
saw the authored terms, regenerated a PROPOSE baseline, and the player's terms
"did not appear afterwards". Every existing SC-5R-2 test called the executor
directly with a hand-built command dict, bypassing the Pydantic boundary, so
the strip shipped undetected.

These tests drive the real endpoint so the round-trip is enforced end to end:
    1. A valid authored package survives the POST and stages a REVIEW with the
       player's exact terms (not a regenerated baseline).
    2. An invalid authored package is rejected with the validation error code +
       humanized detail surfaced on the response (so Godot can remount the
       editor inline with the reason instead of failing silently).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from tests.test_settlement_sc5r2_godot_editor import (
    _acceptance_accepts,
    _gold_indemnity_clause,
    _install_common_peace_war,
)


@pytest.fixture(autouse=True)
def _mock_parser(monkeypatch):
    """Force deterministic mock parsing even when a real API key is present."""
    import backend.main as main_module
    from backend.commands.parser import CommandParser

    monkeypatch.setattr(main_module, "parser", CommandParser(use_real_llm=False))


@pytest.fixture
def client():
    from backend.main import app

    return TestClient(app)


@pytest.fixture
def war_world():
    """Install a France-led common-peace war as the active campaign world."""
    import backend.main as main_module
    from backend.models.world_state import WorldState

    world = WorldState()
    _install_common_peace_war(world)
    main_module._set_active_world(world)
    return world


def _editor_submit_body(settlement_terms):
    """Mirror the structured body main.gd._on_settlement_editor_submit POSTs."""
    return {
        "command": "propose common peace with Austria",
        "action": "propose_common_peace",
        "war_id": "war_1",
        "selected_target_nation": "Austria",
        "covered_enemy_participants": ["Austria", "Prussia"],
        "settlement_terms": settlement_terms,
        "caller_kind": "player_editor",
    }


def test_editor_submit_authored_terms_survive_and_stage_review(client, war_world):
    """Valid authored package: terms survive the Pydantic boundary and stage a
    REVIEW carrying the player's exact clauses (the core round-trip bug)."""
    body = _editor_submit_body([{"type": "peace"}, _gold_indemnity_clause(250)])
    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=_acceptance_accepts,
    ):
        response = client.post("/command", json=body)

    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True, data
    dialogue = data.get("diplomatic_dialogue") or {}
    # Submit-for-Review must land REVIEW, NOT a regenerated PROPOSE baseline.
    assert dialogue.get("dialogue_mode") == "REVIEW", dialogue.get("dialogue_mode")
    staged_terms = dialogue.get("settlement_terms") or []
    gold_amounts = [
        int(t.get("amount", 0))
        for t in staged_terms
        if t.get("type") == "gold_indemnity"
    ]
    # The authored 250 must be present verbatim (a baseline would regenerate a
    # different amount, e.g. ~300).
    assert 250 in gold_amounts, staged_terms


def test_editor_submit_drops_settlement_terms_without_fix_is_guarded(client, war_world):
    """The authored gold amount must not be silently replaced by a baseline.

    This is the direct anti-regression for the Pydantic field strip: if the
    structured `settlement_terms` are dropped, the backend regenerates a
    baseline and 250 would be absent from the staged review.
    """
    body = _editor_submit_body([{"type": "peace"}, _gold_indemnity_clause(250)])
    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=_acceptance_accepts,
    ):
        response = client.post("/command", json=body)
    dialogue = response.json().get("diplomatic_dialogue") or {}
    staged_types = [t.get("type") for t in (dialogue.get("settlement_terms") or [])]
    assert "gold_indemnity" in staged_types, staged_types


def test_editor_submit_invalid_self_vassalage_surfaces_validation_error(
    client, war_world
):
    """Invalid authored package: the rejection must surface the validation code
    and humanized detail so Godot remounts the editor inline (not silently)."""
    body = _editor_submit_body(
        [{"type": "peace"}, {"type": "vassalage", "from": "France", "to": "France"}]
    )
    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=_acceptance_accepts,
    ):
        response = client.post("/command", json=body)

    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is False, data
    # The remount trigger code main.gd keys on must survive to the client.
    assert data.get("error") == "submitted_terms_failed_revalidation", data
    assert data.get("validation_error") == "dependency_direction_invalid", data
    # A non-empty humanized reason must reach the player.
    assert str(data.get("validation_detail") or "").strip() != "", data
    assert str(data.get("message") or "").strip() != "", data
