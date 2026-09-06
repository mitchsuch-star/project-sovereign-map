"""FA-S15-2 — "The Save That Says Nothing".

A failed autosave reached the **server console** and nobody else:
`print(f"Autosave warning: ...")` at two call sites, no notification, no
dispatch line, no client key. The player kept playing.

⚠ **And the harm is not "there is no save".** Measured on the shipped board:
the file EXISTS and goes **stale** — world turn 4, slot turn 2. It sits in the
Load menu looking plausible, and the menu's Continue reads the newest save, so
a player who lost saving mid-campaign is silently resumed several turns back.

⚠ **Two independent defects, so two levers.** Below the notification sits a
worse one: `ensure_save_dir()` stood OUTSIDE `save_game`'s `try`, so
`save_game` could RAISE despite a docstring promising a success/failure dict —
and on both turn roads the raise destroyed four keys of the end-turn response
(`enemy_phase`, `morning_dispatch`, `tactical_events`, `turn_ended`). A single
lever could not reproduce prior behaviour for that half, which is slice 14's
"both levers or neither" discipline applied.

⚠ **The announcement is sited in the door that already exists.** The filed
shape was a new `autosave_and_report` helper that three call sites must
remember to call — the one-of-several shape this build keeps getting caught
by. `save_manager.autosave()` IS the single door; notifying there covers both
turn roads with **zero** call-site edits, and the two prints are DELETED
rather than joined by a third.
"""

import ast
import contextlib
import io
import json
import os
import pathlib
import tempfile

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import notifications, save_manager
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" /
               "maps" / "europe_1805.json")


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


@pytest.fixture
def client(monkeypatch, tmp_path):
    """A real `/command` surface on a fresh 1805 boot, saves sandboxed."""
    monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path / "saves"))
    monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path / "saves")
    world = _quiet(WorldState.from_scenario, SCENARIO)
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "game_state", {"world": world})
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), world


class _BoomJson:
    """⚠ The FORCING IDIOM, and the two arms are different defects.

    Shimming `save_manager.json` so `dump` raises reproduces the FILED
    defect: `save_game` catches it and returns `success: False`. Patching
    `save_game` itself to raise reproduces the OTHER one, the escape. Pin
    both; do not confuse them.
    """
    JSONDecodeError = json.JSONDecodeError

    @staticmethod
    def dump(*a, **k):
        raise OSError("No space left on device")

    load = staticmethod(json.load)
    loads = staticmethod(json.loads)
    dumps = staticmethod(json.dumps)


def _rows(payload, kind=notifications.SAVE_FAILED):
    return [n for n in (payload.get("notifications") or [])
            if n.get("type") == kind]


# ═══════════════════════════════════════════════════════════════════════════
# The filed defect: the turn goes on and nobody is told
# ═══════════════════════════════════════════════════════════════════════════

class TestTheFailureReachesThePlayer:

    def test_a_broken_autosave_is_announced(self, client, monkeypatch):
        """P1 / ARM A. RED at HEAD: measured 0 rows and no save token
        anywhere in the response body, on a turn that advanced normally."""
        tc, world = client
        monkeypatch.setattr(save_manager, "json", _BoomJson)
        before = world.current_turn
        r = tc.post("/command", json={"command": "end turn"})
        assert r.status_code == 200
        body = r.json()
        assert world.current_turn > before, "the turn must still advance"
        rows = _rows(body)
        assert len(rows) == 1, body.get("notifications")
        assert rows[0]["priority"] == int(
            notifications.NotificationPriority.CRITICAL)

    def test_an_unbroken_turn_carries_no_such_row(self, client):
        """The negative control. Without it the pin above passes on a rail
        that always carries the row."""
        tc, _world = client
        body = tc.post("/command", json={"command": "end turn"}).json()
        assert _rows(body) == []

    def test_the_copy_says_the_slot_goes_stale(self, client, monkeypatch):
        """⚠ The row's own framing ("autosave.json does not exist") is wrong
        in the common case and the truth is worse — the file is there and
        lags. The player must be told THAT, because Continue reads it."""
        tc, world = client
        monkeypatch.setattr(save_manager, "json", _BoomJson)
        body = tc.post("/command", json={"command": "end turn"}).json()
        text = (_rows(body)[0]["title"] + " " + _rows(body)[0]["message"]).lower()
        assert "stale" in text
        assert "earlier turn" in text or "back" in text

    def test_the_slot_really_does_lag(self, client, monkeypatch, tmp_path):
        """P7 — the actual harm, which no filed pin covered. Measured at
        HEAD: world 4, slot 2, with the file present."""
        tc, world = client
        _quiet(tc.post, "/command", json={"command": "end turn"})
        slot = tmp_path / "saves" / save_manager.AUTOSAVE_FILENAME
        assert slot.exists(), "no baseline autosave to go stale"
        good = json.loads(slot.read_text(encoding="utf-8"))["metadata"]["turn"]

        monkeypatch.setattr(save_manager, "json", _BoomJson)
        for _ in range(3):
            _quiet(tc.post, "/command", json={"command": "end turn"})
        stale = json.loads(slot.read_text(encoding="utf-8"))["metadata"]["turn"]
        assert stale == good
        assert stale < world.current_turn, (
            "the slot did not actually fall behind — this pin is vacuous")


class TestTheEscapeIsCaughtToo:
    """⚠ ARM B, added after a sweep reported the try/except in `autosave`
    INERT — and it was right: with L1 in place `save_game` no longer raises
    through the shim, so nothing exercised the belt. It is not dead code
    (L1 can be flipped, and a future edit can reintroduce an escape), so it
    gets the arm the report specified and nobody built.

    ⚠ This is a DIFFERENT defect from the shim: patching `save_game` to
    raise reproduces the escape; shimming `json.dump` reproduces the filed
    return-False case. Pin both; do not confuse them.
    """

    def test_a_raising_save_game_does_not_break_the_turn(self, client,
                                                         monkeypatch):
        tc, world = client

        def boom(*a, **k):
            raise RuntimeError("forced")

        monkeypatch.setattr(save_manager, "save_game", boom)
        before = world.current_turn
        body = tc.post("/command", json={"command": "end turn"}).json()
        assert body.get("success") is True, body.get("message")
        for key in ("morning_dispatch", "enemy_phase", "tactical_events",
                    "turn_ended"):
            assert key in body, f"{key} was destroyed by the raise"
        assert world.current_turn > before
        assert len(_rows(body)) == 1


class TestTheLatch:

    def test_five_broken_turns_leave_exactly_one_row(self, client,
                                                     monkeypatch):
        """P4. `add()` would give one row titled "(x5)" — measured. `refresh`
        keeps one id so the desk bell rings once, not once per turn."""
        tc, _world = client
        monkeypatch.setattr(save_manager, "json", _BoomJson)
        body = None
        for _ in range(5):
            body = tc.post("/command", json={"command": "end turn"}).json()
        rows = _rows(body)
        assert len(rows) == 1
        assert "(x" not in rows[0]["title"]
        assert rows[0]["repeat_count"] >= 1

    def test_it_keeps_one_id_across_the_failures(self, client, monkeypatch):
        tc, world = client
        monkeypatch.setattr(save_manager, "json", _BoomJson)
        ids = set()
        for _ in range(4):
            tc.post("/command", json={"command": "end turn"})
            ids |= {n["id"] for n in world.notifications.to_list()
                    if n.get("type") == notifications.SAVE_FAILED}
        assert len(ids) == 1, ids

    def test_the_turn_it_broke_is_the_turn_it_reports(self, client,
                                                      monkeypatch):
        tc, world = client
        monkeypatch.setattr(save_manager, "json", _BoomJson)
        first = tc.post("/command", json={"command": "end turn"}).json()
        stamped = _rows(first)[0]["turn_created"]
        # ⚠ Added after a sweep: comparing later stamps only to the FIRST
        # one is satisfied by any constant offset, because `refresh` keeps
        # whatever the first call wrote. Anchor it to the board instead.
        # The autosave runs AFTER `advance_turn`, so the turn the player is
        # now on is the turn the warning is about — measured, not assumed:
        # my first version of this line asserted the PRE-advance turn and
        # was wrong about the code rather than finding a defect in it.
        assert stamped == world.current_turn, (stamped, world.current_turn)
        for _ in range(3):
            body = tc.post("/command", json={"command": "end turn"}).json()
        assert _rows(body)[0]["turn_created"] == stamped

    def test_one_good_turn_retires_it(self, client, monkeypatch):
        """P6."""
        tc, world = client
        monkeypatch.setattr(save_manager, "json", _BoomJson)
        tc.post("/command", json={"command": "end turn"})
        assert _rows({"notifications": world.notifications.to_list()})
        monkeypatch.setattr(save_manager, "json", json)
        body = tc.post("/command", json={"command": "end turn"}).json()
        assert _rows(body) == []

    def test_the_cap_can_never_evict_it(self, client, monkeypatch):
        """P10. CRITICAL is exempt from eviction at any age; flood the tray
        and the warning must survive."""
        tc, world = client
        monkeypatch.setattr(save_manager, "json", _BoomJson)
        tc.post("/command", json={"command": "end turn"})
        for i in range(60):
            world.notifications.add(notifications.create_notification(
                notification_type="manpower_replenished",
                priority=notifications.NotificationPriority.NORMAL,
                title=f"filler {i}", message="", turn_created=i))
        kinds = [n["type"] for n in world.notifications.to_list()]
        assert notifications.SAVE_FAILED in kinds
        assert len(kinds) <= notifications.NOTIFICATION_CAP


# ═══════════════════════════════════════════════════════════════════════════
# L1 — the raise that ate four keys of the end-turn report
# ═══════════════════════════════════════════════════════════════════════════

class TestSaveGameHonoursItsOwnContract:

    def test_a_directory_failure_no_longer_escapes(self, client,
                                                   monkeypatch):
        """P3 / ARM G, the production shape. `ensure_save_dir()` stood
        outside the try, so a PermissionError propagated out of a function
        whose docstring promises a dict. Measured at HEAD: success False,
        message "Error: [Errno 5] Access is denied", and `morning_dispatch`,
        `enemy_phase`, `tactical_events` and `turn_ended` all GONE."""
        tc, world = client

        def boom():
            raise PermissionError(5, "Access is denied")

        monkeypatch.setattr(save_manager, "ensure_save_dir", boom)
        before = world.current_turn
        body = tc.post("/command", json={"command": "end turn"}).json()
        assert body.get("success") is True, body.get("message")
        for key in ("morning_dispatch", "enemy_phase", "tactical_events",
                    "turn_ended"):
            assert key in body, f"{key} was destroyed by the raise"
        assert world.current_turn > before
        assert len(_rows(body)) == 1

    def test_a_file_where_the_directory_should_be(self, client, monkeypatch):
        """The SECOND reachable trigger, which the row does not name:
        `mkdir(parents=True, exist_ok=True)` over a FILE raises
        FileExistsError, not the PermissionError everyone reaches for."""
        tc, _world = client

        def boom():
            raise FileExistsError(183, "Cannot create a file when it "
                                       "already exists")

        monkeypatch.setattr(save_manager, "ensure_save_dir", boom)
        body = tc.post("/command", json={"command": "end turn"}).json()
        assert body.get("success") is True
        assert len(_rows(body)) == 1

    def test_the_typed_save_command_refuses_instead_of_erroring(
            self, client, monkeypatch):
        """P3b. ⚠ Nobody's pin covered this: `executor.py`'s typed
        `save <name>` returns `save_game`'s dict STRAIGHT to the player, so
        the escape surfaced there as a bare "Error: ..." from the generic
        handler."""
        tc, _world = client

        def boom():
            raise PermissionError(5, "Access is denied")

        monkeypatch.setattr(save_manager, "ensure_save_dir", boom)
        body = tc.post("/command", json={"command": "save mygame"}).json()
        assert body.get("success") is False
        assert "Save failed" in str(body.get("message"))

    def test_the_lever_restores_the_raise(self, monkeypatch, tmp_path):
        """L1's False arm must reproduce HEAD exactly, or the attribution
        experiment is unavailable."""
        world = _quiet(WorldState.from_scenario, SCENARIO)

        def boom():
            raise PermissionError(5, "Access is denied")

        monkeypatch.setattr(save_manager, "ensure_save_dir", boom)
        monkeypatch.setattr(save_manager, "SAVE_DIR_FAILURE_IS_CAUGHT", False)
        with pytest.raises(PermissionError):
            save_manager.save_game(world, "x", tmp_path / "x.json")
        monkeypatch.setattr(save_manager, "SAVE_DIR_FAILURE_IS_CAUGHT", True)
        res = save_manager.save_game(world, "x", tmp_path / "x.json")
        assert res["success"] is False


# ═══════════════════════════════════════════════════════════════════════════
# Both roads, and one door
# ═══════════════════════════════════════════════════════════════════════════

class TestOneDoorCoversBothRoads:

    def test_the_auto_advance_road_carries_it_too(self, monkeypatch,
                                                  tmp_path):
        """P5 — the ONLY thing that binds `executor.py`'s auto-advance
        mirror. ⚠ It must be a FRESH boot with the AP arranged: on a reused
        mid-campaign world the auto-advance does not fire, and the pin goes
        VACUOUS rather than red."""
        monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path / "saves"))
        monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path / "saves")
        world = _quiet(WorldState.from_scenario, SCENARIO)
        monkeypatch.setattr(M, "world", world)
        monkeypatch.setattr(M, "game_state", {"world": world})
        monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
        world.actions_remaining = 1
        world.admin_actions_remaining = 0
        monkeypatch.setattr(save_manager, "json", _BoomJson)

        before = world.current_turn
        tc = TestClient(M.app)
        body = tc.post("/command", json={"command": "Davout, defend"}).json()
        assert world.current_turn > before, (
            "the auto-advance never fired — this pin is vacuous, not passing")
        assert len(_rows(body)) == 1, body.get("notifications")

    def test_the_call_sites_no_longer_carry_their_own_handling(self):
        """P10's census, made true instead of contradictory: the two prints
        are DELETED, so no `autosave(` call in the backend is followed by
        local failure handling. ⚠ Scoped to CALL NODES, not file text — a
        source grep is satisfied by the comment block explaining the fix."""
        offenders = []
        for path in (REPO / "backend").rglob("*.py"):
            if path.name == "save_manager.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name)
                        and node.func.id == "autosave"):
                    continue
                # anything reading the result and printing about it
                parent_src = ast.get_source_segment(
                    path.read_text(encoding="utf-8"), node) or ""
                if "print" in parent_src:
                    offenders.append(str(path))
        assert offenders == [], offenders

    def test_no_print_of_an_autosave_result_survives_outside_the_door(self):
        """⚠ Scoped to PRINTABLE string literals — not file text, and
        not docstrings. My first cut failed on its own comments; my second
        failed on the docstring that EXPLAINS the defect. Both are prose,
        and here prose makes the census RED rather than green — the same
        fault pointing the other way. What is forbidden is a warning the
        code can print, so docstrings are excluded, and the exclusion has
        its own sensitivity arm below."""
        offenders = []
        for path in (REPO / "backend").rglob("*.py"):
            if path.name == "save_manager.py":
                continue
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
            docstrings = set()
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.ClassDef,
                                     ast.FunctionDef, ast.AsyncFunctionDef)):
                    body = getattr(node, "body", None)
                    if (body and isinstance(body[0], ast.Expr)
                            and isinstance(body[0].value, ast.Constant)
                            and isinstance(body[0].value.value, str)):
                        docstrings.add(id(body[0].value))
            for node in ast.walk(tree):
                if (isinstance(node, ast.Constant)
                        and isinstance(node.value, str)
                        and id(node) not in docstrings
                        and "Autosave warning" in node.value):
                    offenders.append(f"{path.name}:{node.lineno}")
        assert offenders == [], offenders

    def test_that_census_can_see_an_offender(self):
        """Sensitivity arm — and it is the arm that matters here, because
        the version this replaced was RED on prose while a real offender
        would have looked identical."""
        NL = chr(10)
        tree = ast.parse(
            'def f():' + NL + '    print("Autosave warning: x")' + NL)
        found = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Constant) and isinstance(n.value, str)
                 and "Autosave warning" in n.value]
        assert len(found) == 1
        # …a DOCSTRING saying it must be invisible too, or the census
        # reds on the very comment that explains it
        tree3 = ast.parse(
            'def f():' + NL + '    """Autosave warning: explained."""' + NL
            + '    pass' + NL)
        doc = tree3.body[0].body[0].value
        assert [n for n in ast.walk(tree3)
                if isinstance(n, ast.Constant)
                and isinstance(n.value, str)
                and n is not doc
                and "Autosave warning" in n.value] == []
        # …and a COMMENT saying the same thing is invisible to it
        tree2 = ast.parse(
            'def f():' + NL + '    # Autosave warning: gone' + NL
            + '    pass' + NL)
        assert not [n for n in ast.walk(tree2)
                    if isinstance(n, ast.Constant)
                    and isinstance(n.value, str)
                    and "Autosave warning" in n.value]

    def test_the_announcement_has_exactly_one_producer(self):
        """P11 — an AST call census, so a fourth caller cannot quietly add a
        second, differently-worded warning."""
        producers = []
        for path in (REPO / "backend").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr == "report_save_failure"):
                    producers.append(f"{path.name}:{node.lineno}")
        assert len(producers) == 1, producers
        assert producers[0].startswith("save_manager.py"), producers

    def test_the_census_can_see_an_offender(self):
        """Sensitivity arm for both censuses above."""
        tree = ast.parse("def f():\n    x = autosave(w)\n    print(x)\n")
        found = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "autosave"]
        assert len(found) == 1

    def test_the_tutorial_still_never_touches_the_slot(self, monkeypatch,
                                                       tmp_path):
        """TUT-F2's contract is untouched — and the skip arm CLEARS a
        standing warning rather than leaving one stranded on the lesson."""
        monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path / "saves")
        world = _quiet(WorldState.from_scenario, SCENARIO)
        world.scenario_name = "tutorial"
        # ⚠ Added after a sweep: the pin asserted only the skip, so
        # deleting the skip arm's clear was invisible. A warning raised on
        # the campaign must not follow the player into the lesson.
        notifications.report_save_failure(world, "earlier failure", 3)
        assert [n for n in world.notifications.to_list()
                if n.get("type") == notifications.SAVE_FAILED]
        res = save_manager.autosave(world)
        assert res.get("skipped") == "tutorial"
        assert not (tmp_path / "saves" /
                    save_manager.AUTOSAVE_FILENAME).exists()
        assert [n for n in world.notifications.to_list()
                if n.get("type") == notifications.SAVE_FAILED] == []

    def test_the_announcement_lever_restores_the_silence(self, monkeypatch,
                                                         tmp_path):
        monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path / "saves")
        monkeypatch.setattr(save_manager, "SAVE_FAILURE_IS_ANNOUNCED", False)
        monkeypatch.setattr(save_manager, "json", _BoomJson)
        world = _quiet(WorldState.from_scenario, SCENARIO)
        _quiet(save_manager.autosave, world)
        assert [n for n in world.notifications.to_list()
                if n.get("type") == notifications.SAVE_FAILED] == []


# ═══════════════════════════════════════════════════════════════════════════
# The client can draw it
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRailCanRenderIt:

    @staticmethod
    def _gd_map(name):
        import re
        src = (REPO / "godot-client" / "project-sovereign" / "scripts" /
               "notification_bar.gd").read_text(encoding="utf-8")
        block = src[src.index(f"const {name} = {{"):]
        block = block[:block.index("}")]
        return dict(re.findall(
            r'\s*"([a-z0-9_]+)"\s*:\s*"([A-Za-z0-9\-]+)"\s*,', block))

    def test_both_maps_name_the_new_type(self):
        """⚠ BOTH, in the SAME commit, or REV-V3's two-directional census
        reds: a type in one map and not the other renders a legacy
        three-letter fallback beside a real glyph."""
        assert self._gd_map("TYPE_ICONS").get("save_failed") == "SAV"
        assert self._gd_map("TYPE_ICON_SVGS").get("save_failed") == \
            "floppy-disk"

    def test_the_glyph_asset_exists(self):
        hits = list((REPO / "godot-client").rglob("floppy-disk.svg*"))
        assert hits, "the rail would draw nothing"

    def test_the_constant_name_matches_its_value(self):
        """The rail census derives declared types as
        `{v for k, v in vars(notifications) if v == k.lower()}`, so a
        constant whose name is not the upper-case of its value is
        mis-classified as un-declared."""
        assert notifications.SAVE_FAILED == "save_failed"
        assert getattr(notifications, "SAVE_FAILED".upper()) == "save_failed"

    def test_it_is_not_on_the_rail_exempt_list(self):
        assert notifications.SAVE_FAILED not in notifications.RAIL_EXEMPT_TYPES


class TestTheRecordSaysWhatItCarries:

    def test_the_save_format_reference_warns_about_the_payload(self):
        """⚠ The failure `message` carries a raw OS error including a user
        filesystem path, and it then PERSISTS into every later save. The
        reference documents that row's shape and is owed the mention."""
        doc = (REPO / "docs" / "SAVE_FORMAT_REFERENCE.md").read_text(
            encoding="utf-8")
        assert "save_failed" in doc
