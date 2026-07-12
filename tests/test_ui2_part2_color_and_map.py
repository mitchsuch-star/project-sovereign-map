"""UI Visual Foundation Sweep — Session U2 Part 2 behavior gate.

Pins the U2 Part 2 deliverables per ``docs/UI_VISUAL_FOUNDATION_SPEC.md`` §8:

- **Colour centralization** — the recurring navy/gold/state Colors that were
  duplicated inline across the HUD/ledger/popup scripts now live once in
  ``Utils`` (``UI_*`` Color consts) and the chrome files reference them; the
  migrated literals are gone from those files so the reduction can't regress.
- **Per-type theme font sizes** — ``main_theme.tres`` declares an explicit
  ``font_size`` for ``Label`` / ``LineEdit`` / ``RichTextLabel`` (Button 15 and
  HeadingLabel 22 were already differentiated), completing per-type control.
- **True native-resolution map compensation** — the map renderer displays the
  SubViewport through a ``STRETCH_SCALE`` ``TextureRect`` (``map_display``) and
  sizes the SubViewport to PHYSICAL pixels (logical * content_scale_factor) via
  ``_refresh_map_viewport_resolution``; the pointer/pan/zoom conversions apply
  ``_viewport_pixel_scale()`` so hit-testing stays correct at any UI scale. The
  old stretch-drawing ``SubViewportContainer`` is gone.

Display-only slice (Golden Rule 6): file/text assertions, no game logic. The
crispness itself is the user's ≥2560 visual sign-off (spec's visual gate); the
boot-smoke (0 ``SCRIPT ERROR``) is the manual per-session gate.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT = REPO_ROOT / "godot-client" / "project-sovereign"
SCRIPTS = GODOT / "scripts"
SCENES = GODOT / "scenes"
THEME_PATH = GODOT / "ui" / "main_theme.tres"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# Colour centralization — Utils.UI_* palette + chrome-file migration
# ═══════════════════════════════════════════════════════════════════════════

# Every centralized UI chrome color the migration introduced.
UI_PALETTE_CONSTS = [
    "UI_GOLD",
    "UI_GOLD_BRIGHT",
    "UI_PANEL_BG",
    "UI_ACTIVE_TAB_BG",
    "UI_POPUP_BG",
    "UI_TEXT_DIM",
    "UI_ALERT",
    "UI_WARNING",
    "UI_SCORE_POSITIVE",
    "UI_SCORE_NEGATIVE",
    "UI_SCORE_NEUTRAL",
    "UI_BAR_BG",
]


def test_utils_defines_ui_chrome_palette():
    text = _read(SCRIPTS / "utils.gd")
    for const in UI_PALETTE_CONSTS:
        assert re.search(rf"(?m)^const {const}\s*:=\s*Color\(", text), (
            f"utils.gd must define the centralized UI chrome color {const}"
        )


def test_ui_gold_matches_theme_and_string_palette():
    # The centralized Color-object gold must match the BBCode hex COLOR_GOLD
    # (d9c08c = 217,192,140 = 0.851,0.753,0.549) and the theme's Button accent.
    text = _read(SCRIPTS / "utils.gd")
    m = re.search(r"(?m)^const UI_GOLD\s*:=\s*Color\(([^)]*)\)", text)
    assert m, "UI_GOLD not found"
    r, g, b = (float(x) for x in m.group(1).split(",")[:3])
    assert abs(r - 0.85) < 0.01 and abs(g - 0.75) < 0.01 and abs(b - 0.55) < 0.01


# (file, must-reference, migrated-literal-that-must-be-gone)
MIGRATION_CASES = [
    ("top_bar.gd", "Utils.UI_ACTIVE_TAB_BG", "Color(0.25, 0.22, 0.15, 1.0)"),
    ("top_bar.gd", "Utils.UI_PANEL_BG", "Color(0.12, 0.14, 0.18, 1.0)"),
    ("top_bar.gd", "Utils.UI_GOLD", None),
    ("top_bar.gd", "Utils.UI_ALERT", None),
    ("top_bar.gd", "Utils.UI_WARNING", None),
    ("top_bar.gd", "Utils.UI_TEXT_DIM", None),
    ("diplomatic_ledger.gd", "Utils.UI_ACTIVE_TAB_BG", "Color(0.25, 0.22, 0.15, 1.0)"),
    ("diplomatic_ledger.gd", "Utils.UI_PANEL_BG", "Color(0.12, 0.14, 0.18, 1.0)"),
    ("diplomatic_ledger.gd", "Utils.UI_GOLD", None),
    ("strategic_ledger.gd", "Utils.UI_ACTIVE_TAB_BG", "Color(0.25, 0.22, 0.15, 1.0)"),
    ("strategic_ledger.gd", "Utils.UI_PANEL_BG", "Color(0.12, 0.14, 0.18, 1.0)"),
    ("strategic_ledger.gd", "Utils.UI_GOLD", None),
    ("popup_base.gd", "Utils.UI_POPUP_BG", "Color(0.1, 0.1, 0.18, 0.95)"),
    ("war_status_panel.gd", "Utils.UI_SCORE_POSITIVE", None),
    ("war_status_panel.gd", "Utils.UI_BAR_BG", "Color(0.15, 0.15, 0.2, 0.8)"),
    ("war_detail_popup.gd", "Utils.UI_BAR_BG", "Color(0.15, 0.15, 0.2, 0.8)"),
    ("war_detail_popup.gd", "Utils.UI_SCORE_POSITIVE", None),
]


def test_chrome_files_reference_centralized_palette():
    for fname, must_have, _gone in MIGRATION_CASES:
        text = _read(SCRIPTS / fname)
        assert must_have in text, f"{fname} must reference {must_have}"


def test_migrated_literals_are_gone():
    # Locks the reduction: the exact inline literals the migration replaced must
    # no longer appear in the migrated file (guards silent drift back to inline).
    for fname, _have, gone in MIGRATION_CASES:
        if gone is None:
            continue
        text = _read(SCRIPTS / fname)
        assert gone not in text, (
            f"{fname} still inlines {gone} — use the Utils.UI_* constant"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Per-type theme font sizes
# ═══════════════════════════════════════════════════════════════════════════


def test_theme_declares_per_type_font_sizes():
    text = _read(THEME_PATH)
    for key in (
        r"Button/font_sizes/font_size\s*=\s*15",
        r"Label/font_sizes/font_size\s*=\s*16",
        r"LineEdit/font_sizes/font_size\s*=\s*16",
        r"RichTextLabel/font_sizes/normal_font_size\s*=\s*16",
        r"HeadingLabel/font_sizes/font_size\s*=\s*22",
    ):
        assert re.search(rf"(?m)^{key}\b", text), (
            f"main_theme.tres must declare per-type font size: {key}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Native-resolution map compensation
# ═══════════════════════════════════════════════════════════════════════════


def _renderer() -> str:
    return _read(SCENES / "map_renderer_base.gd")


def test_renderer_drops_subviewport_container():
    # The stretch-drawing container is replaced by a TextureRect display. Check
    # for actual CODE usage (instantiation / type annotation) — the word may
    # still appear in explanatory comments.
    text = _renderer()
    assert "SubViewportContainer.new()" not in text, (
        "map_renderer_base.gd must no longer instantiate a SubViewportContainer "
        "(UI-2 Part 2 displays the SubViewport via a STRETCH_SCALE TextureRect)"
    )
    assert not re.search(r"(?m):\s*SubViewportContainer\b", text), (
        "map_renderer_base.gd must not type a var as SubViewportContainer"
    )


def test_renderer_displays_via_stretch_scale_texture_rect():
    text = _renderer()
    assert re.search(r"(?m)^var map_display\s*:\s*TextureRect", text), (
        "renderer must declare a map_display TextureRect"
    )
    assert "map_display.stretch_mode = TextureRect.STRETCH_SCALE" in text
    assert "map_display.expand_mode = TextureRect.EXPAND_IGNORE_SIZE" in text
    assert "map_display.texture = map_viewport.get_texture()" in text


def test_renderer_sizes_viewport_to_physical_resolution():
    text = _renderer()
    hook = text.split("func _refresh_map_viewport_resolution", 1)
    assert len(hook) == 2, "renderer must define _refresh_map_viewport_resolution"
    body = hook[1].split("\nfunc ", 1)[0]
    assert "map_viewport.size" in body, "must set the SubViewport size"
    assert "_target_content_scale" in body, (
        "must scale the render resolution by content_scale_factor"
    )
    # content scale is read from the window.
    assert "content_scale_factor" in text


def test_pointer_conversion_accounts_for_viewport_scale():
    text = _renderer()
    # The screen->map conversion must scale the logical offset into viewport px.
    hook = text.split("func _screen_to_map_position", 1)
    assert len(hook) == 2
    body = hook[1].split("\nfunc ", 1)[0]
    assert "_viewport_pixel_scale()" in body, (
        "_screen_to_map_position must apply _viewport_pixel_scale() so hit-"
        "testing stays correct when the SubViewport renders at physical res"
    )


def test_refresh_hook_drives_resolution():
    text = _renderer()
    hook = text.split("func refresh_viewport_scale", 1)
    assert len(hook) == 2, "renderer must define refresh_viewport_scale"
    body = hook[1].split("\nfunc ", 1)[0]
    assert "_refresh_map_viewport_resolution" in body, (
        "refresh_viewport_scale must re-assert the physical render resolution"
    )
    assert "_update_camera_limits" in body
