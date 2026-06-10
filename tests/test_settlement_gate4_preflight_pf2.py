"""PF-2 — Gate-4 pre-flight audit §5: draft-restore honesty (D4).

The May-31 "Settlement draft kept" Back Out promise was broken: suspend
saved under the full ``(war_id, target, covered)`` scoped key (and
dual-wrote a legacy store nothing reads), while the only real reopen route
(War Detail → Open Settlement) sends ``{war_id, target_nation}`` with NO
covered list — a different hash, so reopen always regenerated a fresh
baseline. PF-2 makes the promise true and visible:

- ``load_scoped_settlement_draft`` falls back to a ``(war_id, target)`` key
  prefix, then a ``war_id`` prefix (most recent save wins).
- The suspend arm writes ONE store (scoped) — the legacy dual-write is gone.
- War Detail carries a ``settlement_draft_kept`` badge iff a same-turn
  scoped draft would actually restore.

The restore test drives the REAL client payload shape through the HTTP
boundary (the D4 lesson: the old round-trip test passed an explicit covered
list the client never sends, so the real shape was never exercised).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.game_logic.settlement_preview import (
    handle_settlement_dialogue_action,
    load_scoped_settlement_draft,
    stage_settlement_confirm,
)
from backend.game_logic.war_status import build_active_wars
from backend.models.world_state import (
    SMOKE_START_ENV,
    SMOKE_START_SETTLEMENT_LOSING,
    WorldState,
)

GODOT_SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "godot-client"
    / "project-sovereign"
    / "scripts"
)

REAL_REOPEN_BODY = {
    # Mirrors main.gd::_on_war_settlement_clicked exactly — no covered list,
    # no selected_target_nation, no settlement_terms.
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain",
    "war_id": "war_1",
}


@pytest.fixture
def losing_world(monkeypatch):
    monkeypatch.setenv(SMOKE_START_ENV, SMOKE_START_SETTLEMENT_LOSING)
    return WorldState()


def _suspend_with_dialed_draft(world: WorldState) -> list:
    """Stage PROPOSE, ease the whole table once (terms now differ from a
    fresh baseline), then Back Out via the non-destructive suspend."""
    staged = stage_settlement_confirm(
        world,
        war_id="war_1",
        actor_nation="France",
        selected_target_nation="Britain",
        covered_enemy_participants=["Britain", "Prussia"],
        caller_kind="player_editor",
        dialogue_mode="PROPOSE",
    )
    assert staged.get("success"), staged
    dialed = handle_settlement_dialogue_action(
        world,
        action="settlement_dial_generous",
        dialogue=world.dialogue_manager.peek(),
        action_params={"action": "settlement_dial_generous", "scope": "table"},
    )
    assert dialed.get("success"), dialed
    dialed_terms = [
        dict(t)
        for t in dialed["diplomatic_dialogue"]["settlement_terms"]
        if isinstance(t, dict)
    ]
    suspended = handle_settlement_dialogue_action(
        world,
        action="suspend_settlement_editor",
        dialogue=world.dialogue_manager.peek(),
        action_params={},
    )
    assert suspended.get("success") and suspended.get("draft_preserved"), suspended
    assert world.dialogue_manager.peek() is None
    return dialed_terms


def _gold_amounts(terms) -> list:
    return sorted(
        int(t.get("amount", 0) or 0)
        for t in terms
        if t.get("type") == "gold_indemnity" and t.get("from") == "France"
    )


class TestDraftRestoreHonesty:
    def test_reopen_without_covered_list_restores_scoped_draft(
        self, losing_world
    ):
        """D4: Back Out → reopen restores the dialed terms on the REAL
        client payload shape (HTTP boundary, NOT executor-direct)."""
        import backend.main as main_module

        main_module._set_active_world(losing_world)
        dialed_terms = _suspend_with_dialed_draft(losing_world)
        client = TestClient(main_module.app)
        response = client.post("/command", json=REAL_REOPEN_BODY)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True, data
        assert data.get("draft_restored_from_scope") is True, (
            "reopen regenerated a fresh baseline instead of restoring the "
            "kept draft (the D4 broken promise)"
        )
        dialogue = data.get("diplomatic_dialogue") or {}
        assert _gold_amounts(dialogue.get("settlement_terms") or []) == (
            _gold_amounts(dialed_terms)
        )

    def test_reopen_restores_after_coverage_narrowing(self, losing_world):
        """The (war_id, target) prefix can also miss (the player narrowed
        coverage before suspending); the war_id prefix fallback still
        restores the most recent draft for the war."""
        staged = stage_settlement_confirm(
            losing_world,
            war_id="war_1",
            actor_nation="France",
            selected_target_nation="Prussia",
            covered_enemy_participants=["Prussia"],
            caller_kind="player_editor",
            dialogue_mode="PROPOSE",
        )
        assert staged.get("success"), staged
        suspended = handle_settlement_dialogue_action(
            losing_world,
            action="suspend_settlement_editor",
            dialogue=losing_world.dialogue_manager.peek(),
            action_params={},
        )
        assert suspended.get("draft_preserved"), suspended
        restored = load_scoped_settlement_draft(
            losing_world,
            war_id="war_1",
            selected_target_nation="Britain",
            covered_enemy_participants=[],
        )
        assert restored, "war_id-prefix fallback did not restore"

    def test_war_detail_exposes_draft_kept_indicator(self, losing_world):
        """UX-1: the badge appears iff a draft would actually restore."""
        def _war_entry():
            wars = build_active_wars(losing_world).get("wars") or []
            for war in wars:
                if war.get("war_instance_id") == "war_1":
                    return war
            raise AssertionError(f"war_1 row missing: {wars}")

        assert _war_entry().get("settlement_draft_kept") is False
        _suspend_with_dialed_draft(losing_world)
        assert _war_entry().get("settlement_draft_kept") is True
        # Godot renders the badge in the war detail body.
        popup_gd = (GODOT_SCRIPTS / "war_detail_popup.gd").read_text(
            encoding="utf-8"
        )
        assert "settlement_draft_kept" in popup_gd
        assert re.search(r"Draft kept", popup_gd)

    def test_single_draft_store_no_dual_write(self, losing_world):
        """CH-3 (PF-2 slice): suspend writes exactly ONE store — the scoped
        store survives, the legacy war_id-keyed dual-write is gone."""
        legacy_before = dict(
            getattr(losing_world, "pending_settlement_drafts", {}) or {}
        )
        _suspend_with_dialed_draft(losing_world)
        legacy_after = getattr(losing_world, "pending_settlement_drafts", {}) or {}
        assert legacy_after == legacy_before, (
            "suspend dual-wrote the legacy pending_settlement_drafts store"
        )
        scoped = getattr(
            losing_world, "pending_settlement_drafts_by_key", {}
        ) or {}
        assert any(
            key.startswith("settlement_draft:war_1:") and entry
            for key, entry in scoped.items()
        )
