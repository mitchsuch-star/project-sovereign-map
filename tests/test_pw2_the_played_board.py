"""Row PW "Plain Words", part 2 (November 18, 2026) — the played board, DRIVEN (PW2-R9).

The enemy's moves are played on the map in two beats: `map_renderer_base.play_all_regions` (the pieces march
while a province that changed hands keeps its old colour) and `finish_play` (the new board, whole). The
part's review found the second beat had ONE caller, the report's own telling — and a response that another
window answers first (a letter, a marshal's petition, a paradox riding the end of the turn: every entry of
`main._post_hud_response_routes` returns before the report) never reached it: the board would stand in its
old colours with its marching corps held out of it.

A played board now finishes ITSELF a moment after its march (`PLAY_SELF_FINISH_S`). The probe
(`tools/pw2_played_board_probe.gd`, headless) stands the shared renderer on the registry's 1805 board, puts
a corps the fog half-hides on it and plays three boards; what is read is the renderer's own state.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess

import pytest

_REPO = pathlib.Path(__file__).resolve().parents[1]
_PROJECT = _REPO / "godot-client" / "project-sovereign"
_PROBE = _REPO / "tools" / "pw2_played_board_probe.gd"

_CANDIDATES = [
    os.environ.get("GODOT_BIN", ""),
    r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
    r"\Godot_v4.4.1-stable_win64.exe",
    "godot",
    "godot4",
]


def _engine():
    for candidate in _CANDIDATES:
        if not candidate:
            continue
        if os.path.sep in candidate or "/" in candidate:
            if pathlib.Path(candidate).is_file():
                return candidate
            continue
        found = shutil.which(candidate)
        if found:
            return found
    return None


@pytest.fixture(scope="module")
def played(tmp_path_factory):
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, and a skip is not a pass")
    work = tmp_path_factory.mktemp("pw2_played")
    out, log = work / "out.json", work / "godot.log"
    proc = subprocess.run(
        [engine, "--headless", "--path", str(_PROJECT), "--log-file", str(log), "--script", str(_PROBE),
         "--", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, cwd=str(_PROJECT),
        stdin=subprocess.DEVNULL)
    if not out.is_file():
        pytest.fail(f"the probe wrote no result\nexit={proc.returncode}\n{proc.stdout[-1500:]}\n{proc.stderr[-1500:]}")
    result = json.loads(out.read_text(encoding="utf-8"))
    assert "error" not in result, result.get("error")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["script_errors"] = [ln for ln in text.splitlines() if "SCRIPT ERROR" in ln][:5]
    return result


class TestThePlayedBoardDriven:
    def test_the_probe_ran_clean_on_a_board_with_a_corps(self, played):
        assert played["script_errors"] == []
        assert played["stands_before"] is True, "the half-hidden corps stands where the board put him"

    def test_beat_one_holds_the_old_colour_and_walks_the_corps(self, played):
        assert len(played["played"]["changed"]) == 1, played["played"]
        assert played["played"]["moved"] == 1, "the fog's marker marches too"
        assert played["one_held_old_colour"] is True, "the province keeps its holder's colour while he marches"
        assert played["one_final_pending"] is True
        assert played["one_marcher_held_out"] is True, "he is not put down where he goes before he gets there"
        assert played["one_markers_marching"] == 1

    def test_a_played_board_nobody_comes_back_for_finishes_itself(self, played):
        """PW2-R9. Was: the board stood as beat one left it until the next board arrived."""
        assert played["one_self_finished"] is True
        assert played["one_new_colour"] is True, "the province takes its new holder's colour"
        assert played["one_marcher_arrived"] is True, "the corps stands where the new board has him, and only there"
        assert played["one_markers_after"] == 0, "the marching marker is gone with the board that walked it"

    def test_a_caller_that_finishes_first_leaves_the_clock_nothing_to_do(self, played):
        assert played["two_caller_finished"] is True and played["two_colour_at_once"] is True
        assert played["two_colour_stays"] is True
        assert played["two_nothing_left"] is True, "`finish_play` answers False when no played board stands"

    def test_a_newer_board_is_never_overlaid_by_the_played_one(self, played):
        """The played board's own clock must not land an OLDER board over one that arrived meanwhile."""
        assert played["three_newer_board_stands"] == "Britain"
        assert played["three_final_empty"] is True


class TestTheProbeIsWired:
    def test_the_lane_and_the_seconds(self):
        conftest = (_REPO / "tests" / "conftest.py").read_text(encoding="utf-8")
        assert '"test_pw2_the_played_board",' in conftest, "a headless engine: it rides a lane"
        probe = _PROBE.read_text(encoding="utf-8")
        assert "await create_timer(MARCH_S + map.PLAY_SELF_FINISH_S + 0.25).timeout" in probe
        renderer = (_PROJECT / "scenes" / "map_renderer_base.gd").read_text(encoding="utf-8")
        assert "const PLAY_SELF_FINISH_S := 0.3" in renderer
