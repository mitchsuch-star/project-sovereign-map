"""Row FUN, FUN-1 (November 25, 2026) — the fast lane picks the tests that
name what changed (`tools/fast_lane.py`); the full gate still runs at the
commit. Pinned on a synthetic tests folder, so the pick is exact."""
from __future__ import annotations

import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("fast_lane", REPO / "tools" / "fast_lane.py")
FL = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FL)


def _tests(tmp_path, files: dict) -> pathlib.Path:
    d = tmp_path / "tests"
    d.mkdir()
    for name, text in files.items():
        (d / name).write_text(text, encoding="utf-8")
    return d


class TestTheFastLanePicksWhatNamesTheChange:

    def test_a_backend_module_by_its_dotted_name_its_path_or_its_import(self, tmp_path):
        d = _tests(tmp_path, {
            "test_a.py": "from backend.game_logic.naval import crossing_check\n",
            "test_b.py": "from backend.game_logic import naval, diplomacy\n",
            "test_c.py": "SRC = 'backend/game_logic/naval.py'\n",
            "test_d.py": "from backend.game_logic import navalese\n",      # a longer name: not naval
            "test_e.py": "import backend.models.world_state\n",
        })
        got = FL.select_tests(["backend/game_logic/naval.py"], d)
        assert got == ["test_a.py", "test_b.py", "test_c.py"], got

    def test_a_client_script_and_a_doc_by_their_file_names(self, tmp_path):
        d = _tests(tmp_path, {
            "test_map.py": "MAP = PROJECT / 'scenes' / 'map_renderer_base.gd'\n",
            "test_doc.py": "text = (REPO / 'docs' / 'STATUS.md').read_text()\n",
            "test_none.py": "x = 1\n",
        })
        got = FL.select_tests(["godot-client/project-sovereign/scenes/map_renderer_base.gd",
                               "docs/STATUS.md"], d)
        assert got == ["test_doc.py", "test_map.py"], got

    def test_a_changed_test_runs_itself(self, tmp_path):
        d = _tests(tmp_path, {"test_mine.py": "x = 1\n", "test_other.py": "y = 2\n"})
        assert FL.select_tests(["tests/test_mine.py"], d) == ["test_mine.py"]

    def test_window_modules_wait_for_with_engine(self, tmp_path):
        d = _tests(tmp_path, {
            "test_windowed.py": "uses dd_b_play\n",
            "test_headless.py": "uses dd_b_play\n",
        })
        assert FL.select_tests(["tools/dd_b_play.py"], d, engine_modules=["test_windowed"]) \
            == ["test_headless.py"]
        assert FL.select_tests(["tools/dd_b_play.py"], d, engine_modules=["test_windowed"],
                               with_engine=True) == ["test_headless.py", "test_windowed.py"]

    def test_an_engine_lane_pin_that_launches_nothing_stays(self, tmp_path):
        """The review (lane C): the lane's source pins launch nothing — a `.gd`
        change must keep them."""
        d = _tests(tmp_path, {"test_pin.py": "SRC = 'map_renderer_base.gd'  # read only\n"})
        assert FL.select_tests(["godot-client/project-sovereign/scenes/map_renderer_base.gd"], d,
                               engine_modules=["test_pin"]) == ["test_pin.py"]

    def test_a_parenthesised_import_over_lines_and_an_absolute_path(self, tmp_path):
        d = _tests(tmp_path, {
            "test_multi.py": "from backend.commands import (\n    executor,\n    order_quotes,\n)\n",
        })
        assert FL.select_tests(["backend/commands/order_quotes.py"], d) == ["test_multi.py"]
        absolute = str(FL.REPO / "backend" / "commands" / "order_quotes.py")
        assert FL.select_tests([absolute], d) == ["test_multi.py"]

    def test_the_real_lane_reads_the_engine_set_from_conftest(self):
        mods = FL._engine_modules()
        assert "test_dd_b_the_client_hands" in mods and "test_fun1_the_hands" in mods, mods
