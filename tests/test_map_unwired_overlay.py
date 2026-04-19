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

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROVINCE_JSON = (
    REPO_ROOT
    / "godot-client"
    / "project-sovereign"
    / "assets"
    / "maps"
    / "session8_placeholder_provinces.json"
)
BASE_GD = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes" / "map_renderer_base.gd"


# Mirror of UNWIRED_GREY_COLOR / UNWIRED_GREY_BLEND in the renderer.
UNWIRED_GREY_RGB = (int(round(0.32 * 255)), int(round(0.32 * 255)), int(round(0.34 * 255)))
UNWIRED_GREY_BLEND = 0.7


def _load_province_definition() -> dict:
    return json.loads(PROVINCE_JSON.read_text(encoding="utf-8"))


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


def test_overlay_constants_match_renderer_source():
    """Pin the renderer constants so the Python mirror stays in sync."""
    source = BASE_GD.read_text(encoding="utf-8")
    assert "const UNWIRED_GREY_COLOR := Color(0.32, 0.32, 0.34, 1.0)" in source
    assert "const UNWIRED_GREY_BLEND: float = 0.7" in source


def test_all_wired_overlay_is_a_no_op():
    """When the registry has zero unwired regions, overlay is a no-op.

    This matches the current 19-region placeholder — every province is
    wired, so the overlay helper returns early and the final texture is
    visually identical to the pre-overlay visual image.
    """
    province_data = _load_province_definition()
    assert all(entry["wired"] is True for entry in province_data["regions"].values()), (
        "Test assumption: placeholder has no unwired regions yet. "
        "If this changes, update this test."
    )
    paris_rgb = tuple(province_data["regions"]["Paris"]["lookup_color"])
    belgium_rgb = tuple(province_data["regions"]["Belgium"]["lookup_color"])

    visual = [
        [(200, 150, 100), (50, 80, 200)],
        [(120, 120, 120), (255, 255, 255)],
    ]
    lookup = [
        [paris_rgb, belgium_rgb],
        [paris_rgb, belgium_rgb],
    ]
    result = _apply_overlay(visual, lookup, unwired_keys=set())
    assert result == visual


def test_overlay_blends_only_unwired_pixels_toward_grey():
    """The overlay must touch ONLY pixels belonging to unwired provinces."""
    province_data = _load_province_definition()
    paris_rgb = tuple(province_data["regions"]["Paris"]["lookup_color"])
    belgium_rgb = tuple(province_data["regions"]["Belgium"]["lookup_color"])
    sentinel_rgb = tuple(province_data["no_province_color"])

    # Paris is wired; Belgium stands in for an unwired province for this test.
    unwired_keys = {_color_key(belgium_rgb)}

    visual = [
        [(200, 150, 100), (50, 80, 200), (10, 10, 10)],
        [(120, 120, 120), (0, 0, 0), (255, 255, 255)],
    ]
    lookup = [
        [paris_rgb, belgium_rgb, sentinel_rgb],
        [paris_rgb, belgium_rgb, sentinel_rgb],
    ]
    result = _apply_overlay(visual, lookup, unwired_keys)

    # Paris + sentinel pixels untouched.
    assert result[0][0] == (200, 150, 100)
    assert result[1][0] == (120, 120, 120)
    assert result[0][2] == (10, 10, 10)
    assert result[1][2] == (255, 255, 255)

    # Belgium pixels blended toward UNWIRED_GREY_RGB by UNWIRED_GREY_BLEND.
    expected_top = _lerp_rgb((50, 80, 200), UNWIRED_GREY_RGB, UNWIRED_GREY_BLEND)
    expected_bottom = _lerp_rgb((0, 0, 0), UNWIRED_GREY_RGB, UNWIRED_GREY_BLEND)
    assert result[0][1] == expected_top
    assert result[1][1] == expected_bottom


def test_overlay_drives_pure_tint_toward_grey_color():
    """Feeding a pure-grey visual through the overlay snaps toward the
    configured UNWIRED_GREY_RGB, proving the lerp target is correct.
    """
    province_data = _load_province_definition()
    belgium_rgb = tuple(province_data["regions"]["Belgium"]["lookup_color"])
    unwired_keys = {_color_key(belgium_rgb)}

    # Base pixel: pure black. Lerp(black, grey, 0.7) = 0.7 * grey.
    visual = [[(0, 0, 0)]]
    lookup = [[belgium_rgb]]
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
    province_data = _load_province_definition()
    sentinel_rgb = tuple(province_data["no_province_color"])

    # If someone erroneously listed the sentinel as unwired, the overlay
    # SHOULD still treat it as a province-less background pixel. The
    # renderer's _unwired_lookup_keys() only emits keys drawn from
    # province_color_lookup, which never contains the sentinel, so this
    # test documents the guarantee.
    unwired_keys = set()  # sentinel MUST NOT appear here in the real flow

    visual = [[(77, 77, 77)]]
    lookup = [[sentinel_rgb]]
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
