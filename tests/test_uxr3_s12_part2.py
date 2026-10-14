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


# ═══ Parts 2 and 3 — R6's driven proofs; the never-pressed controls ══════════

class TestAChipUnderAScreenAnswersInPlace:
    """UXR3-27, 40, 45: an order chip on the Generals or either ledger hands
    its order to main.gd, whose terminal echo lies under the screen. The chip
    greys in place to 'Sent: <its words>' — only when main.gd's chip road took
    the order (its in-flight latch can refuse a second press)."""

    def test_the_handshake_in_every_screen(self):
        for rel, signal, meta_var in (("scripts/marshal_management.gd", "order_command.emit(", "meta_str"),
                                      ("scripts/diplomatic_ledger.gd", "vassal_command.emit(command)", "meta_key"),
                                      ("scripts/strategic_ledger.gd", "naval_command.emit(command)", "meta_str")):
            src = _src(rel)
            i = src.index(signal)
            before, after = src[i - 220:i], src[i:i + 220]
            assert "Utils.order_taken = false" in before, rel
            assert f"if Utils.order_taken:\n" in after and f"Utils.mark_chip_sent(content_area, {meta_var})" in after, rel

    def test_main_says_it_took_the_order_after_its_latch(self):
        main = _src("scripts/main.gd")
        for fn in ("_on_reward_command", "_on_vassal_command", "_on_naval_command"):
            body = _func(main, fn)
            latch = body.index("_chip_command_in_flight = true")
            taken = body.index("Utils.order_taken = true")
            assert body.index("if command.is_empty() or _chip_command_in_flight:") < latch < taken, fn

    def test_cancel_greys_when_the_request_is_out(self):
        body = _func(_src("scripts/strategic_ledger.gd"), "_on_meta_clicked")
        i = body.index("_api_client_ref.cancel_strategic_order(marshal_name, _on_cancel_result)")
        assert 'Utils.mark_chip_sent(content_area, meta_str, "Cancel")' in body[i:i + 300]

    def test_the_sent_chip_is_the_disabled_chip_written_through_text(self):
        body = _func(_src("scripts/utils.gd"), "mark_chip_sent")
        assert 'bb_chip_disabled("Sent: " + words)' in body
        assert '"Sent: " + words' in body and "COLOR_INFO" in body
        assert "rtl.text = " in body and "append_text" not in body


class TestTheWarRoomMode:
    """The probe's war-room mode: each hand-off surface opened INSIDE the real
    main.tscn against a sandboxed live backend, the road's control pressed,
    the answer read in the live frame. Its record and the citations it backs
    are the closing re-read's (`docs/audits/uxr3_s12b/`)."""

    def test_the_rails(self):
        gd = (TOOLS / "uxr3_action_probe.gd").read_text(encoding="utf-8")
        assert 'if _war_room and Utils.backend_url().ends_with(":8005"):' in gd
        runner = (TOOLS / "uxr3_action_probe.py").read_text(encoding="utf-8")
        assert "while port == 8005 or not _free(port):" in runner
        assert '"INK_IRON_SAVE_DIR": str(saves)' in runner and '"LLM_MODE": "mock"' in runner
        assert 'assert env["SOVEREIGN_PORT"] != "8005", "never the player\'s 8005"' in runner

    def test_the_roads_cover_every_r6_cross_part_one_left(self):
        """Each road names an IQ-10 shot and a control match; together they
        hold every HANDOFF and NOT PRESSED road part 1's re-read left unproven
        (the HUD pieces shot alone are read in their host, §113.5)."""
        import sys
        sys.path.insert(0, str(TOOLS))
        import iq10_run_captures as R
        import uxr3_action_probe as PROBE
        shots = {s["id"] for s in R.SHOTS}
        ids = [r[0] for r in PROBE.ROADS]
        assert len(ids) == len(set(ids))
        for road, sid, match in PROBE.ROADS:
            assert sid in shots, road
            assert set(match) <= {"kind", "text", "meta_startswith", "path_endswith"}, road
        metas = {m.get("meta_startswith") for _r, _s, m in PROBE.ROADS}
        for need in ("order:", "reward:", "talleyrand_assess", "vassal:", "congress_court:", "do:",
                     "cancel:", "negotiate:", "diorama:"):
            assert need in metas, need
        texts = {m.get("text") for _r, _s, m in PROBE.ROADS}
        for need in ("Save Game", "Load Game", "New Campaign", "Main Menu", "Quit to Desktop"):
            assert need in texts, need

    def test_a_war_room_answer_is_read_in_the_live_frame_only(self):
        gd = (TOOLS / "uxr3_action_probe.gd").read_text(encoding="utf-8")
        assert "changed = _live_only(changed, [before, a2, a3])" in gd
        live = _func(gd, "_live_only")
        assert "floor_now = mini(floor_now" in live
        assert "int(layers.get(key.substr(2), 0)) >= floor_now" in live
        assert 'out.append(scene)    # a scene change leads: it is the answer' in _func(gd, "_describe")
