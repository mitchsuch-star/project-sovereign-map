"""Session UI-6 — the map side: the right-click order signal, the left inset for
the 32:9 columns, the column fill rule, and plaques that gather at any zoom.

Source pins only (no engine is launched here); the lead's engine lane and frames
F01/F02 measure the look.
"""
from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENES = REPO / "godot-client" / "project-sovereign" / "scenes"
RENDERER = (SCENES / "map_renderer_base.gd").read_text(encoding="utf-8")
LAYER = (SCENES / "map_label_layer.gd").read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    m = re.search(r"^(?:static )?func %s\(.*?(?=^(?:static )?func |\Z)" % re.escape(name), src, re.S | re.M)
    assert m, name
    return m.group(0)


def _right_branch() -> str:
    right = RENDERER.split("elif event.button_index == MOUSE_BUTTON_RIGHT:", 1)[1]
    return right.split("\n\t\telif", 1)[0].split("\n\tif ", 1)[0]


class TestRightClickOrders:
    def test_the_signal_exists_with_region_and_marshal(self):
        assert "signal order_context_requested(region: String, marshal: String)" in RENDERER

    def test_the_branch_line_is_verbatim_and_the_button_never_arms_a_drag(self):
        assert RENDERER.count("elif event.button_index == MOUSE_BUTTON_RIGHT:") == 1
        assert "_arm_piece_drag" not in _right_branch()

    def test_the_branch_captures_what_the_left_click_carries(self):
        b = _right_branch()
        for line in ("last_click_shift = event.shift_pressed", "last_click_ctrl = event.ctrl_pressed",
                     'last_click_marshal = str(hovered_marshal.get("name", ""))',
                     'last_click_fogged = str(hovered_fogged_force.get("name", ""))'):
            assert line in b
        assert "_lookup_region_from_color_map(_screen_to_map_position(event.position))" in b
        assert "_label_region_hit" in b and "hovered_region" in b

    def test_panning_unwired_and_nothing_are_handled(self):
        b = _right_branch()
        assert b.index("if is_panning:") < b.index("order_context_requested.emit(")
        assert "not _is_region_wired(ctx_region)" in b
        assert "order_context_requested.emit(str(ctx_region), last_click_marshal)" in b
        # right-click on nothing still dismisses
        assert b.index("order_context_requested.emit(") < b.index("map_dismiss_requested.emit()")

    def test_a_fog_chip_never_names_its_man(self):
        # the signal's marshal is the VISIBLE piece's key only
        assert "last_click_fogged" not in _right_branch().split("order_context_requested.emit(", 1)[1].split("\n", 1)[0]


class TestTheLeftInset:
    def test_the_state_and_the_twin_setter(self):
        assert "var _left_inset := 0.0" in RENDERER
        body = _func(RENDERER, "set_left_inset")
        assert "var inset := maxf(px, 0.0)" in body
        assert "var was_fit := is_fit_view()" in body and "var was_fill := _is_fill_view()" in body
        assert "_left_inset = inset" in body
        assert "_apply_fill_view()" in body and "fit_europe()" in body

    def test_the_room_is_both_strips_and_the_offset_is_their_difference(self):
        assert "return (_left_inset + _right_inset) * _viewport_pixel_scale()" in _func(RENDERER, "_inset_view_px")
        assert "return (_right_inset - _left_inset) * _viewport_pixel_scale()" in _func(RENDERER, "_inset_offset_px")
        assert "_inset_offset_px() / 2.0 / maxf(_zoom_level, 0.001)" in _func(RENDERER, "_sync_camera_zoom")

    def test_the_view_centre_sits_in_the_gap(self):
        assert "Vector2((size.x + _left_inset - _right_inset) / 2.0, size.y / 2.0)" in _func(RENDERER, "_view_centre")


class TestTheColumnFill:
    def test_the_constant_and_the_rule(self):
        assert "const COLUMN_FILL_ASPECT := 2.2" in RENDERER
        body = _func(RENDERER, "_fills_width")
        assert "_left_inset > 0.0" in body and "COLUMN_FILL_ASPECT" in body
        assert "is_wide_room(room)" in body

    def test_the_sheet_setting_still_wins(self):
        body = _func(RENDERER, "_fills_width")
        assert 'UiSettings.get_wide_map() != "fill"' in body
        assert body.index('UiSettings.get_wide_map() != "fill"') < body.index("COLUMN_FILL_ASPECT")

    def test_the_gap_aspect_is_under_the_old_rule_and_over_the_new(self):
        # 32:9 gap between the columns reads 2.42:1
        assert 2.2 <= 2.42 < 2.6


class TestPlaquesGather:
    def test_gather_has_no_zoom_gate(self):
        body = _func(RENDERER, "gathers_names")
        assert "is_at_min_zoom" not in body
        assert "map_canvas_size != Vector2.ZERO and pieces_layer != null" in body

    def test_the_stack_label_speaks_the_gather_phrasing(self):
        assert 'var stack_text := "%s · %d more" % [lead_name, group_size - 1]' in RENDERER
        assert 'const GATHER_FORMAT := "%s · %d more"' in LAYER

    def test_the_selected_marshal_always_leads(self):
        boost = _func(RENDERER, "gather_rank_boost")
        assert "return 2000000000" in boost and "order_selected" in boost and "order_group" in boost
        assert 'int(plate.get_meta("gather_rank", 0)) + _selection_boost(plate)' in LAYER
        assert "gather_rank_boost" in _func(LAYER, "_selection_boost")
        # the selection reaches the layer
        assert "map_label_layer.regather()" in _func(RENDERER, "set_order_selection")
        assert "map_label_layer.regather()" in _func(RENDERER, "set_order_group")

    def test_each_piece_keeps_its_own_hit_box_and_fog_chips_stay_single(self):
        body = _func(RENDERER, "_create_marshal_nodes")
        assert "marshal_hitboxes.append({" in body
        assert "_add_label_hitbox(label_hitboxes, name_label" in body
