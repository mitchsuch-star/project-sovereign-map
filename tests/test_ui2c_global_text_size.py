"""UI Visual Foundation Sweep — Session U2c behavior gate: Global Text Size.

Pins the user-requested "Text Size" control + pop-up-wide scaling
(``docs/UI_VISUAL_FOUNDATION_SPEC.md`` §8 U2c):

- The command window's header replaces the old A− / A+ pair with a labelled
  "Text Size" control: a ``TextSizeLabel`` reading "Text Size" beside a
  ``TextSizeButtons`` VBox holding a ``+`` button STACKED ATOP a ``−`` button
  ("plus and minus … one atop the other").
- Those buttons drive the GLOBAL ``content_scale_factor`` (the same value the
  pause-menu "Interface Scale" slider writes), which scales every CanvasLayer
  pop-up / ledger — so "make all pop-ups adjustable" is satisfied by one control
  rather than a per-pop-up widget.
- The pause menu re-reads the saved scale on open so its slider never disagrees
  with a change made from the Text Size buttons.

Display-only slice (Golden Rule 6): file/text assertions, no game logic. The
engine boot-smoke (0 ``SCRIPT ERROR``) is the manual per-session gate.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT = REPO_ROOT / "godot-client" / "project-sovereign"
SCRIPTS = GODOT / "scripts"
SCENES = GODOT / "scenes"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# main.tscn — the "Text Size" control (label + stacked +/-)
# ═══════════════════════════════════════════════════════════════════════════


def test_tscn_has_text_size_label():
    text = _read(SCENES / "main.tscn")
    assert '[node name="TextSizeLabel"' in text
    assert 'text = "Text Size"' in text


def test_tscn_has_stacked_plus_over_minus_buttons():
    text = _read(SCENES / "main.tscn")
    # Both buttons live inside the vertical TextSizeButtons box.
    assert '[node name="TextSizeButtons" type="VBoxContainer"' in text
    up_marker = 'name="ScaleUpButton" type="Button" parent="' + (
        "BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/"
        "TitleRow/TextSizeBox/TextSizeButtons"
    )
    down_marker = 'name="ScaleDownButton" type="Button" parent="' + (
        "BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/"
        "TitleRow/TextSizeBox/TextSizeButtons"
    )
    up_idx = text.find(up_marker)
    down_idx = text.find(down_marker)
    assert up_idx != -1, "ScaleUpButton must live under TextSizeButtons"
    assert down_idx != -1, "ScaleDownButton must live under TextSizeButtons"
    # A VBox serializes children top-to-bottom: '+' must come before '−'.
    assert up_idx < down_idx, "the + button must sit ATOP the − button"
    # And they show the plus / minus glyphs, not the old 'A+' / 'A−'.
    assert 'text = "+"' in text
    assert 'text = "−"' in text
    assert 'text = "A+"' not in text and 'text = "A−"' not in text


# ═══════════════════════════════════════════════════════════════════════════
# main.gd — @onready wiring + global-scale stepping
# ═══════════════════════════════════════════════════════════════════════════


def test_main_onready_points_at_stacked_buttons():
    text = _read(SCRIPTS / "main.gd")
    suffix = "TitleRow/TextSizeBox/TextSizeButtons/ScaleUpButton"
    assert suffix in text, "scale_up_button @onready must point at the new stacked path"
    assert "TitleRow/TextSizeBox/TextSizeButtons/ScaleDownButton" in text
    assert "text_size_label" in text


def test_main_step_reuses_apply_ui_scale():
    text = _read(SCRIPTS / "main.gd")
    # _step_ui_scale must route through _apply_ui_scale (map compensation +
    # persistence + terminal relayout live there) rather than a bespoke path.
    body = text.split("func _step_ui_scale", 1)
    assert len(body) == 2, "main.gd must define _step_ui_scale"
    step_body = body[1].split("\nfunc ", 1)[0]
    assert "_apply_ui_scale(" in step_body
    assert "UI_SCALE_BUTTON_STEP" in step_body


# ═══════════════════════════════════════════════════════════════════════════
# pause_menu.gd — the slider stays in sync with the Text Size buttons
# ═══════════════════════════════════════════════════════════════════════════


def test_pause_menu_resyncs_slider_on_open():
    text = _read(SCRIPTS / "pause_menu.gd")
    open_body = text.split("func open_menu", 1)
    assert len(open_body) == 2, "pause_menu.gd must define open_menu"
    body = open_body[1].split("\nfunc ", 1)[0]
    assert "set_value_no_signal(UiSettings.get_ui_scale())" in body, (
        "open_menu must re-read the saved scale so the slider matches the "
        "Text Size buttons"
    )
