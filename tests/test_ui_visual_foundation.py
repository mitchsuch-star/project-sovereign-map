"""UI Visual Foundation Sweep — Session U1 (UI-1) behavior gate.

Pins the UI-1 deliverables per ``docs/UI_VISUAL_FOUNDATION_SPEC.md`` §4/§5/§8:

- ``project.godot`` registers the custom theme (``gui/theme/custom``).
- ``ui/main_theme.tres`` exists, parses as a Godot Theme resource, and defines
  the four Button styleboxes, the ``PanelContainer`` panel, the ``HeadingLabel``
  type variation, and a default font at size 16.
- The three UI-1 font families (Cinzel / EB Garamond / Source Sans 3) ship as
  ``.ttf`` with their ``OFL.txt`` license and a committed Godot ``.import``
  sidecar (pins the resource UID the theme references).
- A portrait exists for every ``europe_1805.json`` marshal — the 21 active
  marshals AND the recruitment ``marshal_pool`` — EXCEPT Abdurrahman, who is
  left unillustrated by design (no confident public-domain likeness; §2).

Display-only slice (Golden Rule 6): these are file/format assertions, no game
logic. The engine boot-smoke (0 ``SCRIPT ERROR``) is a manual per-session gate
(§8) that pytest cannot observe — GDScript parse errors are invisible to Python.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT_PROJ = REPO_ROOT / "godot-client" / "project-sovereign"
PROJECT_GODOT = GODOT_PROJ / "project.godot"
THEME_PATH = GODOT_PROJ / "ui" / "main_theme.tres"
FONTS_DIR = GODOT_PROJ / "assets" / "fonts"
PORTRAITS_DIR = GODOT_PROJ / "assets" / "portraits"
EUROPE_1805 = GODOT_PROJ / "assets" / "maps" / "europe_1805.json"

# The three UI-1 families: (ttf filename, OFL filename). Variable-weight faces.
UI1_FONTS = [
    ("Cinzel[wght].ttf", "Cinzel-OFL.txt"),
    ("EBGaramond[wght].ttf", "EBGaramond-OFL.txt"),
    ("SourceSans3[wght].ttf", "SourceSans3-OFL.txt"),
]

# Marshal with no confident PD portrait — unillustrated by design (spec §2).
PORTRAIT_EXEMPT = {"Abdurrahman"}
PORTRAIT_EXTS = (".jpg", ".png", ".jpeg", ".webp")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# project.godot registration
# ═══════════════════════════════════════════════════════════════════════════


def test_project_godot_registers_custom_theme():
    assert PROJECT_GODOT.exists(), f"missing {PROJECT_GODOT}"
    text = _read(PROJECT_GODOT)
    # gui/theme/custom lives under the [gui] section as `theme/custom=...`.
    assert re.search(
        r'(?m)^\s*theme/custom\s*=\s*"res://ui/main_theme\.tres"\s*$', text
    ), "project.godot must register gui/theme/custom = res://ui/main_theme.tres"
    assert "[gui]" in text, "project.godot must have a [gui] section for the theme"


# ═══════════════════════════════════════════════════════════════════════════
# main_theme.tres presence + shape
# ═══════════════════════════════════════════════════════════════════════════


def test_main_theme_exists_and_parses_as_theme_resource():
    assert THEME_PATH.exists(), f"missing {THEME_PATH}"
    text = _read(THEME_PATH)
    assert text.lstrip().startswith(
        '[gd_resource type="Theme"'
    ), "main_theme.tres must be a Godot Theme resource"
    assert "[resource]" in text, "main_theme.tres must have a [resource] block"


def test_theme_sets_default_font_and_size():
    text = _read(THEME_PATH)
    assert re.search(
        r"(?m)^default_font\s*=\s*ExtResource", text
    ), "theme must set a default_font"
    assert re.search(
        r"(?m)^default_font_size\s*=\s*16\b", text
    ), "theme default_font_size must be 16 (§3)"


def test_theme_defines_four_button_styleboxes():
    text = _read(THEME_PATH)
    for state in ("normal", "hover", "pressed", "disabled"):
        assert re.search(
            rf"(?m)^Button/styles/{state}\s*=\s*SubResource", text
        ), f"theme must define Button/styles/{state}"


def test_theme_defines_panelcontainer_panel():
    text = _read(THEME_PATH)
    assert re.search(
        r"(?m)^PanelContainer/styles/panel\s*=\s*SubResource", text
    ), "theme must define PanelContainer/styles/panel"


def test_theme_defines_heading_label_variation_on_label():
    text = _read(THEME_PATH)
    assert re.search(
        r'(?m)^HeadingLabel/base_type\s*=\s*&"Label"', text
    ), "HeadingLabel must be a type variation of Label"
    assert re.search(
        r"(?m)^HeadingLabel/fonts/font\s*=\s*SubResource", text
    ), "HeadingLabel must carry a Cinzel FontVariation"
    assert re.search(
        r"(?m)^HeadingLabel/colors/font_outline_color\s*=", text
    ), "HeadingLabel must carry a navy outline color (§3)"


def test_theme_references_cinzel_and_ebgaramond():
    text = _read(THEME_PATH)
    assert "res://assets/fonts/Cinzel[wght].ttf" in text
    assert "res://assets/fonts/EBGaramond[wght].ttf" in text


# ═══════════════════════════════════════════════════════════════════════════
# Fonts on disk: .ttf + OFL + committed .import sidecar
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize("ttf,ofl", UI1_FONTS)
def test_ui1_font_ttf_and_ofl_present(ttf, ofl):
    assert (FONTS_DIR / ttf).exists(), f"missing font {ttf}"
    assert (FONTS_DIR / ofl).exists(), f"missing license {ofl} (OFL required)"


@pytest.mark.parametrize("ttf,_ofl", UI1_FONTS)
def test_ui1_font_import_sidecar_committed(ttf, _ofl):
    # The .import sidecar pins the FontFile UID the theme resolves against;
    # spec §8 U1 requires it committed even though *.import is git-ignored
    # (force-added). The .godot/imported cache is regenerated, not committed.
    sidecar = FONTS_DIR / f"{ttf}.import"
    assert sidecar.exists(), f"missing Godot import sidecar {sidecar.name}"
    body = _read(sidecar)
    assert 'importer="font_data_dynamic"' in body
    assert re.search(r'(?m)^uid="uid://', body), f"{sidecar.name} must pin a uid"


# ═══════════════════════════════════════════════════════════════════════════
# Portrait coverage: every marshal except Abdurrahman
# ═══════════════════════════════════════════════════════════════════════════


def _all_marshal_names() -> set[str]:
    data = json.loads(_read(EUROPE_1805))
    names: set[str] = set(data.get("marshals", {}).keys())
    for nation_bench in (data.get("marshal_pool") or {}).values():
        for m in nation_bench:
            n = m.get("name")
            if isinstance(n, str):
                names.add(n)
    return names


def _has_portrait(name: str) -> bool:
    return any((PORTRAITS_DIR / f"{name}{ext}").exists() for ext in PORTRAIT_EXTS)


def test_portrait_exists_for_every_marshal_except_abdurrahman():
    names = _all_marshal_names()
    assert names, "europe_1805.json yielded no marshal names"
    missing = sorted(
        n for n in names if n not in PORTRAIT_EXEMPT and not _has_portrait(n)
    )
    assert not missing, f"marshals without a portrait: {missing}"


def test_abdurrahman_exemption_is_real():
    # Guards the exemption: if a portrait is ever added, drop him from the
    # exempt set so the coverage test protects him too (spec §2).
    assert not _has_portrait(
        "Abdurrahman"
    ), "Abdurrahman now has a portrait — remove him from PORTRAIT_EXEMPT"
