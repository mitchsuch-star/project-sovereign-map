"""WO-41 — the redemption question survives the save (September 1, 2026).

Row WO's last unowned residue: filed August 22 by slice 18's verification
(memo docs/audits/WO_35_36_38_VERIFICATION_2026_08_21.md §6a/§6b/§6c),
assigned to slice 9, which landed without it.

The defect wore three coats. `world.pending_redemption` — the field the
save carries, GET /pending_redemption answers from and /load re-attaches —
was written only at the API boundary in main.py, AFTER both autosaves had
already run inside the executor. So:

  (a) the end-turn autosave (the main menu's own Continue arm) recorded
      `marshal.redemption_pending=True` with `world.pending_redemption=None`
      — the latch without the question; the checker returns None forever
      once the latch is set, so the marshal never asked again;
  (b) the auto-advance path hoisted `battle_report` out of the tactical
      events and never the redemption, unlike its end-turn sibling — a
      last-AP turn advance that tripped a cavalry/fortify redemption
      dropped the audience with no save involved;
  (c) two marshals crossing in one tick: the response key carried the
      first, the world field was overwritten with the last, and the
      loser's latch meant he never asked again either.

Fix: the checker writes the world field beside the latch (one seam, both
autosaves now see it); ONE liveness predicate `standing_redemption` read
by the generation seam, GET and /load; ONE hoist `hoist_tactical_redemption`
for both turn-advance paths; /load attaches the key and the client's
world-swap tail stashes and raises it (PT-B1's discipline, never the
route). Flip lever `REDEMPTION_LATCH_AT_GENERATION_ACTIVE` reproduces the
prior behaviour so the tests below can show they are about the right thing.

Every test names the mutation that kills it.
"""

import json
import re
from pathlib import Path

import pytest

from backend import save_manager
from backend.commands import disobedience as DIS
from backend.commands.disobedience import (
    DisobedienceSystem,
    hoist_tactical_redemption,
    standing_redemption,
)
from backend.commands.executor import CommandExecutor
from backend.models.marshal import Stance
from backend.models.world_state import WorldState
from backend.save_manager import load_game, save_game

MAIN_GD = (Path(__file__).resolve().parents[1] / "godot-client"
           / "project-sovereign" / "scripts" / "main.gd")


def _cross(world, name, trust=18):
    """Push a French marshal under the threshold and run the checker."""
    m = world.get_marshal(name)
    m.trust.set(trust)
    m.redemption_pending = False
    return m, world.disobedience_system.check_redemption_threshold(m, world)


def _arm_cavalry_limit(world, name, trust=23):
    """Set up a cavalry marshal so the next turn tick trips the -3 stance
    penalty (23 -> 20, exactly at the <= 20 threshold)."""
    m = world.get_marshal(name)
    m.cavalry = True
    m.trust.set(trust)
    m.redemption_pending = False
    m.stance = Stance.DEFENSIVE
    m.turns_in_defensive_stance = 3
    return m


@pytest.fixture
def sandboxed_saves(tmp_path, monkeypatch):
    """Autosave and /load read `save_manager.SAVE_DIR` at call time."""
    monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path)
    return tmp_path


@pytest.fixture
def api(monkeypatch):
    """A fresh legacy world as the module-global the routes read, with the
    mock parser (the TestClient world-swap discipline)."""
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient

    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    world = WorldState()
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "game_state", {"world": world})
    return M, TestClient(M.app), world


# ═══════════════════════════════════════════════════════════════════════
# 1. The question is written where the latch is
# ═══════════════════════════════════════════════════════════════════════

class TestTheQuestionIsWrittenWhereTheLatchIs:

    def test_checker_writes_the_world_field_as_the_same_object(self):
        """Mutation: delete `world.pending_redemption = event` in
        `check_redemption_threshold`."""
        world = WorldState()
        ney, event = _cross(world, "Ney")
        assert event is not None
        assert ney.redemption_pending is True
        assert world.pending_redemption is event

    def test_lever_off_reproduces_the_filed_defect(self, monkeypatch):
        """The prior behaviour: latch set, world field untouched. Proves the
        pin above is about the lever, not about something else that
        happens to set the field. Mutation: freeze the lever True."""
        monkeypatch.setattr(DIS, "REDEMPTION_LATCH_AT_GENERATION_ACTIVE", False)
        world = WorldState()
        ney, event = _cross(world, "Ney")
        assert event is not None and ney.redemption_pending is True
        assert world.pending_redemption is None

    def test_no_world_no_write_no_crash(self):
        """Producers may hand the checker `world=None` (the objection path's
        `getattr(game_state, 'world', game_state)`). Mutation: drop the
        `world is not None` guard."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.trust.set(18)
        ney.redemption_pending = False
        event = DisobedienceSystem().check_redemption_threshold(ney, None)
        assert event is not None
        assert world.pending_redemption is None

    def test_the_api_boundary_write_is_now_idempotent(self, api):
        """The end-turn route's own write assigns the SAME dict the checker
        already stored. Mutation: delete the world-field write in the
        checker — the boundary still sets it, so this pin holds; it is the
        autosave pins below that kill that mutation."""
        M, client, world = api
        _arm_cavalry_limit(world, "Ney")
        data = client.post("/command", json={"command": "end turn"}).json()
        assert data.get("redemption_event"), data.get("message")
        assert data["redemption_event"]["marshal"] == "Ney"
        assert data["state"] == "awaiting_redemption_choice"
        assert M.world.pending_redemption == data["redemption_event"]


# ═══════════════════════════════════════════════════════════════════════
# 2. The autosave carries the question (§6a)
# ═══════════════════════════════════════════════════════════════════════

class TestTheAutosaveCarriesTheQuestion:

    def _autosave(self, sandboxed_saves):
        path = sandboxed_saves / save_manager.AUTOSAVE_FILENAME
        assert path.exists(), "the end turn did not autosave into the sandbox"
        return json.loads(path.read_text(encoding="utf-8"))["world_state"]

    def test_end_turn_autosave_records_the_question(self, sandboxed_saves):
        """§6a, the Continue arm. Mutation: delete the world-field write in
        the checker (the boundary write runs AFTER the autosave)."""
        world = WorldState()
        ney = _arm_cavalry_limit(world, "Ney")
        result = CommandExecutor()._execute_end_turn({}, {"world": world})
        assert result["success"], result.get("message")
        assert result["redemption_event"]["marshal"] == "Ney"
        assert ney.redemption_pending is True

        saved = self._autosave(sandboxed_saves)
        assert saved["pending_redemption"] is not None
        assert saved["pending_redemption"]["marshal"] == "Ney"

        loaded = load_game(sandboxed_saves / save_manager.AUTOSAVE_FILENAME)
        assert loaded["success"], loaded["message"]
        w2 = loaded["world"]
        assert w2.get_marshal("Ney").redemption_pending is True
        assert standing_redemption(w2) is not None
        assert standing_redemption(w2)["marshal"] == "Ney"

    def test_lever_off_reproduces_the_lost_audience(self, sandboxed_saves,
                                                    monkeypatch):
        """The measured defect: the save carries the latch and not the
        question, and nothing can ever ask again. Mutation: freeze the
        lever True."""
        monkeypatch.setattr(DIS, "REDEMPTION_LATCH_AT_GENERATION_ACTIVE", False)
        world = WorldState()
        _arm_cavalry_limit(world, "Ney")
        result = CommandExecutor()._execute_end_turn({}, {"world": world})
        assert result["redemption_event"]["marshal"] == "Ney"
        saved = self._autosave(sandboxed_saves)
        assert saved["pending_redemption"] is None            # no question
        loaded = load_game(sandboxed_saves / save_manager.AUTOSAVE_FILENAME)
        ney2 = loaded["world"].get_marshal("Ney")
        assert ney2.redemption_pending is True                # the latch
        assert loaded["world"].disobedience_system.check_redemption_threshold(
            ney2, loaded["world"]) is None                    # forever

    def test_auto_advance_hoists_the_redemption_and_autosaves_it(
            self, sandboxed_saves):
        """§6b: the last-AP turn advance. Mutation: delete the
        `_auto_redemption` block in `executor.py`'s auto-advance path
        (the response half) — and the world-field write for the save half."""
        world = WorldState()
        ney = _arm_cavalry_limit(world, "Ney")
        world.actions_remaining = 1
        world.admin_actions_remaining = 0
        # `drill` costs 1 AP (`wait` is free and would never advance the turn)
        result = CommandExecutor().execute({
            "command": {"type": "specific", "marshal": "Davout",
                        "action": "drill", "target": None}
        }, {"world": world})
        assert result.get("success"), result.get("message")
        assert result.get("action_info", {}).get("turn_advanced") is True, (
            "the fixture did not auto-advance; the test drives nothing")
        assert result.get("redemption_event"), (
            "the auto-advance path dropped the audience (WO-41 §6b)")
        assert result["redemption_event"]["marshal"] == "Ney"
        assert ney.redemption_pending is True
        saved = self._autosave(sandboxed_saves)
        assert saved["pending_redemption"]["marshal"] == "Ney"

    def test_the_hoist_is_one_rule(self):
        """First wins; non-dicts and eventless entries are skipped.
        Mutation: make `hoist_tactical_redemption` return None."""
        events = [{"type": "cavalry_stance_forced"}, "not a dict",
                  {"redemption_event": {"marshal": "A"}},
                  {"redemption_event": {"marshal": "B"}}]
        assert hoist_tactical_redemption(events) == {"marshal": "A"}
        assert hoist_tactical_redemption([]) is None
        assert hoist_tactical_redemption(None) is None


# ═══════════════════════════════════════════════════════════════════════
# 3. One live question at a time (§6c)
# ═══════════════════════════════════════════════════════════════════════

class TestOneLiveQuestionAtATime:

    def test_second_marshal_is_not_latched_behind_a_live_question(self):
        """Mutation: delete the `standing_redemption(world) is not None`
        guard in the checker."""
        world = WorldState()
        ney, first = _cross(world, "Ney")
        davout, second = _cross(world, "Davout")
        assert first is not None and second is None
        assert ney.redemption_pending is True
        assert davout.redemption_pending is False, (
            "the loser of the tick must not carry a latch nobody can answer")
        assert world.pending_redemption is first

    def test_second_marshal_asks_once_the_first_is_answered(self):
        """Mutation: latch the second anyway (drop `return None` in the
        guard)."""
        world = WorldState()
        ney, first = _cross(world, "Ney")
        davout, _ = _cross(world, "Davout")
        # answer the first the way POST /respond_to_redemption does
        world.disobedience_system.handle_redemption_response(
            first, "grant_autonomy", {"world": world})
        world.pending_redemption = None
        assert ney.redemption_pending is False
        second = world.disobedience_system.check_redemption_threshold(
            davout, world)
        assert second is not None and second["marshal"] == "Davout"
        assert world.pending_redemption is second
        assert davout.redemption_pending is True

    def test_lever_off_latches_both(self, monkeypatch):
        """The prior behaviour: both latched, one question lost.
        Mutation: freeze the lever True."""
        monkeypatch.setattr(DIS, "REDEMPTION_LATCH_AT_GENERATION_ACTIVE", False)
        world = WorldState()
        ney, first = _cross(world, "Ney")
        davout, second = _cross(world, "Davout")
        assert first is not None and second is not None
        assert ney.redemption_pending and davout.redemption_pending

    def test_the_tick_hoist_agrees_with_the_world_field(self):
        """Two cavalry marshals trip the limit in ONE tick: the response
        carries the same man the world is waiting on, and the other is
        not latched. Mutation: drop the standing guard (both latch) or
        make the hoist read the LAST event."""
        world = WorldState()
        ney = _arm_cavalry_limit(world, "Ney")
        davout = _arm_cavalry_limit(world, "Davout")
        result = CommandExecutor()._execute_end_turn({}, {"world": world})
        event = result.get("redemption_event")
        assert event, "no redemption reached the response"
        assert world.pending_redemption is not None
        assert event["marshal"] == world.pending_redemption["marshal"]
        latched = [m for m in (ney, davout) if m.redemption_pending]
        assert len(latched) == 1 and latched[0].name == event["marshal"]
        assert ney.trust.value <= 20 and davout.trust.value <= 20, (
            "both must have crossed for this fixture to test anything")


# ═══════════════════════════════════════════════════════════════════════
# 4. Stale questions are cleared, live ones kept
# ═══════════════════════════════════════════════════════════════════════

class TestStaleQuestionsAreCleared:

    def _standing(self, world, name="Ney"):
        m = world.get_marshal(name)
        m.trust.set(15)
        m.redemption_pending = True
        world.pending_redemption = {"type": "redemption_event", "marshal": name,
                                    "trust": 15, "message": "m", "options": []}
        return m

    def test_live_question_is_kept(self):
        world = WorldState()
        self._standing(world)
        assert standing_redemption(world) is world.pending_redemption

    def test_recovered_marshal_question_is_stale(self):
        """`Marshal.modify_trust` clears the latch above 20; the stored
        question is then about nothing. Mutation: drop the
        `redemption_pending` clause of the liveness predicate."""
        world = WorldState()
        ney = self._standing(world)
        ney.modify_trust(+30)
        assert ney.redemption_pending is False
        assert standing_redemption(world) is None
        assert world.pending_redemption is None

    def test_fallen_marshal_question_is_stale(self):
        """Mutation: drop the `strength > 0` clause."""
        world = WorldState()
        ney = self._standing(world)
        ney.strength = 0
        assert standing_redemption(world) is None
        assert world.pending_redemption is None

    def test_captured_marshal_question_is_stale(self):
        """Mutation: drop the `captured_by` clause."""
        world = WorldState()
        ney = self._standing(world)
        ney.captured_by = "Austria"
        assert standing_redemption(world) is None

    def test_a_stale_question_is_cleared_not_left_to_block(self):
        """A stale question must not block the next marshal's audience.
        Mutation: `return None` without clearing in the predicate."""
        world = WorldState()
        ney = self._standing(world)
        ney.strength = 0
        davout, event = _cross(world, "Davout")
        assert event is not None and event["marshal"] == "Davout"
        assert world.pending_redemption is event

    def test_get_answers_from_the_liveness_predicate(self, api):
        """Mutation: make GET read the raw field again."""
        M, client, world = api
        ney = self._standing(world)
        assert client.get("/pending_redemption").json()["has_pending"] is True
        ney.strength = 0
        out = client.get("/pending_redemption").json()
        assert out["has_pending"] is False
        assert world.pending_redemption is None

    def test_debug_trigger_latches_the_marshal(self, api, monkeypatch):
        """The debug trigger bypasses the checker; without the latch its
        question would read as stale. Mutation: delete
        `marshal.redemption_pending = True` in `debug_trigger_redemption`."""
        M, client, world = api
        monkeypatch.setattr(M, "DEBUG_MODE", True)
        out = M.debug_trigger_redemption("Ney")
        assert out["success"]
        assert world.get_marshal("Ney").redemption_pending is True
        assert standing_redemption(world) is not None


# ═══════════════════════════════════════════════════════════════════════
# 5. /load attaches the key; the client stashes and raises it
# ═══════════════════════════════════════════════════════════════════════

class TestLoadAttachesTheKey:

    def _save(self, sandboxed_saves, world, name="wo41_probe.json"):
        out = save_game(world, "WO41", filepath=sandboxed_saves / name)
        assert out["success"], out["message"]
        return name

    def test_load_attaches_a_live_question(self, api, sandboxed_saves):
        """Mutation: delete the WO-41 attach block in `/load`."""
        M, client, _ = api
        world = WorldState()
        ney, event = _cross(world, "Ney")
        name = self._save(sandboxed_saves, world)
        data = client.post("/load", json={"filename": name}).json()
        assert data["success"], data["message"]
        assert data.get("redemption_event"), "the standing question was silent at load"
        assert data["redemption_event"]["marshal"] == "Ney"
        assert M.world.get_marshal("Ney").redemption_pending is True

    def test_load_does_not_attach_a_stale_question(self, api, sandboxed_saves):
        """Mutation: attach the raw field instead of the predicate."""
        M, client, _ = api
        world = WorldState()
        ney, event = _cross(world, "Ney")
        ney.modify_trust(+30)  # recovered: latch cleared, field still set
        assert world.pending_redemption is not None
        name = self._save(sandboxed_saves, world)
        data = client.post("/load", json={"filename": name}).json()
        assert data["success"], data["message"]
        assert not data.get("redemption_event")
        assert M.world.pending_redemption is None


class TestTheClientRaisesItAtLoad:

    @pytest.fixture(scope="class")
    def swap_body(self):
        """The handler's CODE — comment lines stripped, so a pin can never be
        satisfied (or violated) by the prose written to explain the fix."""
        src = MAIN_GD.read_text(encoding="utf-8")
        m = re.search(r"func _apply_world_swap_response\((.*?)\nfunc ", src, re.S)
        assert m, "_apply_world_swap_response could not be located"
        return "\n".join(line for line in m.group(1).splitlines()
                         if not line.strip().startswith("#"))

    def test_it_is_stashed_above_the_early_returning_arms(self, swap_body):
        """A capture or interrupt raised first must not lose the stash.
        Mutation: move `_stash_redemption(response)` below the capture arm,
        or delete it."""
        stash = swap_body.find("_stash_redemption(response)")
        capture = swap_body.find("_response_has_capture_choice_route(response)")
        assert stash != -1, "the world-swap tail does not stash the redemption"
        assert capture != -1
        assert stash < capture

    def test_it_is_raised_last_and_owns_input(self, swap_body):
        """Raised behind the capture and interrupt arms, and a shown dialog
        returns before input is re-enabled (the other tails' idiom).
        Mutation: delete the `if _show_pending_redemption():` arm."""
        interrupt = swap_body.find("_response_has_interrupt_route(response)")
        raise_ = re.search(r"\tif _show_pending_redemption\(\):\n\t\treturn", swap_body)
        assert raise_, "the world-swap tail does not raise the stash"
        assert raise_.start() > interrupt
        enable = swap_body.rfind("set_input_enabled(true)")
        assert raise_.start() < enable

    def test_never_through_the_route(self, swap_body):
        """`_route_redemption_response` re-renders the whole payload via
        `_display_result`. Mutation: route it."""
        assert "_route_redemption_response" not in swap_body
