"""DD-C "Nothing fails silently" — the save path speaks (Pre-Deploy S7b, October 12, 2026).

`docs/PRE_DEPLOY_PLAN.md` §3 DD-C (the weak spot, the instrument, the
done-when); `docs/CODE_HEALTH_PLAN.md` §CODE-3 (the `backend/errors.py`
contract); rules `docs/SYSTEMS_REFERENCE.md` §110.

FA-S15-1 broke every save for the rest of a campaign and only the server
console knew; FA-S15-2 put the AUTOSAVE's failure on the rail. What was still
silent, measured on `91c85e43`: a manual save's and a load's failure reached
the player as the raw OS error (with its filesystem path) and reached no log
at all; a corrupt save vanished from the Load menu without a word (and
Continue silently resumed an older one); a failed Final save said nothing on
either of its roads; and the client printed "Save failed: Save failed: …".

Here: every failure is a typed `save_manager.SaveError` raised by the stage
that met it and converted at the door, logged at WARNING with its site,
handed back as a sentence (a filename at most, never a path); the Load menu
lists what it cannot read; the instrument (`tools/save_faults.py`, the
driver's `--save-faults`) injects one fault a turn over forty turns and
checks the sentence, the log, the untouched world, the recovery and the round
trip `to_dict(from_dict(x)) == x` on every autosave.
"""
from __future__ import annotations

import ast
import contextlib
import errno
import io
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import errors, notifications
from backend import save_manager as SM
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json")
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.records = []

    def emit(self, record):
        self.records.append(record)


@pytest.fixture
def records():
    """Every WARNING the reporter writes during the test, as records."""
    cap = _Capture()
    log = logging.getLogger(errors.LOGGER_NAME)
    log.addHandler(cap)
    try:
        yield cap.records
    finally:
        log.removeHandler(cap)


@pytest.fixture
def client(monkeypatch, tmp_path):
    """A real `/command` surface on a fresh 1805 boot, saves sandboxed (the
    FA-S15-2 fixture)."""
    monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path / "saves"))
    monkeypatch.setattr(SM, "SAVE_DIR", tmp_path / "saves")
    world = _quiet(WorldState.from_scenario, SCENARIO)
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "game_state", {"world": world})
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), world


class _FullDisk:
    JSONDecodeError = json.JSONDecodeError
    load = staticmethod(json.load)
    loads = staticmethod(json.loads)
    dumps = staticmethod(json.dumps)

    @staticmethod
    def dump(obj, fp, *a, **k):
        fp.write("{\n")
        raise OSError(errno.ENOSPC, "No space left on device")


def _rows(world):
    return [n for n in world.notifications.to_list()
            if n.get("type") == notifications.SAVE_FAILED]


def _messages(records):
    return [r.getMessage() for r in records]


# ═══════════════════════════════════════════════════════════════════════════
# The reporter (`backend/errors.py`)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheReporter:

    @pytest.fixture(autouse=True)
    def _fresh(self):
        errors.reset_tally()
        yield
        errors.reset_tally()

    def test_a_site_logs_once_and_counts_every_call(self, records):
        for i in range(5):
            try:
                {}["missing"]
            except KeyError as exc:
                errors.report(exc, "dd_c.test: a per-turn loop")
        assert len(records) == 1
        assert records[0].levelno == logging.WARNING
        assert "dd_c.test: a per-turn loop" in records[0].getMessage()
        row = next(r for r in errors.tally() if r["site"] == "dd_c.test: a per-turn loop")
        assert row["count"] == 5 and row["first"].startswith("KeyError")

    def test_every_logs_each_call(self, records):
        for _ in range(3):
            errors.report(ValueError("x"), "dd_c.test: a player's own click", every=True)
        assert len(records) == 3

    def test_the_stack_never_says_the_word_the_score_gate_reads_as_a_crash(self, records):
        """`tools/score_run.py` fails `ai_aliveness.F2` on "Traceback" in an
        arm's log, and the in-process driver sends this logger's stderr into
        that log: the stack is printed with its frames and its causes, under
        another heading."""
        try:
            try:
                int("not a number")
            except ValueError as inner:
                raise RuntimeError("outer") from inner
        except RuntimeError as exc:
            errors.report(exc, "dd_c.test: a chained failure")
        text = records[0].getMessage()
        assert "Traceback" not in text
        assert "stack (most recent call last)" in text
        assert "caused by ValueError" in text
        assert 'int("not a number")' in text

    def test_a_record_holds_strings_only(self, records):
        """The record never keeps the frames — a captured record must not keep
        a world alive."""
        errors.report(RuntimeError("held?"), "dd_c.test: the record's payload")
        rec = records[0]
        assert rec.exc_info is None
        assert all(isinstance(a, str) for a in (rec.args or ()))

    def test_report_never_raises_even_on_a_broken_exception(self, records):
        class Broken(Exception):
            def __str__(self):
                raise RuntimeError("no words")
        errors.report(Broken(), "dd_c.test: a broken __str__")   # must not raise

    def test_swallow_reports_drops_and_notifies(self, records):
        seen = []
        with errors.swallow("dd_c.test: swallowed", notify=seen.append):
            raise KeyError("k")
        assert len(seen) == 1 and isinstance(seen[0], KeyError)
        assert any("dd_c.test: swallowed" in m for m in _messages(records))

    def test_a_notify_that_raises_is_reported_not_raised(self, records):
        def boom(_exc):
            raise ValueError("the notice broke")
        with errors.swallow("dd_c.test: swallowed twice", notify=boom):
            raise KeyError("k")
        assert any("dd_c.test: swallowed twice (the notice)" in m for m in _messages(records))

    def test_the_debug_command_lists_the_tally(self):
        """`/debug errors`: the tally every report counts into, most frequent
        first, each site's first exception beside it."""
        from backend.commands.executor import CommandExecutor
        errors.report(KeyError("k"), "dd_c.test: listed by the debug command")
        errors.report(KeyError("k"), "dd_c.test: listed by the debug command")
        res = CommandExecutor()._meta._execute_debug(
            {"target": "errors"}, {"world": WorldState(player_nation="France"), "debug_mode": True})
        assert res["success"] is True
        assert "dd_c.test: listed by the debug command" in res["message"]
        assert "2×" in res["message"] and "KeyError" in res["message"]

    def test_debug_fields_only_when_the_caller_says_debug(self):
        exc = RuntimeError("x")
        assert errors.debug_fields(exc, "main.save_endpoint: the save route", False) == {}
        assert errors.debug_fields(exc, "main.save_endpoint: the save route", True) == {
            "debug_error": {"class": "RuntimeError", "site": "main.save_endpoint: the save route"}}


# ═══════════════════════════════════════════════════════════════════════════
# A save that fails says so — the sentence, the log, the untouched slot
# ═══════════════════════════════════════════════════════════════════════════

class TestTheSaveSpeaks:

    def test_a_full_disk_reaches_the_player_and_the_log(self, client, monkeypatch, records):
        tc, _world = client
        monkeypatch.setattr(SM, "json", _FullDisk)
        body = tc.post("/save", json={"save_name": "dd_c"}).json()
        assert body["success"] is False
        assert body["message"] == "Save failed — the disk is full. Free some space and save again."
        assert any(m.startswith("save_manager.save_game: writing the file")
                   for m in _messages(records))

    def test_a_failed_write_leaves_the_old_save_whole_and_no_temp_file(self, client, monkeypatch):
        tc, world = client
        assert tc.post("/save", json={"save_name": "dd_c"}).json()["success"] is True
        path = SM.SAVE_DIR / "dd_c.json"
        good = path.read_bytes()
        monkeypatch.setattr(SM, "json", _FullDisk)
        assert tc.post("/save", json={"save_name": "dd_c"}).json()["success"] is False
        assert path.read_bytes() == good
        assert not list(SM.SAVE_DIR.glob("*.tmp"))

    def test_the_sentence_never_carries_a_path(self, client, monkeypatch):
        """The FA-S15-2 row carried the raw OS error, path and all, into every
        later save; the sentence is the OS's words, never its filename."""
        tc, world = client
        secret = str(SM.SAVE_DIR / "dd_c.tmp")

        def refused():
            raise PermissionError(errno.EACCES, "Access is denied", secret)

        monkeypatch.setattr(SM, "ensure_save_dir", refused)
        body = tc.post("/save", json={"save_name": "dd_c"}).json()
        assert body["message"] == ("Save failed — the saves folder cannot be written "
                                   "to (permission denied).")
        tc.post("/command", json={"command": "end turn"})
        row = _rows(world)[0]
        assert secret not in row["message"] and secret not in json.dumps(row["details"])
        assert "permission denied" in row["message"]

    def test_a_planted_value_names_its_own_field_in_the_log(self, client, records):
        tc, world = client
        ney = world.marshals["Ney"]
        prior = ney.original_nation
        ney.original_nation = object()
        try:
            body = tc.post("/save", json={"save_name": "dd_c"}).json()
        finally:
            ney.original_nation = prior
        assert body["success"] is False
        assert "could not be written down" in body["message"]
        assert "world_state" not in body["message"]          # the path is the log's
        assert any("world_state.marshals.Ney.original_nation (object)" in m
                   for m in _messages(records))

    def test_fa_s15_1s_own_shape_reaches_the_rail_through_a_real_end_turn(self, client, records):
        """The P1 this row exists for: a SERIALIZED field deleted at runtime,
        `Marshal.to_dict` reading it bare — every save fails until it is
        back. The end turn goes on, the rail says so in words, the log names
        the stage."""
        tc, world = client
        ney = world.marshals["Ney"]
        prior = ney.original_nation
        delattr(ney, "original_nation")
        try:
            before = world.current_turn
            body = tc.post("/command", json={"command": "end turn"}).json()
        finally:
            ney.original_nation = prior
        assert world.current_turn > before
        assert body.get("success") is True
        rows = [n for n in body.get("notifications") or []
                if n.get("type") == notifications.SAVE_FAILED]
        assert len(rows) == 1
        assert "could not be written down" in rows[0]["message"]
        assert "stale" in rows[0]["message"].lower()       # FA-S15-2's copy kept
        assert any(m.startswith("save_manager.save_game: reading the world")
                   and "AttributeError" in m for m in _messages(records))

    def test_the_autosave_row_carries_the_reason_not_the_os_text(self, client, monkeypatch):
        tc, world = client
        monkeypatch.setattr(SM, "json", _FullDisk)
        tc.post("/command", json={"command": "end turn"})
        row = _rows(world)[0]
        assert row["details"]["detail"] == "The disk is full. Free some space and save again."
        assert "Errno" not in row["message"]


# ═══════════════════════════════════════════════════════════════════════════
# A load that fails says so — and the campaign on the table is untouched
# ═══════════════════════════════════════════════════════════════════════════

class TestTheLoadSpeaks:

    def _truncated(self, tc, name="dd_c"):
        assert tc.post("/save", json={"save_name": name}).json()["success"] is True
        path = SM.SAVE_DIR / f"{name}.json"
        raw = path.read_bytes()
        path.write_bytes(raw[: len(raw) // 2])
        return path

    def test_a_cut_short_save_is_named_corrupt_and_the_world_stays(self, client, records):
        tc, world = client
        self._truncated(tc)
        turn = world.current_turn
        body = tc.post("/load", json={"filename": "dd_c.json"}).json()
        assert body["success"] is False
        assert body["message"] == ("Load failed — the save file is corrupt and cannot be "
                                   "read; it may have been cut short while it was written.")
        assert M.world is world and world.current_turn == turn
        assert any(m.startswith("save_manager.load_game: reading the file")
                   for m in _messages(records))

    def test_a_damaged_file_is_listed_not_dropped(self, client, records):
        """It used to vanish from the Load menu without a word; Continue then
        resumed whatever older save came next."""
        tc, _world = client
        self._truncated(tc)
        listing = tc.get("/saves").json()
        assert "success" not in listing                       # the menu gates on shape
        assert [s["filename"] for s in listing["saves"]] == []
        assert [d["filename"] for d in listing["damaged"]] == ["dd_c.json"]
        assert "corrupt" in listing["damaged"][0]["message"]
        assert listing["damaged"][0]["saved_at"]
        assert SM.list_saves() == []                          # its contract kept
        assert any("save_manager.list_saves" in m for m in _messages(records))

    def test_a_rebuild_that_fails_names_itself(self, client, monkeypatch, records):
        tc, world = client
        assert tc.post("/save", json={"save_name": "dd_c"}).json()["success"] is True

        def broken(cls, data):
            raise KeyError("a field the loader expected")

        monkeypatch.setattr(WorldState, "from_dict", classmethod(broken))
        body = tc.post("/load", json={"filename": "dd_c.json"}).json()
        assert body["success"] is False
        assert body["message"].startswith("Load failed — the campaign in this save could not be rebuilt (KeyError)")
        assert "Your current campaign is untouched." in body["message"]
        assert M.world is world
        assert any(m.startswith("save_manager.load_game: rebuilding the campaign")
                   for m in _messages(records))

    def test_a_missing_file_is_named_by_its_filename_only(self, client):
        tc, _world = client
        res = SM.load_game(SM.SAVE_DIR / "gone.json")
        assert res["message"] == "Load failed — save file not found: gone.json"
        assert str(SM.SAVE_DIR) not in res["message"]


# ═══════════════════════════════════════════════════════════════════════════
# The Final save — the record of a fallen campaign — no longer fails mute
# ═══════════════════════════════════════════════════════════════════════════

class TestTheFinalSaveSpeaks:

    def test_a_failed_final_save_reaches_the_rail(self, client, monkeypatch, records):
        tc, world = client
        record = {"tier": "fall", "terminal": True, "turn": 9,
                  "calendar_label": "June 1806", "final_save": None}
        from backend.game_logic import game_end
        monkeypatch.setattr(game_end, "close_campaign", lambda w: record)
        monkeypatch.setattr(game_end, "terminal_ending", lambda w: record)
        monkeypatch.setattr(SM, "json", _FullDisk)
        res = SM.write_final_save(world)
        assert res["success"] is False
        assert record["final_save"] is None                  # rolled back
        rows = _rows(world)
        assert len(rows) == 1
        assert rows[0]["title"] == "The campaign's Final save could not be written"
        assert "disk is full" in rows[0]["message"]


# ═══════════════════════════════════════════════════════════════════════════
# A route's own failure carries its class and site — in a debug build only
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRouteNamesWhatBroke:

    def _boom(self, *a, **k):
        raise RuntimeError("the route's own failure")

    def test_in_a_debug_build(self, client, monkeypatch, records):
        tc, _world = client
        monkeypatch.setattr(M, "DEBUG_MODE", True)
        monkeypatch.setattr(M, "save_game", self._boom)
        body = tc.post("/save", json={"save_name": "dd_c"}).json()
        assert body["success"] is False
        assert body["debug_error"] == {"class": "RuntimeError",
                                       "site": "main.save_endpoint: the save route"}
        assert any(m.startswith("main.save_endpoint: the save route") for m in _messages(records))

    def test_never_in_production(self, client, monkeypatch):
        tc, _world = client
        monkeypatch.setattr(M, "DEBUG_MODE", False)
        monkeypatch.setattr(M, "save_game", self._boom)
        body = tc.post("/save", json={"save_name": "dd_c"}).json()
        assert body["success"] is False and "debug_error" not in body


# ═══════════════════════════════════════════════════════════════════════════
# The client shows it (static: the arms render the backend's sentence)
# ═══════════════════════════════════════════════════════════════════════════

def _gd_func(path, name):
    src = path.read_text(encoding="utf-8")
    return src.split(f"func {name}", 1)[1].split("\nfunc ", 1)[0]


class TestTheClientShowsIt:

    def test_the_pause_save_prints_the_sentence_once(self):
        body = _gd_func(SCRIPTS / "main.gd", "_on_pause_save_result")
        assert "_failure_line(" in body
        helper = _gd_func(SCRIPTS / "main.gd", "_failure_line")
        assert "begins_with" in helper            # the prefix is added only when absent

    def test_the_load_prints_the_sentence_once(self):
        assert "_failure_line(" in _gd_func(SCRIPTS / "main.gd", "_on_load_result")

    def test_continue_names_a_damaged_newer_file(self):
        body = _gd_func(SCRIPTS / "main.gd", "_on_continue_saves_listed")
        assert 'response.get("damaged"' in body
        assert 'response.get("saves"' in body and "if response.success" not in body

    def test_the_load_dialog_lists_what_it_cannot_read(self):
        body = _gd_func(SCRIPTS / "load_dialog.gd", "show_saves")
        assert "damaged" in body and "disabled = true" in body
        listed = _gd_func(SCRIPTS / "main.gd", "_on_saves_listed")
        assert 'response.get("damaged"' in listed


# ═══════════════════════════════════════════════════════════════════════════
# The census: the save path, the serializer, the routes and the parser's
# client hold no silent handler (CODE-3's done-when)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheCensusHolds:

    @pytest.fixture(scope="class")
    def reading(self):
        sys.path.insert(0, str(REPO))
        from tools import _code_health_census as census
        return census.census()

    @pytest.mark.parametrize("path", ["backend/save_manager.py",
                                      "backend/main.py",
                                      "backend/notifications.py"])
    def test_no_silent_handler_in(self, reading, path):
        assert [s for s in reading["silent_sites"]
                if s[0].replace("\\", "/") == path] == []

    def test_the_census_sees_a_broad_tuple(self):
        """`except (json.JSONDecodeError, Exception)` swallowed in
        `list_saves` while the census looked only at a bare name."""
        sys.path.insert(0, str(REPO))
        from tools import _code_health_census as census
        handler = ast.parse("try:\n    x()\nexcept (ValueError, Exception):\n    pass\n").body[0].handlers[0]
        assert census.is_broad(handler.type)
        assert not census.is_broad(ast.parse("try:\n    x()\nexcept (ValueError, KeyError):\n    pass\n").body[0].handlers[0].type)


# ═══════════════════════════════════════════════════════════════════════════
# The instrument: forty turns, one fault a turn (the driver's --save-faults)
# ═══════════════════════════════════════════════════════════════════════════

class TestFortyTurns:

    @pytest.fixture(scope="class")
    def run(self, tmp_path_factory):
        out = tmp_path_factory.mktemp("dd_c_run")
        env = dict(os.environ)
        env.pop("PYTHONIOENCODING", None)
        env["INK_IRON_SAVE_DIR"] = str(out / "saves_env")
        # The commanded forty-turn script: the default policy's passive
        # France falls by turn 34 (The Eclipse), so its run ends early.
        proc = subprocess.run(
            [sys.executable, str(REPO / "tools" / "playtest_driver.py"),
             "--script", str(REPO / "tools" / "playtest_scripts" / "commanded_full40.json"),
             "--turns", "40", "--name", "dd_c", "--out", str(out), "--save-faults", "--fresh"],
            cwd=REPO, env=env, capture_output=True, text=True, timeout=1500,
            stdin=subprocess.DEVNULL)
        assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
        return json.loads((out / "dd_c" / "save_faults.json").read_text(encoding="utf-8"))

    def test_every_injected_fault_reached_the_player_and_the_log(self, run):
        s = run["summary"]
        assert s["failures"] == [], s["failures"][:3]
        assert s["probes"] == 40 and s["ok"] == s["probes"]

    def test_every_kind_was_injected_on_the_campaign(self, run):
        by = run["summary"]["by_kind"]
        assert set(by) == {"disk_full", "unserializable", "truncated"}
        assert all(v["probes"] >= 13 for v in by.values()), by
        shapes = {r.get("shape") for r in run["rows"] if r["kind"] == "unserializable"}
        assert shapes == {"planted", "delattr"}

    def test_the_round_trip_holds_on_every_autosave(self, run):
        s = run["summary"]
        assert s["round_trips_equal"] == s["probes"]
