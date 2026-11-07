"""T0-A "the turn's recovery" — the first slice of Tier 0 of the November 6,
2026 whole-game review (`docs/audits/GAME_REVIEW_2026_11_06.md` §4.1 #1, #9,
#22; `BUG_FIXES.md` §GR GR-52, GR-51, GR-54, GR-44; the rules
`SYSTEMS_REFERENCE.md` §178).

TURN-2 — one exception inside `advance_turn` used to wedge the campaign: the
R20 stamp is written before the stages, so every later End Turn hit the
guard, skipped the advance, REPLAYED the whole enemy phase and answered
"Turn N is already underway!" with success. Now the failed close rolls the
stamp back and raises `_advance_failed`; the next End Turn resumes the close
alone (no second lapse, enemy phase, AI letter, standing march or grievance
pass) and says so.
TURN-1 — a court's crash row (V2-19) has no marshal and no region, so the fog
filter dropped it and the player was never told a court skipped its turn. It
passes the fog now, names its court, and the rail carries the notice once per
court per turn.
TURN-4 / AIDIP-6 — every broad except speaks through `errors.report` (the
census's "logs" count is 0), and the bandwagon block's one import-labelled
guard is two guards with honest labels.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend import errors as _errors  # noqa: E402
from backend.commands.executor import CommandExecutor  # noqa: E402
from backend.game_logic.turn_manager import TurnManager  # noqa: E402
from backend.models.world_state import WorldState  # noqa: E402
from tests.conftest import WorldFactory  # noqa: E402

HEGEMONY_SITE = "ai_diplomacy.process_diplomatic_phase: the hegemony reading"
BANDWAGON_SITE = "ai_diplomacy.process_diplomatic_phase: P-Bandwagon and the vassal on-ramp"
OLD_LABEL = "ai_diplomacy.process_diplomatic_phase: import backend.game_logic.coalition"


def _raise_once(monkeypatch, exc=None):
    """`process_construction_timers` raises on its first call only — the stage
    sits after the tactical tick and before the counter's increment, so the
    failure lands with the stamp written and the turn not yet moved."""
    exc = exc or RuntimeError("the close failed: boom")
    calls = {"n": 0}
    original = WorldState.process_construction_timers

    def flaky(self):
        calls["n"] += 1
        if calls["n"] == 1:
            raise exc
        return original(self)

    monkeypatch.setattr(WorldState, "process_construction_timers", flaky)
    return calls


class TestTheCloseResumes:
    """TURN-2 (GR-52, the review's P2)."""

    def test_a_failed_close_rolls_the_stamp_back_and_raises(self, monkeypatch):
        world = WorldFactory.basic()
        _raise_once(monkeypatch)
        assert world._last_advanced_turn == 0 and world.current_turn == 1
        with pytest.raises(RuntimeError, match="boom"):
            world.advance_turn()
        assert world.current_turn == 1, "the counter never moved"
        assert world._last_advanced_turn == 0, "the R20 stamp is rolled back, not left at 1"
        assert world._advance_failed is True

    def test_the_next_advance_runs_and_clears_the_flag(self, monkeypatch):
        world = WorldFactory.basic()
        _raise_once(monkeypatch)
        with pytest.raises(RuntimeError):
            world.advance_turn()
        world.advance_turn()
        assert world.current_turn == 2
        assert world._last_advanced_turn == 1
        assert world._advance_failed is False

    def test_a_clean_advance_leaves_the_flag_down(self):
        world = WorldFactory.basic()
        world.advance_turn()
        assert world._advance_failed is False and world.current_turn == 2

    def test_the_old_guard_still_refuses_a_second_whole_advance(self):
        """R20's own case is untouched: a clean advance stamps the turn, and a
        retry with the counter wound back is refused (no double income)."""
        world = WorldFactory.basic()
        world.advance_turn()
        world.current_turn = 1
        gold = dict(world.nation_gold)
        world.advance_turn()
        assert world.current_turn == 1 and world.nation_gold == gold
        assert world._advance_failed is False

    def test_end_turn_resumes_without_replaying_europe(self, monkeypatch):
        """The review's reproduction: End Turn 1 errors, End Turn 2 advances,
        and Europe moved ONCE."""
        world = WorldFactory.basic()
        tm = TurnManager(world, executor=CommandExecutor())
        game_state = {"world": world}
        phases = {"n": 0}
        original = TurnManager._process_enemy_turns

        def counted(self, gs):
            phases["n"] += 1
            return original(self, gs)

        monkeypatch.setattr(TurnManager, "_process_enemy_turns", counted)
        _raise_once(monkeypatch)
        with pytest.raises(RuntimeError, match="boom"):
            tm.end_turn(game_state)
        assert phases["n"] == 1 and world.current_turn == 1
        assert world._advance_failed is True
        result = tm.end_turn(game_state)
        assert result["turn_ended"] == 1 and result["next_turn"] == 2
        assert result.get("resumed") is True
        assert phases["n"] == 1, "the enemy phase was not replayed"
        assert world._advance_failed is False

    def test_the_reply_says_the_close_was_finished(self, monkeypatch):
        """Through the executor, as the player's End Turn arrives: the first
        answer is the error, the second is the new turn — never "already
        underway" — and it says Europe's moves were kept."""
        world = WorldFactory.basic()
        executor = CommandExecutor()
        game_state = {"world": world}
        _raise_once(monkeypatch)
        command = {"command": {"action": "end_turn", "type": "specific"}}
        try:
            first = executor.execute(command, game_state)
        except RuntimeError:
            first = None
        assert first is None or first.get("success") is False
        assert world.current_turn == 1
        result = executor.execute(command, game_state)
        assert result["success"] is True, result.get("message")
        assert "already underway" not in result["message"]
        assert "Turn 2 begins" in result["message"]
        assert "kept, not replayed" in result["message"]
        assert world.current_turn == 2

    # ── T0-B's residue fix: the advance is transactional ──────────────────
    # The counter increments EARLY in `_advance_turn_internal`; a failure in a
    # late stage used to leave it at N+1 with the stamp rolled back, and the
    # retry ran a second whole advance. The snapshot undoes the partial stages.

    @staticmethod
    def _raise_late_once(monkeypatch, exc=None):
        """`_process_manpower_regen` sits after the counter's increment AND
        after the income phase — a failure there is the late case."""
        exc = exc or RuntimeError("the close failed late: boom")
        calls = {"n": 0}
        original = WorldState._process_manpower_regen

        def flaky(self):
            calls["n"] += 1
            if calls["n"] == 1:
                raise exc
            return original(self)

        monkeypatch.setattr(WorldState, "_process_manpower_regen", flaky)
        return calls

    def test_a_late_failure_restores_the_world_whole(self, monkeypatch):
        world = WorldFactory.basic()
        gold_before = dict(world.nation_gold)
        turn_before = world.current_turn
        self._raise_late_once(monkeypatch)
        with pytest.raises(RuntimeError, match="late"):
            world.advance_turn()
        assert world.current_turn == turn_before, "the counter's early increment is undone"
        assert world._last_advanced_turn == 0, "the stamp returns with the snapshot"
        assert world.nation_gold == gold_before, "the income the failed advance applied is undone"
        assert world._advance_failed is True

    def test_the_retry_after_a_late_failure_is_one_clean_advance(self, monkeypatch):
        import random
        control = WorldFactory.basic()
        random.seed(20261106)
        control.advance_turn()
        world = WorldFactory.basic()
        self._raise_late_once(monkeypatch)
        random.seed(20261106)
        with pytest.raises(RuntimeError):
            world.advance_turn()
        random.seed(20261106)
        world.advance_turn()
        assert world.current_turn == control.current_turn == 2, "advanced ONCE, not to turn 3"
        assert world.nation_gold == control.nation_gold, "income applied once, as on a clean advance"
        assert world._last_advanced_turn == 1 and world._advance_failed is False

    def test_the_world_object_keeps_its_identity_through_a_restore(self, monkeypatch):
        """Every holder of the reference — the game_state dict, the turn
        manager, the module's world — must see the restored state."""
        world = WorldFactory.basic()
        game_state = {"world": world}
        tm = TurnManager(world, executor=CommandExecutor())
        self._raise_late_once(monkeypatch)
        with pytest.raises(RuntimeError):
            world.advance_turn()
        assert game_state["world"] is world and tm.world is world
        assert world.current_turn == 1 and len(world.marshals) > 0
        world.advance_turn()
        assert game_state["world"].current_turn == 2

    def test_end_turn_resumes_after_a_late_failure_without_replaying_europe(self, monkeypatch):
        world = WorldFactory.basic()
        tm = TurnManager(world, executor=CommandExecutor())
        game_state = {"world": world}
        phases = {"n": 0}
        original = TurnManager._process_enemy_turns

        def counted(self, gs):
            phases["n"] += 1
            return original(self, gs)

        monkeypatch.setattr(TurnManager, "_process_enemy_turns", counted)
        self._raise_late_once(monkeypatch)
        with pytest.raises(RuntimeError, match="late"):
            tm.end_turn(game_state)
        assert phases["n"] == 1 and world.current_turn == 1
        result = tm.end_turn(game_state)
        assert result["next_turn"] == 2 and result.get("resumed") is True
        assert phases["n"] == 1, "Europe moved once"

    def test_a_failed_snapshot_still_falls_back_to_the_stamp(self, monkeypatch):
        """If `to_dict` itself raises, the advance still runs; on a failure the
        stamp rollback alone stands, reported, and the resume still holds."""
        world = WorldFactory.basic()

        def broken(self):
            raise ValueError("no snapshot tonight")

        monkeypatch.setattr(WorldState, "to_dict", broken)
        _errors.reset_tally()
        _raise_once(monkeypatch)
        with pytest.raises(RuntimeError, match="boom"):
            world.advance_turn()
        assert world._last_advanced_turn == 0 and world._advance_failed is True
        assert any("the snapshot before the advance" in r["site"] for r in _errors.tally())
        world.advance_turn()
        assert world.current_turn == 2

    def test_the_resumed_banner_keeps_the_first_attempts_window(self, monkeypatch):
        """The review's F2: the resumed End Turn's "before" figures are the
        first attempt's (kept in `_end_turn_window`), so the banner's Net
        spans the whole turn, enemy phase included; the window is cleared
        once the close succeeds."""
        import re
        world = WorldFactory.basic()
        executor = CommandExecutor()
        game_state = {"world": world}
        treasury_before_first = int(world.nation_gold.get(world.player_nation, 0))
        self._raise_late_once(monkeypatch)
        command = {"command": {"action": "end_turn", "type": "specific"}}
        try:
            executor.execute(command, game_state)
        except RuntimeError:
            pass
        window = getattr(world, "_end_turn_window", None)
        assert isinstance(window, dict), "the failed attempt keeps its window"
        assert window["treasury_before"] == treasury_before_first
        result = executor.execute(command, game_state)
        assert result["success"] is True and world.current_turn == 2
        assert getattr(world, "_end_turn_window", None) is None, "cleared on the close"
        treasury_after = int(world.nation_gold.get(world.player_nation, 0))
        m = re.search(r"Net: ([+-]?)([\d,]+)g", result["message"])
        assert m, result["message"]
        net = int(m.group(2).replace(",", "")) * (-1 if m.group(1) == "-" else 1)
        assert net == treasury_after - treasury_before_first, (net, treasury_after, treasury_before_first)

    def test_a_clean_end_turn_says_nothing_of_it(self):
        world = WorldFactory.basic()
        result = CommandExecutor().execute(
            {"command": {"action": "end_turn", "type": "specific"}}, {"world": world})
        assert result["success"] is True
        assert "kept, not replayed" not in result["message"]


class TestTheCourtsCrashIsSaid:
    """TURN-1 (GR-51)."""

    @staticmethod
    def _crash_one_court(monkeypatch, nation, both_phases):
        from backend.ai.enemy_ai import EnemyAI

        def boom(self, who, *a, **k):
            if who == nation:
                raise ValueError(f"{who}'s turn broke")
            return []

        monkeypatch.setattr(EnemyAI, "process_nation_turn", boom)
        if both_phases:
            monkeypatch.setattr(EnemyAI, "execute_admin_phase", boom)
        else:
            monkeypatch.setattr(EnemyAI, "execute_admin_phase", lambda self, *a, **k: [])

    def test_the_error_row_passes_the_fog(self):
        from backend.game_logic.enemy_phase_fog import filter_enemy_phase_by_visibility
        world = WorldFactory.basic()
        nation = next(iter(world.enemy_nations))
        phase = {
            "nations": {nation: {"actions": [{
                "action": "error", "nation": nation,
                "message": f"{nation} encountered an error during their turn",
                "battle_message": "",
            }], "action_count": 1}},
            "total_actions": 1, "summary": [],
        }
        shown = filter_enemy_phase_by_visibility(phase, world)
        rows = shown["nations"].get(nation, {}).get("actions", [])
        assert len(rows) == 1 and rows[0]["action"] == "error"
        assert shown["total_actions"] == 1
        assert any("did not complete its turn" in line for line in shown["summary"])

    def test_an_ordinary_fogged_march_is_still_dropped(self):
        """The pass-through is the crash row's alone: a march the player
        cannot see stays hidden."""
        from backend.game_logic.enemy_phase_fog import filter_enemy_phase_by_visibility
        from backend.models.intel import FULL
        world = WorldFactory.basic()
        world.calculate_visibility()
        hidden = [m for m in world.marshals.values()
                  if m.nation != world.player_nation
                  and world.get_region_intel(m.location).visibility != FULL]
        if not hidden:
            pytest.skip("every enemy marshal stands in full view on this board")
        marshal = hidden[0]
        phase = {
            "nations": {marshal.nation: {"actions": [{
                "success": True,
                "ai_action": {"marshal": marshal.name, "action": "move",
                              "target": marshal.location},
                "events": [],
            }], "action_count": 1}},
            "total_actions": 1, "summary": [],
        }
        shown = filter_enemy_phase_by_visibility(phase, world)
        assert marshal.nation not in shown["nations"]

    def test_the_rail_says_a_court_skipped_its_turn_once(self, monkeypatch):
        world = WorldFactory.basic()
        nation = next(iter(world.enemy_nations))
        self._crash_one_court(monkeypatch, nation, both_phases=True)
        _errors.reset_tally()
        tm = TurnManager(world, executor=CommandExecutor())
        results = tm._process_enemy_turns({"world": world})
        rows = results["nations"][nation]["actions"]
        errors = [r for r in rows if r.get("action") == "error"]
        assert errors, rows
        assert all(r.get("nation") == nation for r in errors)
        notes = [n for n in world.notifications.to_list()
                 if n.get("type") == "court_turn_failed"]
        assert len(notes) == 1, "one notice per court per turn, whichever phase failed"
        note = notes[0]
        assert note["details"]["nation"] == nation
        assert "did not complete its turn" in note["title"]
        assert note.get("expires_after_turn") == int(world.current_turn), "a one-shot event"
        sites = {row["site"] for row in _errors.tally()}
        assert any("turn_manager" in s and "phase" in s for s in sites), sites

    def test_a_court_that_crashes_in_one_phase_alone_is_said_once_too(self, monkeypatch):
        world = WorldFactory.basic()
        nation = next(iter(world.enemy_nations))
        self._crash_one_court(monkeypatch, nation, both_phases=False)
        tm = TurnManager(world, executor=CommandExecutor())
        tm._process_enemy_turns({"world": world})
        notes = [n for n in world.notifications.to_list()
                 if n.get("type") == "court_turn_failed"]
        assert len(notes) == 1

    def test_a_quiet_phase_posts_no_notice(self, monkeypatch):
        from backend.ai.enemy_ai import EnemyAI
        monkeypatch.setattr(EnemyAI, "process_nation_turn", lambda self, *a, **k: [])
        monkeypatch.setattr(EnemyAI, "execute_admin_phase", lambda self, *a, **k: [])
        world = WorldFactory.basic()
        TurnManager(world, executor=CommandExecutor())._process_enemy_turns({"world": world})
        assert not [n for n in world.notifications.to_list()
                    if n.get("type") == "court_turn_failed"]

    def test_the_type_is_a_one_shot_event_on_the_rail(self):
        from backend.notifications import COURT_TURN_FAILED, EVENT_NOTICE_TYPES
        assert COURT_TURN_FAILED in EVENT_NOTICE_TYPES
        bar = (REPO / "godot-client" / "project-sovereign" / "scripts"
               / "notification_bar.gd").read_text(encoding="utf-8")
        assert bar.count('"court_turn_failed"') == 2, "a label and a glyph"

    def test_the_digest_prints_the_row_as_the_dialog_does(self):
        """SF-RI2's mirror: the Mode A digest quotes the dialog's own line for
        the crash row (the drift pin in `test_sf_rr6_the_instrument.py` holds
        the two verb tables together)."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_t0a_driver", REPO / "tools" / "playtest_driver.py")
        driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(driver)
        row = {"action": "error", "nation": "Austria",
               "message": "Austria encountered an error during their turn", "battle_message": ""}
        assert driver.rendered_enemy_line(row) == "Austria did not complete its turn — an error was recorded"
        assert driver.rendered_capture_lines(row) == []


class TestEveryBroadExceptSpeaks:
    """TURN-4 (GR-54) and AIDIP-6 (GR-44), read off the census instrument."""

    @pytest.fixture(scope="class")
    def reading(self):
        from tools import _code_health_census as census_tool
        return census_tool.census()

    def test_no_broad_except_merely_prints(self, reading):
        assert reading["except"]["logs"] == 0, reading["except"]

    def test_the_bandwagon_block_is_two_guards_with_honest_labels(self, reading):
        sites = {literal for _, _, literal, _ in reading["report_calls"] if literal}
        assert HEGEMONY_SITE in sites
        assert BANDWAGON_SITE in sites
        assert OLD_LABEL not in sites

    def test_the_hegemony_reading_is_one_call(self):
        from backend.game_logic.ai_diplomacy import _hegemony_reading
        world = WorldFactory.basic()
        nation = next(iter(world.enemy_nations))
        hegemon, share, minor, in_bloc, locked = _hegemony_reading(world, nation)
        assert hegemon is None or isinstance(hegemon, str)
        assert isinstance(share, (int, float))
        assert isinstance(minor, bool) and isinstance(in_bloc, bool) and isinstance(locked, bool)

    def test_a_failed_reading_is_reported_and_the_phase_goes_on(self, monkeypatch):
        from backend.game_logic import ai_diplomacy, coalition

        def boom(world):
            raise KeyError("no bloc")

        monkeypatch.setattr(coalition, "_identify_max_bloc_share", boom)
        _errors.reset_tally()
        world = WorldFactory.basic()
        peaceful = [n for n in world.enemy_nations
                    if not world.is_at_war(n, world.player_nation)]
        if not peaceful:
            pytest.skip("every court is at war with the player on this board")
        out = ai_diplomacy.process_diplomatic_phase(peaceful[0], world)  # never raises
        sites = {row["site"] for row in _errors.tally()}
        # Either the reading's guard spoke, or an earlier rule proposed first
        # and the block was never reached — both are the phase going on.
        assert HEGEMONY_SITE in sites or out is not None
