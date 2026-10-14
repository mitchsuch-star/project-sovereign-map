"""UXR-3 fixes — Pre-Deploy S12 part 2 (October 14, 2026).

S12 part 1's re-read (`docs/audits/UXR3_REREAD_2026_10_13.md`) left 28 of the
review's 73 rows open and filed five more (UXR3-74 … 78). Part 2 closes them in
the order `docs/NEXT_SESSION_PROMPT.md` decided:

  Part 1  the grip and the plate — the one R5 cause on 81 surfaces (UXR3-74),
          the tableau's nameplate (UXR3-75), the grips and ornaments off the
          content (UXR3-F4), the tableau's buttons off its filigree (F2).

Rules `SYSTEMS_REFERENCE.md` §113.7. The pins are engine-free: the source is
the subject. The driven proof of the grips is `tests/test_uxr2_grips_driven.py`
(unchanged), and the action probe's record of every grip as a `drag` control
is pinned in `tests/test_uxr3_the_review.py`'s rails class.
"""
from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"
TOOLS = REPO / "tools"


def _src(rel: str) -> str:
    return (PROJECT / rel).read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    """The body of one GDScript func (to the next top-level func)."""
    m = re.search(rf"(?ms)^(?:static )?func {re.escape(name)}\(.*?(?=^(?:static )?func |^const |\Z)", src)
    assert m, name
    return m.group(0)


def _const(src: str, name: str) -> str:
    m = re.search(rf"(?m)^const {re.escape(name)}(?:: [^=]+)? :?= (.+)$", src)
    assert m, name
    return m.group(1).strip()


GRIP = _src("scripts/resize_grip.gd")
GRIP_SIZE = float(_const(GRIP, "GRIP_SIZE"))
QUADRANT = GRIP_SIZE / 2.0
# The six centred screens that carry a grip (ResizeGrip.attach_centered).
CENTRED = ("dispatch_view", "gazette_view", "campaign_log", "marshal_management",
           "strategic_ledger", "diplomatic_ledger")


def _panel_margins(scene: str) -> dict:
    """The content margins of the scene's first StyleBox sub-resource (the
    PanelContainer's panel)."""
    text = (SCENES / f"{scene}.tscn").read_text(encoding="utf-8")
    out = {}
    for side in ("left", "top", "right", "bottom"):
        m = re.search(rf"(?m)^content_margin_{side} = ([0-9.]+)$", text)
        assert m, (scene, side)
        out[side] = float(m.group(1))
    return out


# ═══ Part 1 — the grip and the plate ══════════════════════════════════════════

class TestTheGripSaysDrag:
    """UXR3-74: the boxed four-arrow tile read as a button (R5 on 81 surfaces).
    The grip is a borderless corner hatch of three diagonal strokes in
    UI_GOLD at 0.7 alpha, and every grip says what it does."""

    def test_no_box_and_no_arrows(self):
        make = _func(GRIP, "make")
        assert 'add_theme_stylebox_override("panel", StyleBoxEmpty.new())' in make
        for gone in ("StyleBoxFlat", "arrows-out", "TextureRect", "set_border_width_all"):
            assert gone not in make, gone

    def test_three_strokes_in_gold_at_seven_tenths(self):
        steps = _const(GRIP, "HATCH_STEPS")
        assert len(re.findall(r"[0-9.]+", steps)) == 3, steps
        assert _const(GRIP, "HATCH_ALPHA") == "0.7"
        draw = _func(GRIP, "_draw")
        assert "Color(Utils.UI_GOLD, HATCH_ALPHA)" in draw
        assert "for k in HATCH_STEPS:" in draw and "draw_line(" in draw

    def test_the_hatch_lies_in_the_inner_quadrant(self):
        """The 24-px hit square stays centred on the corner (the driven test's
        `grip_gap`); every stroke lies in its inner quadrant, inside the
        panel, so what the grip DRAWS never leaves its panel's padding."""
        steps = [float(x) for x in re.findall(r"[0-9.]+", _const(GRIP, "HATCH_STEPS"))]
        inset = float(_const(GRIP, "HATCH_INSET"))
        assert inset + max(steps) <= QUADRANT, (inset, steps, QUADRANT)
        assert "position = _corner_point(_target.get_global_rect(), corner) - size * 0.5" in GRIP

    def test_every_grip_says_drag_to_resize(self):
        assert _const(GRIP, "TOOLTIP") == '"Drag to resize · double-click to restore"'
        assert GRIP.count("make(Corner.BOTTOM_RIGHT,\n\t\t\tTOOLTIP)") + GRIP.count("make(grip_corner,\n\t\t\tTOOLTIP)") == 2
        main = _src("scripts/main.gd")
        assert "ResizeGrip.make(ResizeGrip.Corner.TOP_RIGHT, ResizeGrip.TOOLTIP)" in main
        for path in SCRIPTS.glob("*.gd"):
            if path.name == "resize_grip.gd":
                continue
            assert "Drag to resize" not in path.read_text(encoding="utf-8"), path.name

    def test_the_command_windows_grip_reads_the_event_not_the_os_cursor(self):
        """The shared grip's rule (the event's own position): the probe's
        pushed drag never moves the OS cursor, and neither does a player's
        drag through a scaled canvas need it."""
        body = _func(_src("scripts/main.gd"), "_on_grip_gui_input")
        assert "get_global_mouse_position" not in body
        assert body.count("event.global_position") == 2


class TestTheGripSitsOffTheContent:
    """UXR3-F4: no grip or corner ornament on text or a control. The census on
    the closing re-read's frame records holds the rects; these hold the
    geometry that makes it so."""

    def test_every_centred_screen_pads_the_corner_the_grip_draws_in(self):
        for scene in CENTRED:
            m = _panel_margins(scene)
            assert m["right"] >= QUADRANT and m["bottom"] >= QUADRANT, (scene, m)

    def test_the_war_hud_pads_its_top_left_corner(self):
        m = _panel_margins("war_status_panel")
        assert m["top"] >= QUADRANT, m
        ws = _src("scripts/war_status_panel.gd")
        # the shrink-wrap covers the new top margin (12 + 4 + slack)
        assert "vbox.get_combined_minimum_size().y + 18.0" in ws
        assert 'ResizeGrip.attach_edge(panel_container, "war_status", ResizeGrip.Corner.TOP_LEFT)' in ws

    def test_the_generals_filigree_sits_in_the_bottom_band(self):
        """Each corner ornament lies below the content box (it covered the
        last skill bar), and the right one clear of the grip's quadrant."""
        text = (SCENES / "marshal_management.tscn").read_text(encoding="utf-8")
        m = _panel_margins("marshal_management")
        for name in ("FiligreeBottomLeft", "FiligreeBottomRight"):
            block = re.search(rf'(?ms)^\[node name="{name}".*?(?=^\[|\Z)', text).group(0)
            assert 'groups=["corner_ornaments"]' in block, name
            top = float(re.search(r"offset_top = (-?[0-9.]+)", block).group(1))
            bottom = float(re.search(r"offset_bottom = (-?[0-9.]+)", block).group(1))
            assert top >= 0.0 and bottom <= m["bottom"], (name, top, bottom)
            if name.endswith("Right"):
                right = float(re.search(r"offset_right = (-?[0-9.]+)", block).group(1))
                assert right <= m["right"] - QUADRANT, (right, m)

    def test_the_capture_harness_records_the_grips_and_ornaments(self):
        gd = (TOOLS / "iq10_surface_screenshot.gd").read_text(encoding="utf-8")
        assert 'frame["grips"] = _grips_and_ornaments()' in gd
        body = _func(gd, "_grips_and_ornaments")
        assert "n is ResizeGrip" in body and 'is_in_group("corner_ornaments")' in body


class TestThePlateIsAnEngravedLabel:
    """UXR3-75: the gold-filled, bordered nameplate stood in the button row
    and read as the main button. It is a flat engraved label: no fill, no
    border, no hover; the same words in the same place."""

    def test_no_fill_and_no_border(self):
        body = _func(_src("scripts/battle_diorama.gd"), "_build_verdict_and_plate")
        plate = body[body.index("_nameplate = PanelContainer.new()"):body.index("var plate_box")]
        assert "StyleBoxEmpty.new()" in plate and "StyleBoxFlat" not in plate
        assert "bg_color" not in plate and "border" not in plate.replace("no border", "")
        assert "_nameplate.mouse_filter = Control.MOUSE_FILTER_IGNORE" in plate
        # the margins keep its size, so it keeps its place
        for side in ("left", "right"):
            assert f"engraved.content_margin_{side} = 26.0" in plate
        for side in ("top", "bottom"):
            assert f"engraved.content_margin_{side} = 5.0" in plate

    def test_the_words_read_on_the_walnut(self):
        """Brass text on WOOD_BG: the name 6.0 : 1, the sub-line 4.6 : 1."""
        src = _src("scripts/battle_diorama.gd")

        def lum(rgb):
            def lin(c):
                return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
            r, g, b = (lin(float(x)) for x in rgb)
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        def rgb(name):
            return re.findall(r"[0-9.]+", _const(src, name))[:3]

        wood = lum(rgb("WOOD_BG"))
        for name, floor in (("BRASS", 4.5), ("PLATE_SUB", 3.0)):
            ratio = (lum(rgb(name)) + 0.05) / (wood + 0.05)
            assert ratio >= floor, (name, ratio)
        body = _func(src, "_build_verdict_and_plate")
        assert '_plate_name.add_theme_color_override("font_color", BRASS)' in body
        assert '_plate_sub.add_theme_color_override("font_color", PLATE_SUB)' in body


class TestTheTableausButtonsClearItsFiligree:
    """UXR3-F2's third clause: Close sat on the bottom-right corner ornament."""

    def test_close_ends_left_of_the_corner_ornament(self):
        src = _src("scripts/battle_diorama.gd")
        tray_w = float(_const(src, "TRAY_W"))
        m = re.search(r"_btn_close\.position = Vector2\(TRAY_W - ([0-9.]+), ", src)
        close_left = tray_w - float(m.group(1))
        close_w = float(re.search(r"_btn_close\.custom_minimum_size = Vector2\(([0-9.]+),", src).group(1))
        fil = _func(src, "_build_filigree")
        assert "TRAY_W - 38.0" in fil and 'fil.add_to_group("corner_ornaments")' in fil
        assert close_left + close_w <= tray_w - 38.0, (close_left, close_w)
