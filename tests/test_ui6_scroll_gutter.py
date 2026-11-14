"""Session UI-6 (November 13, 2026) — UI6-X22, THE SCROLL THAT FLIPPED FOREVER.

The full shoot died at the province panel on the compact view (Paris,
Interface Scale 2.0): signal 11, after the frame counter had stood still at
one frame for minutes while the memory climbed. Measured with a watchdog
thread and counters on the panel's layout signals: the panel's ScrollContainer
toggled its vertical bar about 780 times a second, forever, inside ONE frame.

The panel's text is not monotonic in its width (its chips are inline tables
that rewrap): 336 px tall at 336 px wide — one more than the scroll's 335, so
the bar shows — and 333 px tall at 328 (the bar's 8 px taken), so the bar is
not needed and hides. In SCROLL_MODE_AUTO the container re-sorts on every
flip, and Godot runs the queued sorts inside the frame until the queue is
empty; it never is. A band of panel widths (about 353 to 367 px) put the text
on that knife-edge; the bgcolor tag, the NBSP padding and a crash in the text
server were each suspected and each ruled out by a measured arm.

The fix is at the class: every ScrollContainer in the client keeps its
vertical bar's gutter (SCROLL_MODE_RESERVE, Godot 4.4) — the label's width,
and so its height, never depend on whether the bar shows. A self-scrolling
RichTextLabel makes one bounded pass (Godot 4.4.1's `_update_scroll_exceeds`)
and is not of the class.

The census below holds every scene node and every scripted scroll to it; the
driven arm replays the dumped Paris panel in the panel's own nesting, headless
(tools/ui6_scroll_flip_probe.gd): RESERVE finishes, AUTO still hangs (the arm
that proves the fixture still exercises the engine's flip).
"""

import json
import os
import pathlib
import re
import shutil
import subprocess

import pytest

_REPO = pathlib.Path(__file__).resolve().parents[1]
_PROJECT = _REPO / "godot-client" / "project-sovereign"
_PROBE = _REPO / "tools" / "ui6_scroll_flip_probe.gd"
_FIXTURE = _REPO / "tests" / "fixtures" / "ui6_scroll_flip_paris.bbcode"

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


def _scene_scrolls():
    """(scene, node header, the node's property block) for every ScrollContainer."""
    out = []
    for scene in sorted((_PROJECT / "scenes").glob("*.tscn")):
        lines = scene.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if line.startswith("[node ") and 'type="ScrollContainer"' in line:
                block = []
                for nxt in lines[i + 1:]:
                    if nxt.startswith("["):
                        break
                    block.append(nxt)
                out.append((scene.name, line, block))
    return out


class TestEveryScrollKeepsItsGutter:

    def test_every_scene_scroll_reserves_its_bar(self):
        scrolls = _scene_scrolls()
        assert len(scrolls) >= 21, len(scrolls)          # sensitive: the census finds them
        loose = [f"{scene}: {header}" for scene, header, block in scrolls
                 if "vertical_scroll_mode = 4" not in block]
        assert loose == [], ("a ScrollContainer whose child's width follows its bar can flip "
                             "forever in one frame (UI6-X22) — give it vertical_scroll_mode = 4 "
                             "(SCROLL_MODE_RESERVE):\n" + "\n".join(loose))

    def test_every_scripted_scroll_reserves_its_bar(self):
        made = 0
        loose = []
        for script in sorted((_PROJECT / "scripts").glob("*.gd")):
            src = script.read_text(encoding="utf-8")
            for m in re.finditer(r"^\s*(?:var\s+)?([A-Za-z_][A-Za-z_0-9]*)\s*:?=\s*ScrollContainer\.new\(\)",
                                 src, re.M):
                made += 1
                name = m.group(1)
                window = src[m.end():m.end() + 900]
                if f"{name}.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_RESERVE" not in window:
                    loose.append(f"{script.name}: {name}")
        assert made >= 6, made
        assert loose == [], loose

    def test_the_province_panel_reserves_its_bar(self):
        scene = (_PROJECT / "scenes" / "region_panel.tscn").read_text(encoding="utf-8")
        block = scene.split('[node name="Scroll" type="ScrollContainer"', 1)[1].split("[node", 1)[0]
        assert "vertical_scroll_mode = 4" in block


@pytest.fixture(scope="module")
def engine():
    found = _engine()
    if found is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    return found


def _run(engine, mode, out, timeout):
    return subprocess.run(
        [engine, "--headless", "--path", str(_PROJECT), "--script", str(_PROBE), "--",
         str(_FIXTURE), str(out), mode],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout, cwd=str(_PROJECT))


class TestTheFlipIsBroken:

    def test_reserve_finishes_the_paris_panel(self, engine, tmp_path):
        out = tmp_path / "reserve.json"
        proc = _run(engine, "reserve", out, timeout=120)
        assert out.is_file(), proc.stdout[-2000:] + proc.stderr[-2000:]
        got = json.loads(out.read_text(encoding="utf-8"))
        assert got["done"] is True and got["mode"] == "reserve"
        assert got["label_width"] == 328          # the gutter kept: 336 - the bar's 8
        assert got["scroll_height"] == 335
        assert (proc.stdout + proc.stderr).count("SCRIPT ERROR") == 0

    def test_auto_still_flips_on_the_same_text(self, engine, tmp_path):
        """Sensitive: the fixture still sits on the engine's knife-edge — the
        default mode never ends its frame. If a Godot upgrade ends it, this
        arm says so and the reserve rule may be revisited (never deleted)."""
        out = tmp_path / "auto.json"
        with pytest.raises(subprocess.TimeoutExpired):
            _run(engine, "auto", out, timeout=15)
        assert not out.is_file()
