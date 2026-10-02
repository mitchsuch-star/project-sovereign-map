"""SF-DIP-1 "The dial survives the drop" (Score Finish Step 2, October 2, 2026).

Verified REAL before building: every cover add/drop re-drew the WHOLE
package from the baseline, so a pressed Austria was reset to the bare peace
the moment Russia was dropped. Now the remaining courts keep the terms the
player dialled, only the dropped court's clauses are struck, an added court
receives the baseline slice authored for it, and each court's change is
named.
"""
import contextlib
import io
from pathlib import Path

import pytest

from backend.game_logic import settlement_actions as SA
from backend.game_logic.settlement_staging import stage_settlement_confirm
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCEN = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
           / "europe_1805.json")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture
def table():
    """The PROPOSE surface over Austria + Russia, reached the player's way."""
    with _quiet():
        world = WorldState.from_scenario(SCEN)
        stage_settlement_confirm(world, war_id="war_1", settlement_terms=[{"type": "peace"}],
                                 covered_enemy_participants=["Austria", "Russia"],
                                 caller_kind="player_editor")
        r = SA.handle_settlement_dialogue_action(
            world, action="return_to_settlement_terms",
            dialogue=world.pending_diplomatic_dialogue, action_params={})
    assert r.get("success"), r
    assert world.pending_diplomatic_dialogue.get("dialogue_mode") == "PROPOSE"
    return world


def _act(world, action, **params):
    with _quiet():
        r = SA.handle_settlement_dialogue_action(
            world, action=action, dialogue=world.pending_diplomatic_dialogue,
            action_params=params)
    assert r.get("success"), (action, r.get("error"), r.get("error_display"))
    return r


def _terms(world):
    return [dict(t) for t in world.pending_diplomatic_dialogue.get("settlement_terms") or []]


def _press(world, court):
    return _act(world, "settlement_dial_harsher", scope=court, nation=court, war_id="war_1")


class TestTheDialSurvivesTheDrop:

    def test_the_pressed_court_keeps_its_terms_when_another_is_dropped(self, table):
        world = table
        _press(world, "Austria")
        before = _terms(world)
        austrian = [t for t in before if SA.clause_names_court(t, "Austria")]
        assert austrian, before
        r = _act(world, "settlement_cover_drop", nation="Russia", war_id="war_1")
        after = _terms(world)
        assert [t for t in after if SA.clause_names_court(t, "Austria")] == austrian, after
        assert not any(SA.clause_names_court(t, "Russia") for t in after)
        assert sorted(world.pending_diplomatic_dialogue["covered_enemy_participants"]) == ["Austria"]
        msg = r.get("message", "")
        assert msg.startswith("Dropped Russia — 0 clauses naming it struck."), msg
        assert "Austria keeps 1 clause (gold indemnity)" in msg, msg

    def test_the_dropped_courts_own_clauses_are_struck(self, table):
        world = table
        _press(world, "Austria")
        _press(world, "Russia")
        before = _terms(world)
        assert any(SA.clause_names_court(t, "Russia") for t in before), before
        r = _act(world, "settlement_cover_drop", nation="Russia", war_id="war_1")
        after = _terms(world)
        assert not any(SA.clause_names_court(t, "Russia") for t in after)
        assert [t for t in after if SA.clause_names_court(t, "Austria")] == \
            [t for t in before if SA.clause_names_court(t, "Austria")]
        assert r.get("message", "").startswith("Dropped Russia — 1 clause naming it struck.")

    def test_an_added_court_receives_its_baseline_slice_and_the_rest_stand(self, table):
        world = table
        _press(world, "Austria")
        _act(world, "settlement_cover_drop", nation="Russia", war_id="war_1")
        austrian = [t for t in _terms(world) if SA.clause_names_court(t, "Austria")]
        r = _act(world, "settlement_cover_add", nation="Russia", war_id="war_1")
        after = _terms(world)
        assert [t for t in after if SA.clause_names_court(t, "Austria")] == austrian, after
        assert sorted(world.pending_diplomatic_dialogue["covered_enemy_participants"]) == ["Austria", "Russia"]
        msg = r.get("message", "")
        assert msg.startswith("Added Russia — "), msg
        assert "Austria keeps 1 clause (gold indemnity)" in msg, msg
        assert sum(1 for t in after if t.get("type") == "peace") == 1

    def test_lever_down_resets_the_dial(self, table, monkeypatch):
        monkeypatch.setattr(SA, "THE_DIAL_SURVIVES_THE_DROP", False)
        world = table
        _press(world, "Austria")
        assert any(SA.clause_names_court(t, "Austria") for t in _terms(world))
        r = _act(world, "settlement_cover_drop", nation="Russia", war_id="war_1")
        assert not any(SA.clause_names_court(t, "Austria") for t in _terms(world))
        assert r.get("message") == "Dropped Russia; the settlement was re-drafted."

    def test_the_predicate(self):
        assert SA.clause_names_court({"type": "gold_indemnity", "from": "Austria", "to": "France"}, "Austria")
        assert SA.clause_names_court({"type": "gold_indemnity", "from": "Austria", "to": "France"}, "France")
        assert not SA.clause_names_court({"type": "peace"}, "Austria")
        assert not SA.clause_names_court({"type": "territory_cede", "from": "Russia"}, "Austria")
