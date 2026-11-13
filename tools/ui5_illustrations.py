"""UI-5 illustrations: turn sourced public-domain paintings into banner + plate crops.

Reads ``provenance_img.json`` (a JSON list of entries, or an object with an
``images`` list) plus the originals from a staging folder, and writes for each key

    <key>_banner.jpg   1200x400  (3:1)
    <key>_plate.jpg    1280x720  (16:9)

into ``godot-client/project-sovereign/assets/ui/illustrations/``.

Every image gets the same treatment so the set reads as one: a warm grade toward
parchment, saturation x0.92, a slight contrast lift, a soft elliptical vignette
(edges ~22 % darker), JPEG q88 progressive sRGB with metadata stripped.

Usage (Pillow + stdlib only; run with -I):
    .venv/Scripts/python.exe -I tools/ui5_illustrations.py <staging_dir> [key ...]

``<staging_dir>`` holds ``provenance_img.json`` and an ``originals/`` folder (or is
the ``originals/`` folder itself, with the JSON one level up). Re-runnable: outputs
are overwritten deterministically.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "godot-client" / "project-sovereign" / "assets" / "ui" / "illustrations"

BANNER = (1200, 400)
PLATE = (1280, 720)
QUALITY = 88

TINT = (1.04, 1.0, 0.92)
SATURATION = 0.92
CONTRAST = 1.06
VIGNETTE_EDGE = 0.22  # fraction darkened at the extreme corners/edges

# key -> (fx, fy) in 0..1: where the subject sits in the original (centre of the crop).
FOCUS: dict[str, tuple[float, float]] = {
    "council": (0.50, 0.50),
    "court": (0.38, 0.45),
    "coronation": (0.52, 0.50),
    "treaty": (0.55, 0.55),
    "tilsit": (0.45, 0.55),
    "congress": (0.50, 0.50),
    "study": (0.50, 0.10),
    "talleyrand": (0.50, 0.28),
    "courier": (0.55, 0.22),
    "moniteur": (0.55, 0.55),
    "ceremony": (0.42, 0.50),
    "te_deum": (0.50, 0.50),
    "treasury": (0.50, 0.60),
    "fleet": (0.50, 0.50),
    "rising": (0.50, 0.50),
    "repression": (0.45, 0.55),
    "disasters": (0.50, 0.50),
    "retreat": (0.50, 0.50),
    "fontainebleau": (0.50, 0.28),
    "arcole": (0.50, 0.25),
    "horatii": (0.42, 0.55),
    "pius_vii": (0.50, 0.22),
    "santo_domingo": (0.50, 0.50),
    "camp": (0.50, 0.55),
    "horses": (0.45, 0.45),
    "convoy": (0.50, 0.55),
    "berlin": (0.42, 0.50),
    "ulm": (0.45, 0.50),
    "borodino": (0.50, 0.50),
    "somosierra": (0.50, 0.50),
    "aboukir": (0.50, 0.45),
    "copenhagen": (0.50, 0.50),
    "marengo": (0.50, 0.50),
    "wedding": (0.50, 0.50),
    "holland": (0.50, 0.22),
    "reich": (0.50, 0.27),
}


def load_entries(staging: Path) -> list[dict]:
    prov = staging / "provenance_img.json"
    if not prov.exists():
        prov = staging.parent / "provenance_img.json"
    data = json.loads(prov.read_text(encoding="utf-8"))
    return data["images"] if isinstance(data, dict) else data


def originals_dir(staging: Path) -> Path:
    return staging / "originals" if (staging / "originals").is_dir() else staging


def crop_to(img: Image.Image, size: tuple[int, int], focus: tuple[float, float]) -> Image.Image:
    """Cover-crop ``img`` to ``size`` with the crop window centred on ``focus``."""
    tw, th = size
    w, h = img.size
    scale = max(tw / w, th / h)
    cw, ch = tw / scale, th / scale  # crop window in source pixels
    cx = min(max(focus[0] * w, cw / 2), w - cw / 2)
    cy = min(max(focus[1] * h, ch / 2), h - ch / 2)
    box = (round(cx - cw / 2), round(cy - ch / 2), round(cx + cw / 2), round(cy + ch / 2))
    return img.resize(size, Image.LANCZOS, box=box)


def vignette_mask(size: tuple[int, int]) -> Image.Image:
    """L-mode mask: 255 in the middle, falling to (1 - VIGNETTE_EDGE) * 255 at the edge midpoints."""
    w, h = size
    # Build small and upscale: the falloff is smooth, so this is exact enough and fast.
    sw, sh = 160, max(1, round(160 * h / w))
    mask = Image.new("L", (sw, sh))
    px = mask.load()
    for y in range(sh):
        ny = (y + 0.5) / sh * 2 - 1
        for x in range(sw):
            nx = (x + 0.5) / sw * 2 - 1
            d = (nx * nx + ny * ny) ** 0.5 / 1.4142  # 0 centre .. 1 corner
            t = max(0.0, (d - 0.35) / 0.65)  # clear inner ellipse, ramp to the corner
            px[x, y] = round(255 * (1 - VIGNETTE_EDGE * t * t * (3 - 2 * t)))
    return mask.resize(size, Image.BICUBIC)


def grade(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    r, g, b = img.split()
    r = r.point(lambda v: min(255, round(v * TINT[0])))
    g = g.point(lambda v: min(255, round(v * TINT[1])))
    b = b.point(lambda v: min(255, round(v * TINT[2])))
    img = Image.merge("RGB", (r, g, b))
    img = ImageEnhance.Color(img).enhance(SATURATION)
    img = ImageEnhance.Contrast(img).enhance(CONTRAST)
    mask = vignette_mask(img.size)
    dark = Image.new("RGB", img.size, (0, 0, 0))
    # multiply by mask/255: blend toward black by (1 - mask)
    return Image.composite(img, dark, mask)


def save(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = Image.new("RGB", img.size)
    clean.paste(img)  # fresh image: no EXIF/ICC/info carried over
    clean.save(path, "JPEG", quality=QUALITY, progressive=True, optimize=True, subsampling=2)


def process(entry: dict, odir: Path) -> list[str]:
    key = entry["key"]
    src = odir / entry["file"]
    focus = FOCUS.get(key, (0.5, 0.5))
    lines = []
    with Image.open(src) as im:
        im.load()
        # ICC profiles other than sRGB are ignored: period scans are tagged sRGB or untagged.
        for suffix, size in (("banner", BANNER), ("plate", PLATE)):
            out = OUT_DIR / f"{key}_{suffix}.jpg"
            save(grade(crop_to(im, size, focus)), out)
            lines.append(f"{key:14s} {suffix:6s} {size[0]}x{size[1]} focus=({focus[0]:.2f},{focus[1]:.2f}) src={entry['file']} -> {out.name}")
    return lines


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    staging = Path(argv[0])
    wanted = set(argv[1:])
    odir = originals_dir(staging)
    missing = 0
    for entry in load_entries(staging):
        if wanted and entry["key"] not in wanted:
            continue
        if not (odir / entry["file"]).exists():
            print(f"{entry['key']:14s} MISSING {entry['file']}")
            missing += 1
            continue
        for line in process(entry, odir):
            print(line)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
