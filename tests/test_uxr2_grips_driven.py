"""UXR-2 Slice C — the six screens resize and remember, DRIVEN (Pre-Deploy S9,
October 12, 2026).

The layout law's done-when, measured on the real `main.tscn` with real mouse
events (`tools/uxr2_grip_harness.gd`): each top-bar screen's grip sits on its
panel's corner, a drag resizes the panel about its centre without closing the
screen, the size is stored and returns on the next open, a double-click
restores the authored size, a click that does not move stores nothing; a
screen grown wider than the viewport is refit when the Interface Scale rises
under it; Reset layout forgets every stored size.

SKIPS when the Godot engine is absent (a skip is not a pass).
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
_HARNESS = _REPO / "tools" / "uxr2_grip_harness.gd"
SCREENS = ("ledger", "generals", "dispatch", "event_log", "gazette", "diplomatic_ledger")
DRAG = (80.0, -60.0)   # the harness's drag: +80 right, −60 up

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
def driven(tmp_path_factory):
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    out = tmp_path_factory.mktemp("uxr2") / "grips.json"
    # A port nothing listens on: the harness stubs the API, and refuses to
    # run against the player's live 8005 if a request ever slips past it.
    env = dict(os.environ, UXR2_OUT=str(out), SOVEREIGN_PORT="8993")
    # A REAL window, parked past the desktop as the IQ-10 capture parks it:
    # a headless root viewport is 64x64, where every panel sits at its
    # minimum and no grip has room to move anything.
    proc = subprocess.run(
        [engine, "--audio-driver", "Dummy", "--windowed", "--resolution", "1600x900",
         "--position", "5200,20", "--path", str(_PROJECT), "--script", str(_HARNESS)],
        capture_output=True, text=True, timeout=300, env=env, cwd=str(_PROJECT),
        stdin=subprocess.DEVNULL)
    if not out.is_file():
        pytest.fail(f"the harness wrote nothing (exit {proc.returncode}):\n"
                    f"{proc.stdout[-3000:]}\n{proc.stderr[-3000:]}")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data.get("fatal") == "", data.get("fatal")
    assert data["viewport"][0] >= 1200 and data["viewport"][1] >= 700, (
        "the harness did not get its 1600x900 window", data["viewport"])
    return data


def _near(a, b, tol=2.0):
    return all(abs(float(x) - float(y)) <= tol for x, y in zip(a, b))


@pytest.mark.parametrize("screen", SCREENS)
class TestEachScreenResizesAndRemembers:
    def test_the_grip_sits_on_the_corner(self, driven, screen):
        r = driven["screens"][screen]
        assert r.get("open") and r.get("grip") and r.get("grip_visible"), r
        assert r["grip_gap"] < 2.0, r

    def test_a_drag_resizes_about_the_centre_and_keeps_the_screen_open(self, driven, screen):
        r = driven["screens"][screen]
        aw, ah = r["authored"]
        want = (aw + 2 * DRAG[0], ah + 2 * DRAG[1])
        assert _near(r["after_drag"], want), (r["authored"], r["after_drag"], want)
        assert r["open_after_drag"], "the press reached the close-on-click overlay"
        assert r["grip_gap_after"] < 2.0, "the grip did not follow the corner"

    def test_the_size_is_stored_and_returns_on_the_next_open(self, driven, screen):
        r = driven["screens"][screen]
        assert r["stored"] and _near(r["stored_size"], r["after_drag"]), r
        assert r["closed"], r
        assert _near(r["reopened"], r["after_drag"]), (r["after_drag"], r["reopened"])

    def test_a_double_click_restores_the_authored_size(self, driven, screen):
        r = driven["screens"][screen]
        assert _near(r["after_double_click"], r["authored"]), r
        assert r["stored_after_double_click"] is False
        assert r["open_after_double_click"], "the double-click closed the screen"

    def test_a_click_that_does_not_move_stores_nothing(self, driven, screen):
        assert driven["screens"][screen]["stored_after_click"] is False


class TestTheRefitRoadAndTheReset:
    def test_a_wide_screen_is_refit_when_the_scale_rises_under_it(self, driven):
        assert driven["refit_before"][0] > driven["refit_view"][0], (
            "the staging did not grow the panel past the new viewport", driven)
        assert driven["refit_inside"], (driven["refit_view"], driven["refit_rect"])
        assert driven["refit_grip_gap"] < 2.0

    def test_reset_layout_forgets_every_stored_size(self, driven):
        assert driven["stored_before_reset"] is True
        assert driven["stored_after_reset"] is False
        # the authored rect, as the clamp fits it to the viewport the reset
        # leaves (Reset layout returns the scale to the derivation too)
        aw, ah = driven["ledger_authored"]
        vw, vh = driven["reset_view"]
        want = (min(aw, max(320.0, vw - 24.0)), min(ah, max(240.0, vh - 88.0)))
        assert _near(driven["ledger_after_reset"], want), (driven["ledger_after_reset"], want)

    def test_the_command_window_keeps_its_grip(self, driven):
        assert driven["terminal_grip"] is True
