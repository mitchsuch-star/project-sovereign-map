"""PC15-10 B3 — "The crisis survives a new flow" (W7;
`docs/PETITION_POPUP_REVISIT_SPEC.md` §4 F6; Score Mandate Chunk 4,
September 27, 2026).

A HYBRID dialogue — a vassal teetering on rebellion, Talleyrand's sabotage
reckoning — does not block commands, so the player may type a declaration of
war (or any new flow) over it. `DialogueManager.open_flow` preserved only
MAIL; a hybrid fell through to `replace()` and was DESTROYED: the rebellion
decision gone from the slot and the queue alike, the sabotage record left
`discovered` forever with no reckoning. F6's other half — the popups' ids and
the client sending them — landed on Sept 2 (FA-N5); measured at HEAD, the
stale answer was already refused rather than cross-applied.

The fix, two parts:
  * `open_flow` preempts a displaced hybrid too (the queue keeps it);
  * its modal was consumed when first delivered, so a stale answer aimed at a
    QUEUED hybrid re-issues the modal (ONE builder each: the rebellion's
    `rebellion_popup_for_dialogue`, the sabotage's new
    `diplomatic_defiance.build_sabotage_popup`); the FA-N5 delivery gate then
    holds it until its dialogue is current again, and the refusal says the
    crisis will return.

Levers: `dialogue_manager.HYBRIDS_SURVIVE_A_NEW_FLOW`,
`diplomatic_executor.THE_HYBRID_MODAL_RETURNS`.
"""

import contextlib
import io

import pytest
from fastapi.testclient import TestClient

import backend.commands.diplomatic_executor as DX
import backend.main as M
import backend.models.dialogue_manager as DMmod
from backend.commands import diplomatic_defiance as DD
from backend.game_logic import vassal as V
from backend.models.dialogue_manager import DialogueManager
from tests import _chip_census as C


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    w = M.world
    dm = w.dialogue_manager
    while dm.peek() is not None:
        dm.pop()
    return w


def _post(client, path, body):
    with _quiet():
        return client.post(path, json=body).json()


def _live_ids(world):
    dm = world.dialogue_manager
    return {int(d["dialogue_id"]) for d in [dm.peek()] + dm.iter_queue()
            if isinstance(d, dict) and d.get("dialogue_id") is not None}


def _raise_rebellion(world, vassal="Holland"):
    world.vassals[vassal]["loyalty"] = 9
    with _quiet():
        V.process_vassal_loyalty(world)
    cur = world.dialogue_manager.peek()
    assert cur and cur.get("type") == "vassal_rebellion_imminent", cur
    return int(cur["dialogue_id"])


# ═══════════════════════ open_flow — the rule, pinned ═══════════════════════

class TestOpenFlowKeepsWhatThePlayerOwns:

    def _dm(self, current_type):
        dm = DialogueManager()
        dm.push({"type": current_type, "target_nation": "Holland"})
        return dm

    def test_a_hybrid_is_preempted_not_destroyed(self):
        dm = self._dm("vassal_rebellion_imminent")
        dm.open_flow({"type": "war_purpose_selection"})
        assert dm.peek()["type"] == "war_purpose_selection"
        assert [d["type"] for d in dm.iter_queue()] == ["vassal_rebellion_imminent"]

    def test_sabotage_is_a_hybrid_too(self):
        dm = self._dm("sabotage_confrontation")
        dm.open_flow({"type": "war_purpose_selection"})
        assert [d["type"] for d in dm.iter_queue()] == ["sabotage_confrontation"]

    def test_mail_is_preempted_as_before(self):
        """REV-3's rule — nothing pinned it until now."""
        dm = self._dm("incoming_proposal")
        dm.open_flow({"type": "war_purpose_selection"})
        assert [d["type"] for d in dm.iter_queue()] == ["incoming_proposal"]

    def test_a_planning_step_is_still_overwritten(self):
        dm = self._dm("war_purpose_selection")
        dm.open_flow({"type": "proposal_confirm"})
        assert dm.peek()["type"] == "proposal_confirm"
        assert dm.iter_queue() == []

    def test_lever_down_the_hybrid_is_destroyed_as_before(self, monkeypatch):
        monkeypatch.setattr(DMmod, "HYBRIDS_SURVIVE_A_NEW_FLOW", False)
        dm = self._dm("vassal_rebellion_imminent")
        dm.open_flow({"type": "war_purpose_selection"})
        assert dm.iter_queue() == []


# ═══════════════════════ W7 — the rebellion, end to end ═════════════════════

class TestTheRebellionReturns:

    def test_the_whole_road(self, world):
        client = TestClient(M.app)
        reb_id = _raise_rebellion(world)
        body = _post(client, "/command", {"command": "status"})
        assert (body.get("vassal_rebellion_imminent") or {}).get("dialogue_id") == reb_id

        body = _post(client, "/command", {"command": "declare war on Prussia"})
        assert world.dialogue_manager.peek()["type"] != "vassal_rebellion_imminent"
        assert reb_id in _live_ids(world), "the crisis survives the new flow"

        body = _post(client, "/respond_to_diplomatic_dialogue",
                     {"choice": "invest_vassal_rebellion", "dialogue_id": reb_id})
        assert body.get("stale_dialogue") is True
        assert world.vassals["Holland"]["loyalty"] == 9, "nothing was applied"
        assert "will return" in body.get("message", "")
        assert any(p.get("dialogue_id") == reb_id
                   for p in world.vassal_rebellion_imminent_popups), \
            "the consumed modal is re-issued"

        war_dialogue = world.dialogue_manager.peek()
        back = _post(client, "/respond_to_diplomatic_dialogue",
                     {"choice": "reconsider",
                      "dialogue_id": war_dialogue.get("dialogue_id")})
        assert world.dialogue_manager.peek()["type"] == "vassal_rebellion_imminent"

        # The modal comes back on the very response that makes its crisis
        # current again (every response drains the popups) — or, at the
        # latest, on the next one. Delivered exactly once either way.
        after = _post(client, "/command", {"command": "status"})
        delivered = [r.get("vassal_rebellion_imminent") or {} for r in (back, after)]
        ids = [d.get("dialogue_id") for d in delivered if d]
        assert ids == [reb_id], f"the modal is delivered again, once: {ids}"

        body = _post(client, "/respond_to_diplomatic_dialogue",
                     {"choice": "garrison_vassal_rebellion", "dialogue_id": reb_id})
        assert not body.get("stale_dialogue"), body.get("message")
        assert reb_id not in _live_ids(world) or not body.get("success") is False

    def test_a_second_stale_answer_does_not_duplicate_the_modal(self, world):
        client = TestClient(M.app)
        reb_id = _raise_rebellion(world)
        _post(client, "/command", {"command": "status"})
        _post(client, "/command", {"command": "declare war on Prussia"})
        for _ in range(2):
            _post(client, "/respond_to_diplomatic_dialogue",
                  {"choice": "invest_vassal_rebellion", "dialogue_id": reb_id})
        assert sum(1 for p in world.vassal_rebellion_imminent_popups
                   if p.get("dialogue_id") == reb_id) == 1

    def test_lever_down_the_modal_does_not_return(self, world, monkeypatch):
        monkeypatch.setattr(DX, "THE_HYBRID_MODAL_RETURNS", False)
        client = TestClient(M.app)
        reb_id = _raise_rebellion(world)
        _post(client, "/command", {"command": "status"})
        _post(client, "/command", {"command": "declare war on Prussia"})
        body = _post(client, "/respond_to_diplomatic_dialogue",
                     {"choice": "invest_vassal_rebellion", "dialogue_id": reb_id})
        assert body.get("stale_dialogue") is True
        assert "will return" not in body.get("message", "")
        assert not any(p.get("dialogue_id") == reb_id
                       for p in world.vassal_rebellion_imminent_popups)


# ═══════════════════════ the sabotage reckoning ═════════════════════════════

class TestTheSabotageReckoningReturns:

    def _stage(self, world):
        record = {"target_nation": "Prussia", "defiance_type": "softened",
                  "original_proposal": {"type": "alliance"},
                  "modified_proposal": {"type": "alliance"},
                  "original_summary": "an alliance", "modified_summary":
                  "a softer alliance", "discovered": True, "turn_created": 1}
        world.pending_talleyrand_sabotage = record
        talleyrand = world.diplomats.get(world.player_nation)
        dialogue = DD.build_confrontation_dialogue(record, talleyrand)
        world.dialogue_manager.push(dialogue)
        sid = int(dialogue["dialogue_id"])
        world.diplomatic_sabotage_popup = DD.build_sabotage_popup(record, sid)
        return sid, record

    def test_one_builder_for_the_producer_and_the_return(self, world):
        sid, record = self._stage(world)
        popup = DD.build_sabotage_popup(record, sid)
        assert popup["dialogue_id"] == sid
        assert popup["ordered_summary"] == "an alliance"
        assert popup["delivered_summary"] == "a softer alliance"
        import inspect
        from backend.game_logic import dispatch as D
        src = inspect.getsource(D)
        assert "build_sabotage_popup(" in src, "the producer reads the one builder"

    def test_the_reckoning_survives_and_returns(self, world):
        client = TestClient(M.app)
        sid, _record = self._stage(world)
        body = _post(client, "/command", {"command": "status"})
        assert (body.get("diplomatic_sabotage") or {}).get("dialogue_id") == sid
        _post(client, "/command", {"command": "declare war on Prussia"})
        assert sid in _live_ids(world)
        body = _post(client, "/respond_to_diplomatic_dialogue",
                     {"choice": "confront_sabotage", "dialogue_id": sid})
        assert body.get("stale_dialogue") is True
        assert (world.diplomatic_sabotage_popup or {}).get("dialogue_id") == sid
        assert "will return" in body.get("message", "")
