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

# Marshals with no confident PD portrait — unillustrated by design (spec §2),
# rendered with the gold-monogram fallback. Abdurrahman + the ARTILLERY_GAP_SPEC
# gunners (bench artillery candidates, no curated PD likeness sourced yet).
PORTRAIT_EXEMPT = {
    "Abdurrahman",
    "Senarmont", "Smola", "Kutaisov", "Holtzendorff", "Shrapnel",
}
PORTRAIT_EXTS = (".jpg", ".png", ".jpeg", ".webp")

# ── War-Table Pieces (UI-4, spec §7) ────────────────────────────────────────
PIECES_DIR = GODOT_PROJ / "assets" / "ui" / "pieces"
# NV-7 adds "ship" — the fourth carved piece, from the same generator, for
# the naval diorama. It is DIORAMA-only (NAVAL_SPEC Q1(a) keeps the naval
# model to one national fleet record, so nothing on the map is a ship), but
# it is a war-table piece and every quality check below applies to it.
# NP-5 adds "emperor" — the sovereign's own piece (bicorne, redingote, the
# faction grand cordon + base rim), keyed off the map summary's
# is_sovereign-first arm derivation. Pin flipped consciously 32→40 sprites.
PIECE_ARMS = ("infantry", "cavalry", "artillery", "ship", "emperor")
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


def test_every_shipped_art_asset_is_TRACKED_not_merely_on_disk():
    """NP-V (adversarial review P3-4, CONFIRMED): `assets/` is gitignored,
    so an asset generated into it is invisible to git unless force-added.
    Row NP shipped `Napoleon.jpg` and eight `emperor_*.png` that existed
    on the developer's disk, passed every on-disk test in this file, and
    were in NO commit — on a fresh clone (and in the position-10 build)
    the Emperor would have had no portrait and no map piece, the two most
    visible "he is different" cues.

    On-disk assertions cannot catch this by construction. This one asks
    git.
    """
    import subprocess
    repo = Path(__file__).resolve().parents[1]
    tracked = set(subprocess.run(
        ["git", "ls-files", "godot-client/project-sovereign/assets/ui/pieces",
         "godot-client/project-sovereign/assets/portraits"],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.split())

    missing = []
    for name in ALL_PIECE_FILES:
        rel = f"godot-client/project-sovereign/assets/ui/pieces/{name}"
        if rel not in tracked:
            missing.append(rel)
        # Godot needs the .import sibling or the texture will not load in
        # an exported build.
        if f"{rel}.import" not in tracked:
            missing.append(f"{rel}.import")

    assert not missing, (
        "art assets exist on disk but are NOT in git (assets/ is "
        f"gitignored — force-add them): {missing}")


def test_pieces_dir_has_the_whole_canonical_set():
    # (24 at U4; 32 since NV-7 added the ship; 40 since NP-5's emperor.)
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


# ── Map label serif faces (Task 1, July 16, 2026) ───────────────────────────
# The map previously drew ALL labels with ThemeDB.fallback_font (Open Sans, a
# plain sans). It now uses two distinct on-disk serifs: nations in Marcellus SC
# (small caps), provinces/cities in Spectral. Both are already OFL-credited.
MAP_LABEL_GD = SCENES_DIR / "map_label_layer.gd"
MAP_LABEL_NATION_TTF = FONTS_DIR / "MarcellusSC-Regular.ttf"
MAP_LABEL_PROVINCE_TTF = FONTS_DIR / "Spectral-Regular.ttf"


def test_map_label_font_assets_present():
    """Both label faces (and their committed .import sidecars) ship on disk."""
    for ttf in (MAP_LABEL_NATION_TTF, MAP_LABEL_PROVINCE_TTF):
        assert ttf.exists(), f"missing map-label font {ttf}"
        assert ttf.with_suffix(".ttf.import").exists(), (
            f"missing committed Godot .import sidecar for {ttf.name} "
            "(load() would fail on a fresh checkout)"
        )


def test_map_labels_use_distinct_nonfallback_serifs():
    """The two tiers draw with the loaded serif faces, NOT ThemeDB.fallback_font.

    Guards the whole point of the change: a regression that reverts _draw_label_tier
    to the fallback font, or collapses the two tiers to one face, fails here.
    """
    assert MAP_LABEL_GD.exists(), f"missing {MAP_LABEL_GD}"
    src = _read(MAP_LABEL_GD)
    # Both face paths are referenced and loaded into per-tier fields.
    assert 'res://assets/fonts/MarcellusSC-Regular.ttf' in src, "nation face path"
    assert 'res://assets/fonts/Spectral-Regular.ttf' in src, "province face path"
    assert "_load_label_font(" in src, "faces load through the guarded helper"
    # The province tier draws with province_font and the nation tier with
    # nation_font — the distinct-hierarchy contract.
    assert re.search(r"_draw_label_tier\(\s*province_font,", src), (
        "province tier must draw with the province face"
    )
    assert re.search(r"_draw_label_tier\(\s*nation_font,", src), (
        "nation tier must draw with the nation face"
    )
    # The fallback face survives ONLY as the graceful-degradation path inside
    # _load_label_font / the _draw() null-guard — never as the primary draw font.
    # (i.e. no bare `var font: Font = ThemeDB.fallback_font` feeding both tiers.)
    assert not re.search(
        r"_draw_label_tier\(\s*font,", src
    ), "neither tier may draw with the shared fallback `font` var (pre-Task-1 shape)"


# ═══════════════════════════════════════════════════════════════════════════
# July 18, 2026 playtest sweep — viewport overflow
#
# REPORTED: "the dplo window is too big for the screen when in settle a war."
#
# Confirmed and generalised. Every modal is a centre-anchored PanelContainer
# with fixed offsets and grow_horizontal/vertical = 2. Because PanelContainer
# is a Container, its size floor is get_combined_minimum_size() — so when the
# custom_minimum_size chain (or an unbounded fit_content RichTextLabel) exceeds
# the authored box, the panel grows SYMMETRICALLY and spills off both edges,
# carrying the action buttons out of reach. Interface Scale amplifies it: the
# logical viewport is physical/scale, and the slider runs to 2.0.
#
# Two things are therefore required together, and each is pinned below:
#   (1) BOUND the content, so the panel's minimum can actually shrink.
#   (2) CLAMP to the live viewport (Utils.clamp_centered_panel).
# The clamp alone is inert — Godot clamps size UP to the combined minimum.
# ═══════════════════════════════════════════════════════════════════════════

UTILS_GD = GODOT_PROJ / "scripts" / "utils.gd"


def _scene(name: str) -> str:
    path = SCENES_DIR / f"{name}.tscn"
    assert path.exists(), f"missing scene {path}"
    return _read(path)


def _script(name: str) -> str:
    path = GODOT_PROJ / "scripts" / f"{name}.gd"
    assert path.exists(), f"missing script {path}"
    return _read(path)


def _node_block(src: str, node_name: str) -> str:
    """The property block of a single [node name="X" ...] declaration."""
    match = re.search(
        r'^\[node name="%s"[^\]]*\]\n(.*?)(?=^\[node |\Z)' % re.escape(node_name),
        src, re.M | re.S)
    assert match, f"node {node_name!r} not found"
    return match.group(1)


def test_settlement_footer_is_bounded():
    """The reported window. FooterLabel was fit_content=true / scroll_active=
    false with no minimum, as a DIRECT VBox child outside any ScrollContainer —
    the single unbounded contributor to the settlement popup's height."""
    block = _node_block(_scene("proposal_confirm_popup"), "FooterLabel")
    assert "fit_content = true" not in block, (
        "FooterLabel must not size itself to its content — that is the "
        "unbounded growth vector that pushed the buttons off-screen")
    assert "scroll_active = true" in block, "it needs its own scrollbar instead"
    assert "custom_minimum_size" in block, "it needs a real height budget"


def test_settlement_tier2_buttons_have_their_own_bounded_rail():
    """Per-court affordances are uncapped (one button per court per action), so
    they must not share the primary rail — Submit / Back Out has to stay put."""
    src = _scene("proposal_confirm_popup")
    tier2 = _node_block(src, "Tier2Scroll")
    assert "custom_minimum_size" in tier2, "the tier-2 rail must be bounded"
    assert 'name="Tier2ButtonContainer"' in src
    gd = _script("proposal_confirm_popup")
    assert "tier2_button_container.add_child(btn)" in gd, (
        "tier-2 affordances must mount in the scrolled container, not the "
        "primary rail")
    # The primary rail must stay OUTSIDE any scroll region.
    assert re.search(
        r'\[node name="ButtonContainer" type="GridContainer" '
        r'parent="PanelContainer/VBoxContainer"\]', src), (
        "the primary button rail must remain a direct VBox child so it is "
        "always visible")
    # Both rails must be cleared, or last turn's buttons stack on this turn's.
    clear = gd[gd.index("func _clear_buttons"):]
    assert "tier2_button_container" in clear[:400]


def test_settlement_popup_has_an_escape_hatch():
    """main.gd's ESC ladder refuses to act while a modal is open, so an
    off-screen button row was an unrecoverable soft-lock."""
    gd = _script("proposal_confirm_popup")
    assert "_unhandled_input" in gd
    assert "ui_cancel" in gd
    # It must be OPTION-DERIVED: `dismiss` is a proposal-family action with no
    # settlement arm, so hard-coding it would desync the backend dialogue.
    assert "_find_safe_exit_action" in gd
    body = gd.split("func _unhandled_input")[1].split("func _find_safe_exit_action")[0]
    assert '"dismiss"' not in body, "the escape action must be derived, not literal"


def _panel_anchor(scene_src: str):
    """(anchor_left, anchor_right) of the root PanelContainer, or None."""
    try:
        block = _node_block(scene_src, "PanelContainer")
    except AssertionError:
        return None
    left = re.search(r"^anchor_left = ([\d.]+)", block, re.M)
    right = re.search(r"^anchor_right = ([\d.]+)", block, re.M)
    if not left or not right:
        return None
    return float(left.group(1)), float(right.group(1))


def _centre_anchored_surfaces():
    """Derived, not hand-maintained. A hand-written list silently under-covers:
    the first version named 12 of the 22 scripts the sweep actually touched, so
    a refactor could drop the clamp from any of the other 10 unnoticed."""
    out = []
    for scene in sorted(SCENES_DIR.glob("*.tscn")):
        anchors = _panel_anchor(_read(scene))
        if anchors == (0.5, 0.5) and (
                GODOT_PROJ / "scripts" / f"{scene.stem}.gd").exists():
            out.append(scene.stem)
    return out


def test_the_derived_clamp_set_is_not_silently_empty():
    surfaces = _centre_anchored_surfaces()
    assert len(surfaces) >= 25, (
        f"only {len(surfaces)} centre-anchored surfaces found — the derivation "
        f"has probably drifted and is under-covering: {surfaces}")


@pytest.mark.parametrize("script_name", _centre_anchored_surfaces())
def test_centre_anchored_surfaces_clamp_to_the_viewport(script_name):
    """EVERY centre-anchored PanelContainer surface must consult the live
    viewport on open — the modals this sweep touched AND the five layer-50
    ledger screens that already did. Before the sweep the helper existed in
    utils.gd but reached only those five; none of the ~20 modals called it."""
    assert "Utils.clamp_centered_panel($PanelContainer)" in _script(script_name), (
        f"{script_name}.gd never clamps; at Interface Scale 2.0 the logical "
        f"viewport halves and its action row can leave the screen")


def test_edge_anchored_panels_are_deliberately_excluded():
    """The paired negative. clamp_centered_panel writes SYMMETRIC offsets about
    the midpoint, so applying it to an edge-anchored panel would teleport it to
    mid-screen. These two must stay out — and the helper guards them
    structurally rather than trusting each caller to remember."""
    for name in ("war_detail_popup", "war_status_panel"):
        anchors = _panel_anchor(_scene(name))
        assert anchors is not None and anchors != (0.5, 0.5), (
            f"{name} is expected to be edge-anchored; if it became "
            f"centre-anchored it must join the clamped set")
    body = _utils_func_body("clamp_centered_panel")
    # Pin the guard's SHAPE, not just that the words appear: a mutation to
    # `if false and (...)` left every earlier version of this test green while
    # the guard no longer fired.
    guard = re.search(
        r"if not \(is_equal_approx\(panel\.anchor_left,\s*0\.5\)\s*\n"
        r"\s*and is_equal_approx\(panel\.anchor_right,\s*0\.5\)\):\s*\n"
        r"\s*return\b",
        body)
    assert guard, (
        "clamp_centered_panel must guard BOTH anchors and RETURN — guarding "
        "on anchor_left alone misses a half-centre-anchored panel, and a "
        "guard that does not return protects nothing")
    cache_at = body.find('has_meta("design_size")')
    assert cache_at != -1
    assert guard.start() < cache_at, (
        "the anchor guard must RETURN before the design_size cache is written, "
        "or an edge-anchored panel gets a bogus cached rect")


def test_clamp_runs_after_show_so_layout_has_settled():
    for name in ("proposal_confirm_popup", "reward_dialog", "diplomacy_wizard"):
        gd = _script(name)
        show_at = gd.index("\tshow()\n")
        clamp_at = gd.index("Utils.clamp_centered_panel")
        assert clamp_at > show_at, f"{name}: clamp must follow show()"


def _utils_func_body(name: str) -> str:
    """The source of one static func in utils.gd, up to the next top-level
    `static func`. Scoping assertions to a body is what stops them being
    satisfied by an unrelated occurrence elsewhere in the file."""
    src = _read(UTILS_GD)
    start = src.index(f"static func {name}")
    rest = src[start + 10:]
    end = rest.find("\nstatic func ")
    return src[start:] if end == -1 else src[start:start + 10 + end]


def test_clamp_helper_relaxes_child_minimums():
    """The load-bearing half. Rewriting offsets alone is INERT: Godot clamps a
    Container's size UP to get_combined_minimum_size(), so a panel whose
    children declare fixed minimums ignores the clamped offsets entirely.

    Pins the WIRING, not the vocabulary. The first version of this test asserted
    only that the string "_relax_child_minimums" appeared somewhere in the file
    — which stayed true when the pass was orphaned as dead code. The
    pre-commit review proved that by mutation: deleting the call site left all
    three clamp tests green.
    """
    body = _utils_func_body("clamp_centered_panel")
    assert re.search(r"_relax_child_minimums\(\s*panel\s*,", body), (
        "the second pass must be CALLED from clamp_centered_panel; rewriting "
        "offsets alone is inert")
    relax = _utils_func_body("_relax_child_minimums")
    assert "authored_min_y" in relax, (
        "authored minimums must be cached so they stay the CEILING and "
        "viewports that already fit are byte-unchanged")
    assert "get_combined_minimum_size" in relax, (
        "the pass must measure the real combined minimum, not guess")


def test_relax_pass_restores_before_measuring():
    """The one-way-ratchet fix. Measuring against the ALREADY-SHRUNK minimums
    left by a previous open meant the pass could only ever shrink: open the
    settlement popup once at Interface Scale 2.0 and the per-court table stayed
    pinned near the floor for the rest of the session, on a full-size screen."""
    relax = _utils_func_body("_relax_child_minimums")
    restore_at = relax.find('custom_minimum_size.y = float(control.get_meta("authored_min_y"))')
    # The CALL, not the docstring's mention of the concept.
    measure_at = relax.find("panel.get_combined_minimum_size()")
    assert restore_at != -1, "the pass must restore authored minimums"
    assert measure_at != -1, "the pass must measure the real combined minimum"
    assert restore_at < measure_at, (
        "restore must happen BEFORE the excess is measured, or the pass is a "
        "one-way ratchet that never grows content back")


def test_relax_pass_iterates_instead_of_under_delivering():
    """A single proportional pass systematically stops short: a share handed to
    a control whose real minimum is text-derived buys no actual reduction."""
    relax = _utils_func_body("_relax_child_minimums")
    assert "for _round in range(_RELAX_ROUNDS)" in relax, (
        "the pass must re-measure and redistribute, not distribute once")
    # A literal `range(1)` would satisfy the loop text while restoring the very
    # single-pass behavior this guards against, so pin the bound itself.
    rounds = re.search(r"const _RELAX_ROUNDS\s*:=\s*(\d+)", _read(UTILS_GD))
    assert rounds and int(rounds.group(1)) >= 2, (
        "one round systematically under-delivers — a share handed to a control "
        "whose real minimum is text-derived buys no reduction")
    # The excess must be re-read INSIDE the loop, not hoisted above it.
    loop_body = relax[relax.index("for _round in range(_RELAX_ROUNDS)"):]
    assert "panel.get_combined_minimum_size()" in loop_body, (
        "each round must re-measure; a hoisted measurement is a single pass "
        "wearing a loop")


def test_relax_cache_follows_a_caller_that_re_derives_its_floor():
    """proposal_confirm_popup re-derives PerCourtScroll's floor from the live
    viewport on EVERY open. A write-once cache would let a later relax clobber
    that fresh value with a stale, smaller one, silently undoing the
    scene-level half of the fix."""
    collect = _utils_func_body("_collect_flexible")
    assert "relaxed_min_y" in collect, (
        "the pass must be able to tell its OWN output apart from a value the "
        "caller re-derived")
    relax = _utils_func_body("_relax_child_minimums")
    assert 'set_meta("relaxed_min_y"' in relax
    # And the caller must actually still re-derive it.
    assert "per_court_scroll.custom_minimum_size.y = minf(" in _script(
        "proposal_confirm_popup")




def test_clamp_helper_never_shrinks_a_click_target():
    """Buttons declare their minimum as a click target; shrinking those to make
    room is the opposite of the goal."""
    src = _read(UTILS_GD)
    assert "is Button" in src


def test_proclamation_body_is_scrollable_and_the_button_is_pinned():
    """A blocking modal whose single [Acknowledge] can leave the screen is
    unrecoverable — the worst case in the sweep."""
    src = _scene("proclamation_popup")
    assert 'name="ContentScroll" type="ScrollContainer"' in src
    assert 'parent="PanelContainer/VBoxContainer/ContentScroll"' in src, (
        "the variable-length body must live inside the scroll")
    assert 'name="ButtonContainer" type="HBoxContainer" ' \
           'parent="PanelContainer/VBoxContainer"' in src, (
        "[Acknowledge] must stay OUTSIDE the scroll so it is always reachable")
    panel = _node_block(src, "PanelContainer")
    assert "offset_bottom" in panel, (
        "the panel needs an authored design rect for the clamp to capture")
    assert "custom_minimum_size = Vector2(680, 0)" not in panel, (
        "a 680px hard width floor defeats the clamp horizontally")
    # The script must follow the re-parent.
    assert "ContentScroll/ContentLabel" in _script("proclamation_popup")


def test_reward_dialog_explainer_is_bounded():
    block = _node_block(_scene("reward_dialog"), "InfoLabel")
    assert "fit_content = false" in block
    assert "scroll_active = true" in block


def test_war_detail_button_row_wraps_instead_of_growing_left():
    """One ~130px Target button per coalition member; an HBox's minimum width
    is the SUM of its children, and this panel is right-anchored with
    grow_horizontal = 0, so it grew LEFT off the viewport."""
    src = _scene("war_detail_popup")
    assert '[node name="ButtonRow" type="HFlowContainer"' in src, (
        "must be an HFlowContainer so the minimum is the widest single child")
    block = _node_block(src, "ButtonRow")
    assert "h_separation" in block and "v_separation" in block, (
        "HFlowContainer uses h/v separation, not the HBox `separation` key")
    assert "alignment = 1" in block, "centring must be preserved"


@pytest.mark.parametrize("name", ["enemy_phase_dialog", "strategic_report_popup"])
def test_report_dialogs_are_dismissable_without_a_mouse(name):
    """Both are registered modal=true, and main.gd's ESC ladder refuses to act
    while a modal is open — so before this there was no non-mouse way out and a
    clipped [Continue] cost the player the turn."""
    gd = _script(name)
    assert "_unhandled_input" in gd
    assert "ui_accept" in gd and "ui_cancel" in gd
    # Route through the existing handler so hide()+dismissed stays single-source.
    handler = gd[gd.index("func _unhandled_input"):]
    assert "_on_continue_pressed()" in handler[:700]


def test_diplomacy_wizard_fixed_chain_fits_its_authored_box():
    """The wizard's own minimum chain (150 + 260 + header + separators + button
    row + margins) exceeded its authored 520px box before any content."""
    src = _scene("diplomacy_wizard")
    assessment = _node_block(src, "AssessmentPanel")
    scroll = _node_block(src, "ScrollContainer")
    both = assessment + scroll
    fixed = [int(m) for m in re.findall(
        r"custom_minimum_size = Vector2\(0, (\d+)\)", both)]
    assert fixed, "expected authored height floors"
    assert sum(fixed) <= 200, (
        f"fixed floors sum to {sum(fixed)}px; they must stay small enough that "
        f"the panel fits the clamp's worst case (a halved logical viewport)")
    assert "size_flags_vertical = 3" in assessment, (
        "the assessment panel must expand to fill available height instead of "
        "reserving it")


def test_both_wizard_open_paths_clamp():
    """The wizard is reachable from F1 AND from the war-panel handoff."""
    assert _script("diplomacy_wizard").count(
        "Utils.clamp_centered_panel($PanelContainer)") == 2
