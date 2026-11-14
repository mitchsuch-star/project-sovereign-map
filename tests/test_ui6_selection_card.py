"""Session UI-6 (November 13, 2026) - the selection card, pinned from its source.

`scripts/selection_card.gd` (`class_name SelectionCard`) replaces the two-line selection strip with a card: portrait,
name, status badge, figures, the seven fixed order slots and the hint. Digits arrive from main.gd through
`press_slot`; the card handles no key itself and takes no focus.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SRC = (SCRIPTS / "selection_card.gd").read_text(encoding="utf-8")
KIT = (SCRIPTS / "marshal_state.gd").read_text(encoding="utf-8")


def _func(name: str) -> str:
    start = SRC.index("func " + name + "(")
    m = re.search(r"\n(?:static )?func ", SRC[start + 1:])
    return SRC[start:start + 1 + m.start()] if m else SRC[start:]


class TestTheApi:

    def test_class_and_base(self):
        assert "extends PanelContainer" in SRC
        assert "class_name SelectionCard" in SRC

    def test_signals(self):
        assert "signal verb_pressed(verb: String, marshal: String)" in SRC
        assert "signal cancel_order_pressed(marshal: String)" in SRC
        assert "signal close_pressed" in SRC

    def test_methods(self):
        assert "func show_for(view: Dictionary, marshal: String, actions_left: int, hint_bbcode: String) -> void:" in SRC
        assert "func show_group(names: Array, total_ap: int, in_hand: int, hint_bbcode: String) -> void:" in SRC
        assert "func hide_card() -> void:" in SRC
        assert "func press_slot(n: int) -> bool:" in SRC
        assert "func current_marshal() -> String:" in SRC


class TestTheSlots:

    def test_reads_the_kit_and_draws_all_seven(self):
        assert 'preload("res://scripts/marshal_state.gd")' in SRC
        assert "MarshalStateKit.order_specs(_view)" in _func("_render")
        body = _func("_order_row")
        assert "for spec in _specs:" in body and "flow.add_child(btn)" in body
        assert len(re.findall(r'\{"slot": \d', KIT)) == 7

    def test_locked_is_disabled_with_the_reason_as_hover(self):
        body = _func("_slot_button")
        assert 'btn.disabled = locked' in body
        assert 'var reason := str(spec["reason"])' in body
        assert "btn.tooltip_text = tip" in body
        # an empty reason adds no tooltip text
        assert 'if reason != "":' in body

    def test_face_reads_digit_label_price(self):
        body = _func("_slot_button")
        assert "MarshalStateKit.price_text(int(spec[\"price\"]))" in body
        assert 'btn.text = str(slot) + " " + full' in body

    def test_cancel_slot_has_its_own_signal(self):
        body = _func("_fire")
        assert 'if verb == "cancel":' in body
        assert "cancel_order_pressed.emit(_marshal)" in body
        assert "verb_pressed.emit(verb, _marshal)" in body

    def test_press_slot_denies_locked_or_missing_and_plays_only_that(self):
        body = _func("press_slot")
        assert "AudioManager.play(DENY_CUE)" in body
        assert "return false" in body and "return true" in body
        assert 'bool(spec.get("locked", false))' in body
        assert 'const DENY_CUE := "error"' in SRC
        audio = (SCRIPTS / "audio_manager.gd").read_text(encoding="utf-8")
        assert '"error": {' in audio


class TestTheFaces:

    def test_compact_branch(self):
        render = _func("_render")
        assert "Utils.compact_view()" in render
        assert "Vector2(32.0, 40.0) if compact else Vector2(48.0, 60.0)" in _func("_portrait")
        slot = _func("_slot_button")
        assert "if compact:" in slot and "btn.icon = tex" in slot and 'btn.text = str(slot)\n' in slot
        assert "Utils.glyph(str(spec[\"glyph\"]))" in slot
        width = _func("_card_width")
        assert "Utils.hud_band(" in width and "COMPACT_BAND_SHARE" in width
        assert "const COMPACT_BAND_SHARE := 0.9" in SRC
        # compact: one line clipped at the card's edge; ordinary: wrapped at the card's inner width — both
        # measured, never fit_content (UXR-2's scroll rule)
        hint = _func("_hint_label")
        assert '_measured_rich("Hint", _hint, 0.0 if compact else inner, compact)' in hint
        measured = _func("_measured_rich")
        assert "label.fit_content = false" in measured and "TextServer.AUTOWRAP_OFF" in measured
        assert "fit_content = true" not in SRC

    def test_group_face_has_no_verb_buttons(self):
        render = _func("_render")
        assert "if _group.is_empty():" in render
        group = _func("_group_row")
        assert "march together" in group
        assert "_slot_button" not in group and "Button.new()" not in group

    def test_status_badge_uses_the_kit(self):
        assert "MarshalStateKit.status_of(_view)" in _func("_head_row")


class TestTheHousekeeping:

    def test_every_button_takes_no_focus(self):
        buttons = SRC.count("Button.new()")
        assert buttons >= 2
        assert SRC.count("focus_mode = Control.FOCUS_NONE") == buttons

    def test_mouse_filter_stop_on_the_card(self):
        assert "mouse_filter = Control.MOUSE_FILTER_STOP" in _func("_init")

    def test_no_input_handling_of_its_own(self):
        assert not re.search(r"func _(unhandled_)?(shortcut_)?input\(", SRC)
        assert "InputEventKey" not in SRC

    def test_no_or_picks_a_value(self):
        assert not re.search(r"str\([^)]*\bor\b", SRC)
        assert not re.search(r"\.get\([^)]*\)\s+or\s+\w", SRC)

    def test_no_new_hex_or_font_size_tags(self):
        assert not re.search(r'Color\.html\(|Color\("#|#[0-9a-fA-F]{6}\b', SRC)
        assert "[font_size" not in SRC
