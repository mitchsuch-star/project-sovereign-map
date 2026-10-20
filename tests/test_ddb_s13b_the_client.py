"""Pre-Deploy S13b part 4, slice S13b-5 — the client (October 19, 2026;
`docs/BUG_FIXES.md` §DD-B; rules `SYSTEMS_REFERENCE.md` §132).

  DDB-54  the command line's Esc runs the close-the-topmost ladder (the
          wizard, an open screen, the region panel, the pinned screen) before
          it releases focus — the first Esc after a typed order only left the
          line, a second closed the screen.
  DDB-55  the title screen's caption changes at the crossfade's midpoint — it
          named the next painting while the last still showed.
  DDB-56  a capture from France OR an ally reads red; the backend stamps the
          capture's alignment as it stamps a battle's sides.
  DDB-57  a wheel notch over the command window moves three whole lines; a
          reply taller than the window opens at its first line with the
          window raised to its tallest until the next command.

DRIVEN: `tools/ddb_s13b_client_harness.gd` boots the REAL `main.tscn` (and
`main_menu.tscn`, `enemy_phase_dialog.tscn`) behind the cc harness's API stub
and pushes real keys and wheel events. Read on HEAD before the fix (a copy of
the project in the scratchpad): the first Esc left the screen open and took
the focus; the caption changed at the fade's start; an ally's lost Munich read
in the conquest green; a notch moved 18 px (under one 22 px line) and a tall
reply stood on its last line in a 140 px window. A skip is not a pass.
"""
from __future__ import annotations

import json
import os
import subprocess

import pytest

from tests import _chip_census as C

HARNESS = C.REPO / "tools" / "ddb_s13b_client_harness.gd"


@pytest.fixture(scope="module")
def driven(tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    work = tmp_path_factory.mktemp("ddb_client")
    out = work / "out.json"
    spec = work / "spec.json"
    spec.write_text(json.dumps({"out": str(out)}), encoding="utf-8")
    proc = subprocess.run(
        [exe, "--headless", "--path", str(C.PROJECT), "--log-file", str(work / "godot.log"),
         "--script", str(HARNESS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=400, env=dict(os.environ, DDB_SPEC=str(spec)), cwd=str(C.PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    result = json.loads(out.read_text(encoding="utf-8"))
    assert not result.get("error"), result.get("error")
    log = (work / "godot.log").read_text(encoding="utf-8", errors="replace")
    assert "SCRIPT ERROR" not in log, log[-3000:]
    return result


class TestDDB54:
    def test_the_first_esc_closes_the_screen_and_keeps_the_line(self, driven):
        assert driven["54_screen_open"] and driven["54_line_focused_before"]
        assert driven["54_screen_open_after_first_esc"] is False
        assert driven["54_line_focused_after_first_esc"] is True

    def test_with_nothing_open_esc_lets_the_line_go(self, driven):
        assert driven["54_line_focused_after_second_esc"] is False
        assert driven["54_pause_open_after_second_esc"] is False, \
            "the line's own Esc never opens the pause menu"


class TestDDB55:
    def test_the_caption_changes_at_the_midpoint(self, driven):
        first = driven["55_first_caption"]
        assert driven["55_caption_at_fade_start"] == first
        assert driven["55_caption_at_quarter"] == first
        assert driven["55_caption_past_midpoint"] != first
        assert driven["55_caption_past_midpoint"].startswith("Jacques-Louis David")


class TestDDB56:
    def test_an_allys_loss_reads_red(self, driven):
        assert driven["56_ally_colour"] == "error", driven["56_ally_text"]
        assert driven["56_ours_colour"] == "error"
        assert driven["56_foe_colour"] == "conquest", "a foe's loss is still our good news"

    def test_the_backend_stamps_the_captures_alignment(self):
        import backend.main as M
        from backend.models.world_state import WorldState
        world = WorldState()
        phase = {"nations": {"Austria": {"actions": [{"events": [
            {"type": "conquest", "region": "Munich", "captured_from": "Prussia"},
            {"type": "move", "captured_from": "France"},
            {"type": "move"}]}]}}}
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "ALLIANCE"
        stamped = M._stamp_battle_standing(phase, world)
        events = stamped["nations"]["Austria"]["actions"][0]["events"]
        assert events[0]["captured_from_alignment"] == "friend"
        assert events[1]["captured_from_alignment"] == "player"
        assert "captured_from_alignment" not in events[2], "no capture, no stamp"


class TestDDB57:
    def test_a_notch_moves_three_whole_lines(self, driven):
        assert driven["57_line_px"] > 0
        assert driven["57_wheel_moved"] == int(3 * driven["57_line_px"])
        assert driven["57_wheel_up_moved"] == int(3 * driven["57_line_px"])

    def test_a_tall_reply_opens_at_its_first_line_with_the_window_raised(self, driven):
        assert driven["57_raised"] is True
        assert driven["57_height_raised"] > driven["57_height_before"]
        assert driven["57_scroll"] == driven["57_reply_top"]
        assert driven["57_scroll"] < driven["57_scroll_max"], "not the end of the log"

    def test_the_next_command_puts_the_window_back(self, driven):
        assert driven["57_raised_after_next"] is False
        assert driven["57_height_after_next"] == driven["57_height_before"]

    def test_a_short_reply_keeps_the_log_on_its_newest_line(self, driven):
        assert driven["57_raised_for_a_short_reply"] is False
        assert driven["57_scroll_at_end_for_a_short_reply"] is True
