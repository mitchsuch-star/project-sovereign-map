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

# ── War-Table Pieces (UI-4, spec §7) ────────────────────────────────────────
PIECES_DIR = GODOT_PROJ / "assets" / "ui" / "pieces"
PIECE_ARMS = ("infantry", "cavalry", "artillery")
PIECE_LAYERS = ("base", "shadow", "coat", "body")  # bottom->top compositing order
PIECE_FACINGS = ("r", "l")                          # nose-right + mirrored


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


# ═══════════════════════════════════════════════════════════════════════════
# Session U3 (UI-3) — texture / icon / portrait polish
# ═══════════════════════════════════════════════════════════════════════════
#
# The curated icon sets are tinted gold at render (BBCode [img color=...] /
# Button icon_*_color). That multiply only works on a WHITE silhouette, so the
# wired icons must have been recolored off their shipped defaults: game-icons
# carry a 512² black background <path> and phosphor uses currentColor (Godot
# rasterizes it black — modulate cannot lighten black). These guard that the
# preprocessing is not silently reverted (display-only, GR6).

ICONS_DIR = GODOT_PROJ / "assets" / "ui" / "icons"
ORNAMENTS_DIR = GODOT_PROJ / "assets" / "ui" / "ornaments"
MARSHAL_MGMT_TSCN = GODOT_PROJ / "scenes" / "marshal_management.tscn"

# game-icons wired inline in the Generals cards + commission bench.
GAME_ICONS_WIRED = ["unit-infantry", "unit-cavalry", "unit-artillery"]
# phosphor icons wired on buttons / inline (close X, top-bar nav, resize grip,
# Text-Size, marshal-card headers).
PHOSPHOR_WIRED = [
    "x", "arrows-out", "medal-military", "crown",
    "list", "map-trifold", "users-three", "handshake", "scroll",
]


@pytest.mark.parametrize("name", GAME_ICONS_WIRED)
def test_game_icon_black_background_stripped(name):
    svg = _read(ICONS_DIR / "game-icons" / f"{name}.svg")
    assert 'd="M0 0h512v512H0z"' not in svg, (
        f"game-icons/{name}.svg still carries the 512² black bg <path> — the "
        f"gold [img color=...] tint would render a black box (spec §8 U3)"
    )


@pytest.mark.parametrize("name", PHOSPHOR_WIRED)
def test_phosphor_icon_recolored_off_currentcolor(name):
    svg = _read(ICONS_DIR / "phosphor" / f"{name}.svg")
    assert "currentColor" not in svg, (
        f"phosphor/{name}.svg still uses currentColor — Godot rasterizes it "
        f"black and modulate cannot lighten black to gold (spec §8 U3)"
    )


def test_filigree_ornament_recolored_white():
    svg = _read(ORNAMENTS_DIR / "corner_floral_01.svg")
    assert "#000000" not in svg, (
        "corner_floral_01.svg is still black fill — the gold modulate on the "
        "Generals filigree corners would render it black (spec §8 U3)"
    )


def test_theme_panel_uses_leather_texture():
    text = _read(THEME_PATH)
    assert "StyleBoxTexture" in text, (
        "main_theme.tres must define a StyleBoxTexture (UI-3 leather panel fill)"
    )
    assert "fabric_leather_01_diff_1k.jpg" in text, (
        "the UI-3 panel StyleBoxTexture must reference the leather texture asset"
    )
    assert re.search(
        r'(?m)^PanelContainer/styles/panel\s*=\s*SubResource\("StyleBoxTexture',
        text,
    ), "PanelContainer/panel must be wired to the leather StyleBoxTexture (UI-3)"


def test_generals_scene_has_filigree_corners():
    text = _read(MARSHAL_MGMT_TSCN)
    assert "corner_floral_01.svg" in text, (
        "the Generals scene must reference the corner filigree ornament (UI-3)"
    )
    assert text.count('type="TextureRect"') >= 2, (
        "the Generals scene must carry the two filigree corner TextureRects (UI-3)"
    )


# UI-3 wires two assets BY UID in committed resources (leather in main_theme.tres,
# corner_floral in the Generals scene). Their .import sidecars pin those UIDs and
# are force-added (like the UI-1 font sidecars) so a clean clone resolves the UID
# without an invalid-reference warning before the first --import (spec §8 UI-0/U3,
# same precedent as test_ui1_font_import_sidecar_committed).
UI3_UID_SIDECARS = [
    ("assets/textures/fabric_leather_01_diff_1k.jpg.import", THEME_PATH),
    ("assets/ui/ornaments/corner_floral_01.svg.import", MARSHAL_MGMT_TSCN),
]


@pytest.mark.parametrize("sidecar_rel,referrer_path", UI3_UID_SIDECARS)
def test_ui3_uid_referenced_import_sidecar_present_and_matches(sidecar_rel, referrer_path):
    sidecar = GODOT_PROJ / sidecar_rel
    assert sidecar.exists(), f"missing UID-pinning import sidecar {sidecar.name}"
    m = re.search(r'(?m)^uid="(uid://[a-z0-9]+)"', _read(sidecar))
    assert m, f"{sidecar.name} must pin a uid"
    uid = m.group(1)
    assert uid in _read(referrer_path), (
        f"{sidecar.name} uid {uid} does not match the ext_resource UID in "
        f"{referrer_path.name} — a UID drift would break the reference on a "
        f"clean clone"
    )


# ═══════════════════════════════════════════════════════════════════════════
# War-Table Pieces (UI-4) — tin-flat map-piece sprites (spec §7)
#
# The three arm flats (infantry / cavalry / artillery) each ship four layered
# PNGs — base disc / contact shadow / faction coat-mask / figure body — in both
# facings, so U5's Godot code can Y-sort them and tint the coat via `modulate`
# (Utils.NATION_COLORS) while metal/base stay neutral. These assertions guard
# the ART (existence, format, non-blank cutout). The "each active marshal
# renders a piece keyed to its dominant arm" behaviour is owned by session U5
# (spec §8 U5 checklist), which lands the placement code + its own test.
#
# PNG parsing is stdlib-only (struct + zlib) so the pre-commit suite gains no
# Pillow dependency — the offline generator (tools/gen_war_table_pieces.py) is
# the only thing that needs Pillow/numpy, and CI never runs it.
# ═══════════════════════════════════════════════════════════════════════════

import struct  # noqa: E402
import zlib  # noqa: E402

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _png_header(path: Path):
    """(width, height, bit_depth, color_type) from the IHDR — no decode."""
    data = path.read_bytes()
    assert data[:8] == _PNG_MAGIC, f"{path.name} is not a PNG"
    assert data[12:16] == b"IHDR", f"{path.name} has no IHDR"
    w, h, bit_depth, color_type = struct.unpack(">IIBB", data[16:26])
    return data, w, h, bit_depth, color_type


def _idat_raw(data: bytes) -> bytes:
    """Concatenate + inflate every IDAT chunk (fast C zlib)."""
    idat = bytearray()
    off = 8
    while off < len(data):
        (ln,) = struct.unpack(">I", data[off:off + 4])
        typ = data[off + 4:off + 8]
        if typ == b"IDAT":
            idat += data[off + 8:off + 8 + ln]
        elif typ == b"IEND":
            break
        off += 12 + ln
    return zlib.decompress(bytes(idat))


def _decode_alpha_fraction(path: Path) -> float:
    """Fraction of pixels with alpha>20, after a full RGBA unfilter."""
    data, w, h, _, _ = _png_header(path)
    raw = _idat_raw(data)
    stride = w * 4
    prev = bytearray(stride)
    opaque = 0
    pos = 0
    for _y in range(h):
        f = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride
        if f == 1:
            for i in range(4, stride):
                line[i] = (line[i] + line[i - 4]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i - 4] if i >= 4 else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - 4] if i >= 4 else 0
                b = prev[i]
                c = prev[i - 4] if i >= 4 else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        for i in range(3, stride, 4):
            if line[i] > 20:
                opaque += 1
        prev = line
    return opaque / float(w * h)


ALL_PIECE_FILES = [
    f"{arm}_{layer}_{facing}.png"
    for arm in PIECE_ARMS
    for layer in PIECE_LAYERS
    for facing in PIECE_FACINGS
]


def test_pieces_dir_has_all_24_sprites():
    assert PIECES_DIR.is_dir(), f"missing war-table pieces dir {PIECES_DIR}"
    for name in ALL_PIECE_FILES:
        assert (PIECES_DIR / name).exists(), f"missing piece sprite {name}"
    # exactly the canonical set (guards stray/renamed files)
    on_disk = {p.name for p in PIECES_DIR.glob("*.png")}
    assert on_disk == set(ALL_PIECE_FILES), (
        f"pieces dir contents drifted: extra={on_disk - set(ALL_PIECE_FILES)}, "
        f"missing={set(ALL_PIECE_FILES) - on_disk}"
    )


@pytest.mark.parametrize("name", ALL_PIECE_FILES)
def test_piece_sprite_is_256_rgba_and_not_truncated(name):
    path = PIECES_DIR / name
    data, w, h, bit_depth, color_type = _png_header(path)
    assert (w, h) == (256, 256), f"{name} is {w}x{h}, expected 256x256"
    assert bit_depth == 8, f"{name} bit depth {bit_depth}, expected 8"
    assert color_type == 6, f"{name} color type {color_type}, expected 6 (RGBA)"
    raw = _idat_raw(data)
    assert len(raw) == h * (w * 4 + 1), f"{name} IDAT decodes to a truncated image"
    assert any(b != 0 for b in raw), f"{name} is fully blank/transparent"


@pytest.mark.parametrize("arm", PIECE_ARMS)
def test_piece_body_and_coat_are_real_cutouts(arm):
    """The figure (body) is a cutout with detail; the coat mask has a tintable
    mass. Both must be neither blank nor a full opaque rectangle."""
    body_frac = _decode_alpha_fraction(PIECES_DIR / f"{arm}_body_r.png")
    coat_frac = _decode_alpha_fraction(PIECES_DIR / f"{arm}_coat_r.png")
    assert 0.02 < body_frac < 0.85, (
        f"{arm}_body_r alpha coverage {body_frac:.3f} out of range — blank or solid?"
    )
    # cavalry/artillery carry a single rider/gunner coat (~0.5%); infantry ~4%.
    # Floor guards a blank mask; ceiling guards a full-frame fill.
    assert 0.003 < coat_frac < 0.60, (
        f"{arm}_coat_r coat-mask coverage {coat_frac:.3f} out of range — the "
        f"faction tint would have no (or a full-frame) target"
    )


# ═══════════════════════════════════════════════════════════════════════════
# War-Table Pieces — CODE (Session U5, spec §8 U5)
#
# The "each active marshal renders a piece keyed to its dominant arm" behaviour
# needs a live Godot tree, which pytest cannot boot; the engine boot-smoke
# (0 SCRIPT ERROR) is the manual runtime gate. These are STATIC source
# assertions — the same .gd-as-text approach the UI-1/2/3 tests use — pinning
# that the placement layer, arm keying, faction tint, and tween/facing wiring
# are present and can't silently regress.
# ═══════════════════════════════════════════════════════════════════════════

SCENES_DIR = GODOT_PROJ / "scenes"
WAR_PIECE_GD = SCENES_DIR / "war_table_piece.gd"
MAP_RENDERER_GD = SCENES_DIR / "map_renderer_base.gd"


def test_war_table_piece_script_shape():
    assert WAR_PIECE_GD.exists(), f"missing {WAR_PIECE_GD}"
    src = _read(WAR_PIECE_GD)
    assert "class_name WarTablePiece" in src, "piece must register a global class_name"
    # loads its sprites from the pieces dir, both facings, layered composite.
    assert 'PIECES_DIR := "res://assets/ui/pieces/"' in src
    assert '"shadow", "base", "coat", "body"' in src, "layer compositing order"
    # only the coat is faction-tinted (shadow/base/body stay neutral pewter).
    assert re.search(r"func set_faction", src), "faction tint entry point"
    assert re.search(r'_sprites\.get\("coat"', src), "faction tint targets the coat only"
    # facing flip + move tween present (the U5 motion behaviours).
    assert "func set_facing" in src and "func move_to" in src
    assert "create_tween" in src, "move_to must tween province->province"


def test_map_renderer_wires_war_table_pieces():
    assert MAP_RENDERER_GD.exists(), f"missing {MAP_RENDERER_GD}"
    src = _read(MAP_RENDERER_GD)
    # a persistent, y-sorted piece layer distinct from the torn-down force layer.
    assert "pieces_layer" in src
    assert "y_sort_enabled = true" in src, "pieces must y-sort by depth"
    assert "WarTablePiece.pieces_available()" in src, "gate on assets present"
    # dominant-arm keying from the mutually-exclusive tactical_state flags.
    assert "func _marshal_arm" in src
    assert re.search(r'ts\.get\("cavalry"', src) and re.search(r'ts\.get\("artillery"', src), (
        "arm keys off tactical_state cavalry/artillery, else infantry"
    )
    assert 'return "infantry"' in src
    # the diff updater is invoked from BOTH refresh paths.
    assert src.count("_update_war_table_pieces()") >= 3, (
        "_update_war_table_pieces must be defined and called from update_all_regions "
        "and update_region"
    )
    # faction tint sourced from the centralized palette (never inline).
    assert "Utils.COLOR_ENEMY_DEFAULT" in src


def test_war_table_pieces_only_in_bitmap_mode():
    """The legacy circle fixture keeps its square icons — pieces are gated to
    the commissioned bitmap map so the fixture's visuals/tests are untouched."""
    src = _read(MAP_RENDERER_GD)
    # the pieces_layer creation is guarded by _bitmap_mode.
    assert re.search(
        r"if _bitmap_mode and WarTablePiece\.pieces_available\(\):", src
    ), "pieces_layer must be created only in bitmap mode with assets present"
