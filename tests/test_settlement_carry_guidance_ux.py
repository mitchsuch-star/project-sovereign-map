"""Re-front UX follow-up: PROPOSE carry-guidance + blocked-REVIEW recovery.

Gate-4 smoke surfaced that a winning multilateral baseline opens as a
near-acceptable DEMAND that does not carry (Britain 44 / Prussia 35,
threshold 50). Submitting it landed a blocked REVIEW with no Ratify button
and only escape hatches (Seek Bilateral Peace -> single-court reject), which
read as "Submit didn't work / terms lost".

These tests pin the three clarity fixes:
  1. PROPOSE surfaces a `propose_carry_hint` while the package does NOT carry,
     naming the holdout courts + pointing at the dials; it clears once it carries.
  2. A blocked REVIEW leads with a non-destructive `return_to_settlement_terms`
     that re-stages PROPOSE with the draft preserved (not a dead end).
  3. The pair-scoped escape hatches name the single covered court explicitly so
     the player knows they ABANDON the joint settlement.
"""

from __future__ import annotations

import pytest

from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.models.world_state import WorldState


@pytest.fixture
def multilateral_world(monkeypatch):
    """France winning vs Britain + Prussia; default baseline does not carry."""
    monkeypatch.setenv("SOVEREIGN_SMOKE_START", "settlement_multilateral")
    return WorldState()


def _opt_index(dlg, action):
    for i, opt in enumerate(dlg.get("options") or []):
        if opt.get("action") == action:
            return i + 1
    return None


def _open_propose(world):
    ex = DiplomaticExecutor(None)
    result = ex._execute_propose_common_peace(
        {
            "action": "propose_common_peace",
            "target_nation": "Britain",
            "war_id": "war_1",
            "selected_target_nation": "Britain",
            "covered_enemy_participants": ["Britain", "Prussia"],
        },
        {"world": world},
    )
    return ex, result["diplomatic_dialogue"]


def _submit_for_review(ex, dlg, world):
    return ex.handle_diplomatic_dialogue_response(
        _opt_index(dlg, "submit_settlement_for_review"), {"world": world}
    )["diplomatic_dialogue"]


def test_propose_carry_hint_present_and_names_holdouts(multilateral_world):
    _ex, dlg = _open_propose(multilateral_world)
    assert (dlg.get("overall_acceptance") or {}).get("carries") is False
    hint = dlg.get("propose_carry_hint") or ""
    assert hint != ""
    assert "Britain" in hint and "Prussia" in hint
    assert "More generous" in hint
    # It must warn that submitting now is a dead end.
    assert "cannot ratify" in hint or "can't ratify" in hint or "review" in hint.lower()


def test_propose_carry_hint_clears_once_package_carries(multilateral_world):
    ex, dlg = _open_propose(multilateral_world)
    gs = {"world": multilateral_world}
    for _ in range(8):
        idx = _opt_index(dlg, "settlement_dial_generous")
        assert idx is not None
        dlg = ex.handle_diplomatic_dialogue_response(idx, gs)["diplomatic_dialogue"]
        if (dlg.get("overall_acceptance") or {}).get("carries"):
            break
    assert (dlg.get("overall_acceptance") or {}).get("carries") is True
    assert dlg.get("propose_carry_hint", "") == ""


def test_carry_hint_is_propose_only_absent_on_review(multilateral_world):
    ex, dlg = _open_propose(multilateral_world)
    review = _submit_for_review(ex, dlg, multilateral_world)
    assert review.get("propose_carry_hint", "") == ""


def test_blocked_review_offers_return_to_terms_leading_escape_hatches(multilateral_world):
    ex, dlg = _open_propose(multilateral_world)
    review = _submit_for_review(ex, dlg, multilateral_world)
    assert review.get("can_ratify") is False
    actions = [o.get("action") for o in review.get("options") or []]
    assert "return_to_settlement_terms" in actions
    assert "return_to_settlement_terms" in (review.get("available_action_ids") or [])
    # The constructive recovery leads the pair-scoped escape hatches.
    assert actions.index("return_to_settlement_terms") < actions.index("seek_bilateral_peace")


def test_return_to_terms_restages_propose_preserving_draft(multilateral_world):
    ex, dlg = _open_propose(multilateral_world)
    gs = {"world": multilateral_world}
    review = _submit_for_review(ex, dlg, multilateral_world)
    before = [t.get("type") for t in review.get("settlement_terms") or []]
    result = ex.handle_diplomatic_dialogue_response(
        _opt_index(review, "return_to_settlement_terms"), gs
    )
    back = result["diplomatic_dialogue"]
    assert result.get("success") is not False
    assert back.get("dialogue_mode") == "PROPOSE"
    assert [t.get("type") for t in back.get("settlement_terms") or []] == before
    # The conversational dials are available again to keep easing.
    assert _opt_index(back, "settlement_dial_generous") is not None
    # And the carry hint is back on the re-staged PROPOSE surface.
    assert (back.get("propose_carry_hint") or "") != ""


def test_pair_substitute_labels_name_single_court(multilateral_world):
    ex, dlg = _open_propose(multilateral_world)
    review = _submit_for_review(ex, dlg, multilateral_world)
    by_action = {o.get("action"): o for o in review.get("options") or []}
    assert by_action["seek_bilateral_peace"]["label"] == "Make peace with Britain only"
    assert by_action["seek_armistice_instead"]["label"] == "Armistice with Britain only"
    # Description spells out that it abandons the joint settlement.
    assert "joint settlement" in by_action["seek_bilateral_peace"]["description"]
