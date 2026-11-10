"""The engine lanes (November 10, 2026 — the user's "the hook takes so long",
then "Yes, split it").

Until this slice every module that launches the Godot binary shared ONE xdist
group, `engine`; the timed run at 62a3f241 read that one worker busy for
600.8 s of the suite's 648 s while seven others sat idle. The lane is three
now (`tests/conftest.py`, ENGINE_LANES), the heaviest groups are handed out
first (HEAVIEST_FIRST), and `tools/dd_b_play.py start --beside-headless`
counts windows only.

These pins hold the RULES, so the split cannot rot silently:

* a module that opens a window or starts a sandboxed backend is in `engine`
  (two windows, or two port scans from 8006, at once is the one thing the
  lanes exist to prevent);
* the lanes are disjoint, real, and the legacy name `engine` survives (one
  class elsewhere carries the mark by hand);
* the collection really is grouped and — under a worker — really is ordered
  as the tables say;
* the client-hands guard tells a headless engine from a window, and fails
  closed;
* the hook and CLAUDE.md name the same worker count.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
CONFTEST = TESTS / "conftest.py"
HOOK = REPO / "scripts" / "git-hooks" / "pre-commit"

sys.path.insert(0, str(REPO / "tools"))
import dd_b_play as P  # noqa: E402

# What makes a module the window lane's: a real window, the sandboxed
# backend's port scan, or the client-hands instrument's own start.
_WINDOW_OR_BACKEND = re.compile(r'"--windowed"|\bstart_backend\(|"start", "--road"')


@pytest.fixture(scope="module")
def CT(request):
    """The conftest module pytest ALREADY loaded — never a second import: its
    module body mints the suite's save sandbox."""
    for plugin in request.config.pluginmanager.get_plugins():
        path = getattr(plugin, "__file__", None)
        if path and pathlib.Path(path).resolve() == CONFTEST.resolve():
            return plugin
    pytest.fail("tests/conftest.py is not loaded")


class TestTheLanes:
    def test_the_three_lanes_and_the_old_name(self, CT):
        assert list(CT.ENGINE_LANES) == ["engine", "engine_frames", "engine_panels"]
        # `test_moments_armed.TestThePassiveBoard` carries the mark by hand.
        marked = (TESTS / "test_moments_armed.py").read_text(encoding="utf-8")
        assert '@pytest.mark.xdist_group(name="engine")' in marked

    def test_the_lanes_are_disjoint_and_their_union_is_the_old_table(self, CT):
        lanes = list(CT.ENGINE_LANES.values())
        assert sum(len(lane) for lane in lanes) == len(CT.ENGINE_GROUP_MODULES)
        assert CT.ENGINE_GROUP_MODULES == frozenset().union(*lanes)

    def test_every_lane_module_is_a_test_file(self, CT):
        missing = sorted(m for m in CT.ENGINE_GROUP_MODULES if not (TESTS / f"{m}.py").is_file())
        assert not missing, f"a lane names a module that is gone: {missing}"

    def test_a_window_or_a_sandboxed_backend_is_in_the_one_lane(self, CT):
        """THE rule. Census, not a list: a NEW module that opens a window or
        scans for a backend port is caught here the day it is written."""
        found = sorted(p.stem for p in TESTS.glob("test_*.py")
                       if p.name != pathlib.Path(__file__).name
                       and _WINDOW_OR_BACKEND.search(p.read_text(encoding="utf-8", errors="replace")))
        assert {"test_dd_b_the_client_hands", "test_uxr2_grips_driven",
                "test_uxr2b_hud_band", "test_uxr_d4_the_side_desk"} <= set(found), found
        outside = [m for m in found if m not in CT.ENGINE_LANES["engine"]]
        assert not outside, (
            f"{outside} opens a window or starts a sandboxed backend: add it to "
            "ENGINE_LANES['engine'] in tests/conftest.py (one window at a time)")

    def test_the_headless_lanes_open_no_window(self, CT):
        for lane in ("engine_frames", "engine_panels"):
            for module in sorted(CT.ENGINE_LANES[lane]):
                text = (TESTS / f"{module}.py").read_text(encoding="utf-8", errors="replace")
                assert not _WINDOW_OR_BACKEND.search(text), f"{module} belongs in `engine`"

    def test_the_census_bites(self):
        assert _WINDOW_OR_BACKEND.search('[engine, "--windowed", "--resolution", "1600x900"]')
        assert _WINDOW_OR_BACKEND.search("backend, port = AP.start_backend(work, AP.WAR_ROOM_PORT)")
        assert _WINDOW_OR_BACKEND.search('str(PLAY), "start", "--road", "conquest"')
        assert not _WINDOW_OR_BACKEND.search('[exe, "--headless", "--path", str(PROJECT)]')

    def test_a_module_rides_its_lane_and_any_other_its_own_name(self, CT):
        assert CT._LANE_OF["test_dd_b_the_client_hands"] == "engine"
        assert CT._LANE_OF["test_sf_rr5_the_frames"] == "engine_frames"
        assert CT._LANE_OF["test_cn4_the_chip_honesty_census"] == "engine_panels"
        assert "test_cx_r2_the_offer_is_reachable" not in CT._LANE_OF
        assert CT._module_of("tests/test_x_y.py::TestA::test_b[p/q]@engine") == "test_x_y"
        assert CT._module_of("tests\\test_x_y.py::test_b") == "test_x_y"


class TestTheCollectionIsGroupedAsTheTablesSay:
    """Read off the REAL collection of this run (whole under the hook; one
    module's worth under a targeted run, where it is trivially true)."""

    def test_every_test_carries_its_group(self, CT, request):
        if not request.config.pluginmanager.hasplugin("xdist"):
            pytest.skip("pytest-xdist is not installed — nothing is grouped")
        wrong = []
        for item in request.session.items:
            module, group = CT._module_of(item.nodeid), CT._group_of(item)
            want = CT._LANE_OF.get(module, module)
            if group != want and group not in CT.ENGINE_LANES:
                wrong.append((item.nodeid, group, want))
        assert not wrong, wrong[:5]

    def test_a_lane_modules_tests_are_in_its_lane(self, CT, request):
        if not request.config.pluginmanager.hasplugin("xdist"):
            pytest.skip("pytest-xdist is not installed — nothing is grouped")
        seen = {}
        for item in request.session.items:
            module = CT._module_of(item.nodeid)
            if module in CT._LANE_OF:
                seen.setdefault(module, set()).add(CT._group_of(item))
        assert all(groups == {CT._LANE_OF[m]} for m, groups in seen.items()), seen

    def test_under_a_worker_the_heaviest_are_first(self, CT, request):
        if not hasattr(request.config, "workerinput"):
            pytest.skip("a serial run keeps its order — nothing to read")
        order = []
        for item in request.session.items:
            group = CT._group_of(item)
            if not order or order[-1] != group:
                order.append(group)
        assert len(order) == len(set(order)), "a group's tests were split apart"
        named = [g for g in CT.HEAVIEST_FIRST if g in set(order)]
        assert order[:len(named)] == named


class TestTheHeaviestGoFirst:
    def test_every_name_is_a_lane_or_a_module(self, CT):
        assert len(set(CT.HEAVIEST_FIRST)) == len(CT.HEAVIEST_FIRST)
        for name in CT.HEAVIEST_FIRST:
            assert name in CT.ENGINE_LANES or (TESTS / f"{name}.py").is_file(), name
        assert set(CT.ENGINE_LANES) <= set(CT.HEAVIEST_FIRST)
        # a lane module is named by its LANE, never by itself (it has no group
        # of its own to move)
        assert not set(CT.HEAVIEST_FIRST) & CT.ENGINE_GROUP_MODULES

    def test_the_order(self, CT, monkeypatch):
        monkeypatch.setattr(CT, "HEAVIEST_FIRST", ("slow", "engine"))
        groups = ["a", "big", "big", "engine", "big", "slow", "a", "engine", "tiny", "slow"]
        order = CT.heaviest_first(groups)
        assert [groups[i] for i in order] == ["slow", "slow", "engine", "engine",
                                              "big", "big", "big", "a", "a", "tiny"]
        # a group's tests keep the order they were collected in
        assert [i for i in order if groups[i] == "big"] == [1, 2, 4]
        assert sorted(order) == list(range(len(groups)))

    def test_no_name_listed_changes_nothing_but_the_count_rule(self, CT, monkeypatch):
        monkeypatch.setattr(CT, "HEAVIEST_FIRST", ())
        groups = ["b", "a", "a", "b", "c"]
        assert [groups[i] for i in CT.heaviest_first(groups)] == ["b", "b", "a", "a", "c"]

    def test_the_scheduler_is_told_to_keep_the_order(self, CT):
        class Option:
            dist = "loadgroup"
            loadscopereorder = True

        class Config:
            option = Option()

        CT.pytest_configure(Config)
        assert Config.option.loadscopereorder is False
        Config.option.dist, Config.option.loadscopereorder = "no", True
        CT.pytest_configure(Config)
        assert Config.option.loadscopereorder is True


class TestTheClientHandsCountWindowsOnly:
    """`dd_b_play.py start` refuses while another engine runs. The suite's
    headless lanes run beside it, so the suite's road counts WINDOWS."""

    LINES = [r'"C:\godot.exe" --headless --path C:\p --script harness.gd',
             r'"C:\godot.exe" --audio-driver Dummy --windowed --resolution 5120x1440 --path C:\p',
             r'"C:\godot.exe" --headless --audio-driver Dummy --log-file x.log']

    def test_a_headless_engine_is_no_window(self, monkeypatch):
        monkeypatch.setattr(P, "_godot_command_lines", lambda: list(self.LINES))
        assert P._godot_running(windowed_only=True) == 1
        monkeypatch.setattr(P, "_godot_command_lines", lambda: [self.LINES[0], self.LINES[2]])
        assert P._godot_running(windowed_only=True) == 0

    def test_an_engine_it_cannot_read_counts(self, monkeypatch):
        """Fails closed: Windows shows no command line for it -> it is a window."""
        monkeypatch.setattr(P, "_godot_command_lines", lambda: [self.LINES[0], ""])
        assert P._godot_running(windowed_only=True) == 1

    def test_no_listing_at_all_is_the_plain_count(self, monkeypatch):
        import subprocess

        class Done:
            stdout = "Godot_v4.4.1-stable_win64.exe  1 Console\npython.exe  2 Console\ngodot.exe  3 Console\n"

        monkeypatch.setattr(P, "_godot_command_lines", lambda: None)
        monkeypatch.setattr(subprocess, "run", lambda *a, **k: Done())
        assert P._godot_running(windowed_only=True) == 2
        assert P._godot_running() == 2

    def test_a_measure_still_counts_every_engine(self, monkeypatch):
        """The default is the old rail: the measure's settle timing is the
        reason for it, and a headless engine stretches that too."""
        import subprocess

        class Done:
            stdout = "Godot_v4.4.1-stable_win64.exe  1 Console\n"

        monkeypatch.setattr(P, "_godot_command_lines",
                            lambda: pytest.fail("the default never reads command lines"))
        monkeypatch.setattr(subprocess, "run", lambda *a, **k: Done())
        assert P._godot_running() == 1

    def test_start_takes_the_flag_and_the_suite_passes_it(self):
        src = (REPO / "tools" / "dd_b_play.py").read_text(encoding="utf-8")
        assert '_godot_running(windowed_only=bool(getattr(args, "beside_headless", False)))' in src
        assert 'p.add_argument("--beside-headless", action="store_true"' in src
        test = (TESTS / "test_dd_b_the_client_hands.py").read_text(encoding="utf-8")
        assert test.count('"--godot", engine, "--beside-headless"]') == 2
        assert test.count("P._godot_running(windowed_only=True)") == 2
        assert "P._godot_running()" not in test


class TestTheHookAndTheBookAgree:
    def _workers(self) -> str:
        found = re.findall(r"-n (\d+) --dist loadgroup", HOOK.read_text(encoding="utf-8"))
        assert len(found) == 1, found
        return found[0]

    def test_the_hook_runs_the_whole_suite_in_lanes(self):
        hook = HOOK.read_text(encoding="utf-8")
        n = self._workers()
        assert f'"$PYTHON" -m pytest tests/ -q -n {n} --dist loadgroup' in hook
        assert f"{n} workers" in hook
        assert int(n) >= 8

    def test_claude_md_names_the_hooks_worker_count(self):
        book = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
        named = re.findall(r"-n (\d+) --dist loadgroup", book)
        assert named and set(named) == {self._workers()}, named
