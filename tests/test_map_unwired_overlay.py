"""Behavioral fixture tests for Map Readiness §4.4 unwired province overlay.

The renderer's `_apply_unwired_grey_overlay()` runs inside Godot, so these
tests don't execute the GDScript directly. Instead we mirror the overlay
formula in Python (a straight Color.lerp toward UNWIRED_GREY_COLOR by
UNWIRED_GREY_BLEND) against fixture pixel data, so CI catches regressions
in the intent of the overlay: wired pixels must be untouched, unwired
pixels must blend toward the configured grey, and the sentinel "no
province" color must always be ignored.

The constants mirror the GDScript definitions at the top of
`map_renderer_base.gd` — if those change, update these fixtures too.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map_renderer_base.gd"


# Mirror of UNWIRED_GREY_COLOR / UNWIRED_GREY_BLEND in the renderer.
UNWIRED_GREY_RGB = (int(round(0.32 * 255)), int(round(0.32 * 255)), int(round(0.34 * 255)))
UNWIRED_GREY_BLEND = 0.7

# Self-contained synthetic lookup fixture (Slice 9: the session8 placeholder
# registry these tests used to sample colors from is retired). The overlay
# formula only needs distinct province lookup colors plus the sentinel — it
# never depended on any real registry, so these are deliberately NOT drawn
# from europe.json.
WIRED_LOOKUP_RGB = (179, 68, 55)  # stands in for a wired province
UNWIRED_LOOKUP_RGB = (198, 97, 34)  # stands in for an unwired province
SENTINEL_RGB = (0, 0, 0)  # the "no province" background sentinel


def _color_key(rgb: tuple[int, int, int]) -> str:
    return f"{rgb[0]},{rgb[1]},{rgb[2]}"


def _lerp(a: int, b: int, t: float) -> int:
    return int(round(a + (b - a) * t))


def _lerp_rgb(
    base: tuple[int, int, int], target: tuple[int, int, int], t: float
) -> tuple[int, int, int]:
    return (_lerp(base[0], target[0], t), _lerp(base[1], target[1], t), _lerp(base[2], target[2], t))


def _apply_overlay(
    visual: list[list[tuple[int, int, int]]],
    lookup: list[list[tuple[int, int, int]]],
    unwired_keys: set[str],
) -> list[list[tuple[int, int, int]]]:
    """Python mirror of the renderer's `_apply_unwired_grey_overlay`.

    Pixels whose lookup color belongs to an unwired province are lerped
    toward UNWIRED_GREY_RGB by UNWIRED_GREY_BLEND. All other pixels —
    including the sentinel "no province" color — pass through unchanged.
    """
    height = len(visual)
    width = len(visual[0])
    out = [row[:] for row in visual]
    for y in range(height):
        for x in range(width):
            key = _color_key(lookup[y][x])
            if key not in unwired_keys:
                continue
            out[y][x] = _lerp_rgb(visual[y][x], UNWIRED_GREY_RGB, UNWIRED_GREY_BLEND)
    return out


def _apply_overlay_rgba(
    visual: list[list[tuple[int, int, int, int]]],
    lookup: list[list[tuple[int, int, int]]],
    unwired_keys: set[str],
) -> list[list[tuple[int, int, int, int]]]:
    """RGBA mirror of `_apply_unwired_grey_overlay`.

    The renderer computes `base.lerp(UNWIRED_GREY_COLOR, UNWIRED_GREY_BLEND)`
    and then explicitly restores `tinted.a = base.a`, so alpha is pinned to
    the source pixel. This mirror replicates that contract exactly: RGB
    channels lerp toward UNWIRED_GREY_RGB, alpha comes from the source.
    """
    height = len(visual)
    width = len(visual[0])
    out = [row[:] for row in visual]
    for y in range(height):
        for x in range(width):
            key = _color_key(lookup[y][x])
            if key not in unwired_keys:
                continue
            base_rgb = visual[y][x][:3]
            base_alpha = visual[y][x][3]
            tinted_rgb = _lerp_rgb(base_rgb, UNWIRED_GREY_RGB, UNWIRED_GREY_BLEND)
            out[y][x] = (tinted_rgb[0], tinted_rgb[1], tinted_rgb[2], base_alpha)
    return out


def test_overlay_constants_match_renderer_source():
    """Pin the renderer constants so the Python mirror stays in sync."""
    source = BASE_GD.read_text(encoding="utf-8")
    assert "const UNWIRED_GREY_COLOR := Color(0.32, 0.32, 0.34, 1.0)" in source
    assert "const UNWIRED_GREY_BLEND: float = 0.7" in source


def test_all_wired_overlay_is_a_no_op():
    """When the registry has zero unwired regions, overlay is a no-op.

    With an empty unwired set the overlay helper returns early and the
    final texture is visually identical to the pre-overlay visual image.
    """
    visual = [
        [(200, 150, 100), (50, 80, 200)],
        [(120, 120, 120), (255, 255, 255)],
    ]
    lookup = [
        [WIRED_LOOKUP_RGB, UNWIRED_LOOKUP_RGB],
        [WIRED_LOOKUP_RGB, UNWIRED_LOOKUP_RGB],
    ]
    result = _apply_overlay(visual, lookup, unwired_keys=set())
    assert result == visual


def test_overlay_blends_only_unwired_pixels_toward_grey():
    """The overlay must touch ONLY pixels belonging to unwired provinces."""
    unwired_keys = {_color_key(UNWIRED_LOOKUP_RGB)}

    visual = [
        [(200, 150, 100), (50, 80, 200), (10, 10, 10)],
        [(120, 120, 120), (0, 0, 0), (255, 255, 255)],
    ]
    lookup = [
        [WIRED_LOOKUP_RGB, UNWIRED_LOOKUP_RGB, SENTINEL_RGB],
        [WIRED_LOOKUP_RGB, UNWIRED_LOOKUP_RGB, SENTINEL_RGB],
    ]
    result = _apply_overlay(visual, lookup, unwired_keys)

    # Wired-province + sentinel pixels untouched.
    assert result[0][0] == (200, 150, 100)
    assert result[1][0] == (120, 120, 120)
    assert result[0][2] == (10, 10, 10)
    assert result[1][2] == (255, 255, 255)

    # Unwired-province pixels blended toward UNWIRED_GREY_RGB by UNWIRED_GREY_BLEND.
    expected_top = _lerp_rgb((50, 80, 200), UNWIRED_GREY_RGB, UNWIRED_GREY_BLEND)
    expected_bottom = _lerp_rgb((0, 0, 0), UNWIRED_GREY_RGB, UNWIRED_GREY_BLEND)
    assert result[0][1] == expected_top
    assert result[1][1] == expected_bottom


def test_overlay_drives_pure_tint_toward_grey_color():
    """Feeding a pure-grey visual through the overlay snaps toward the
    configured UNWIRED_GREY_RGB, proving the lerp target is correct.
    """
    unwired_keys = {_color_key(UNWIRED_LOOKUP_RGB)}

    # Base pixel: pure black. Lerp(black, grey, 0.7) = 0.7 * grey.
    visual = [[(0, 0, 0)]]
    lookup = [[UNWIRED_LOOKUP_RGB]]
    result = _apply_overlay(visual, lookup, unwired_keys)

    expected = (
        _lerp(0, UNWIRED_GREY_RGB[0], UNWIRED_GREY_BLEND),
        _lerp(0, UNWIRED_GREY_RGB[1], UNWIRED_GREY_BLEND),
        _lerp(0, UNWIRED_GREY_RGB[2], UNWIRED_GREY_BLEND),
    )
    assert result[0][0] == expected


def test_overlay_ignores_sentinel_pixels_even_if_visually_flagged():
    """The sentinel "no province" color must never be treated as unwired —
    that color signals background, not a province.
    """
    # If someone erroneously listed the sentinel as unwired, the overlay
    # SHOULD still treat it as a province-less background pixel. The
    # renderer's _unwired_lookup_keys() only emits keys drawn from
    # province_color_lookup, which never contains the sentinel, so this
    # test documents the guarantee.
    unwired_keys = set()  # sentinel MUST NOT appear here in the real flow

    visual = [[(77, 77, 77)]]
    lookup = [[SENTINEL_RGB]]
    result = _apply_overlay(visual, lookup, unwired_keys)
    assert result == visual


def test_renderer_source_unwired_lookup_keys_excludes_sentinel_by_construction():
    """The Python mirror's safety hinges on `_unwired_lookup_keys()` never
    emitting the sentinel key. We verify by construction: the helper only
    iterates `province_color_lookup` entries, and `_build_province_shapes()`
    never inserts the sentinel color into that dict.
    """
    source = BASE_GD.read_text(encoding="utf-8")
    # The helper iterates the registry-keyed lookup, not raw pixel data.
    func_start = source.index("func _unwired_lookup_keys()")
    func_body = source[func_start : source.index("\nfunc ", func_start + 1)]
    assert "for color_key in province_color_lookup.keys():" in func_body
    assert "NO_PROVINCE_COLOR" not in func_body  # no sentinel path reaches here
    # And the shape builder never maps the sentinel to a region name.
    shape_start = source.index("func _build_province_shapes():")
    shape_body = source[shape_start : source.index("\nfunc ", shape_start + 1)]
    assert "province_color_lookup[_color_to_key(lookup_color)] = region_name" in shape_body
    assert "province_color_lookup[_color_to_key(NO_PROVINCE_COLOR)]" not in shape_body


def test_overlay_preserves_alpha_channel_under_rgba_mirror():
    """§4.4 audit 2026-04-19: the renderer restores `tinted.a = base.a` after
    lerping so partially transparent commissioned-art pixels don't drift to
    opaque (or leak toward UNWIRED_GREY_COLOR's alpha = 1.0). The RGBA mirror
    pins that contract end-to-end: partial, zero, and full alpha inputs all
    survive the overlay unchanged on their alpha channel.
    """
    unwired_keys = {_color_key(UNWIRED_LOOKUP_RGB)}

    # Three pixels spanning the alpha range: fully transparent, half, fully
    # opaque. All three sit on an unwired province, so all three WILL be
    # touched by the overlay — but only on RGB. Alpha must be identical.
    visual_rgba = [[(200, 150, 100, 0), (50, 80, 200, 128), (10, 10, 10, 255)]]
    lookup = [[UNWIRED_LOOKUP_RGB, UNWIRED_LOOKUP_RGB, UNWIRED_LOOKUP_RGB]]

    result = _apply_overlay_rgba(visual_rgba, lookup, unwired_keys)

    assert result[0][0][3] == 0, "fully transparent pixel must stay transparent"
    assert result[0][1][3] == 128, "half-alpha pixel must keep alpha=128"
    assert result[0][2][3] == 255, "fully opaque pixel must stay opaque"

    # Sanity: RGB channels DID change (overlay fired), so we know the test
    # is actually exercising the blend path, not short-circuiting.
    for x in range(3):
        base_rgb = visual_rgba[0][x][:3]
        expected_rgb = _lerp_rgb(base_rgb, UNWIRED_GREY_RGB, UNWIRED_GREY_BLEND)
        assert result[0][x][:3] == expected_rgb


def test_renderer_source_explicitly_restores_alpha_after_lerp():
    """§4.4 audit 2026-04-19: the overlay body must contain the explicit
    `tinted.a = base.a` line. Without it, Color.lerp would drift alpha toward
    UNWIRED_GREY_COLOR's alpha=1.0 and partially transparent commissioned-art
    pixels would lose their transparency. This source-level assertion binds
    the RGBA mirror above to the runtime implementation.
    """
    source = BASE_GD.read_text(encoding="utf-8")
    func_start = source.index("func _apply_unwired_grey_overlay(")
    func_body = source[func_start : source.index("\nfunc ", func_start + 1)]
    assert "var tinted = base.lerp(UNWIRED_GREY_COLOR, UNWIRED_GREY_BLEND)" in func_body
    # The critical alpha-restoration line the audit flagged: if a future edit
    # removes it, this test fails even though the RGB-only mirror tests stay
    # green on their own.
    assert "tinted.a = base.a" in func_body
    # Order matters — alpha restoration must happen AFTER the lerp, BEFORE
    # set_pixel; otherwise the blended alpha lands in the image.
    lerp_idx = func_body.index("var tinted = base.lerp(")
    restore_idx = func_body.index("tinted.a = base.a")
    set_idx = func_body.index("visual_image.set_pixel(")
    assert lerp_idx < restore_idx < set_idx
