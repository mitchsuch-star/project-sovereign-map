"""Stat-bar textures (UI) — 11 inline graphical bars (values 0..10) for the
marshal character sheet's skill / glory rows, built from the CC0 Kenney RPG
UI-expansion bar slices already in assets/ui/bars/.

Each bar_<v>.png is a recessed frame (bar_frame) with a GRAYSCALE glossy fill
spanning v/10 of the width. The fill is grayscale so the Godot RichTextLabel
can tint it per value via [img color=#hex] (peak green / weak red / etc.) while
keeping the gloss; the dark frame takes the same subtle tint (a faint coloured
track). Display size is baked in (W x H) so [img width=W height=H] is 1:1.

OFFLINE dev tool — NOT run by CI or the game. Regenerate after tuning:
    .venv/Scripts/python.exe tools/gen_stat_bars.py
Requires Pillow (dev-only; not in requirements.txt).
"""
from __future__ import annotations

import os

from PIL import Image

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(_REPO, "godot-client", "project-sovereign", "assets", "ui", "bars")

W, H = 110, 14      # baked display size (matches the ~14px skill-row font)
CAP = 9             # source 3-slice cap width (px)
STEPS = 10          # value granularity 0..10


def _grayscale(img: Image.Image) -> Image.Image:
    """Luminance in RGB (keeps the gloss), alpha preserved — so [img color]
    modulation colours it cleanly."""
    px = img.load()
    out = img.copy()
    o = out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            lum = (r * 299 + g * 587 + b * 114) // 1000
            o[x, y] = (lum, lum, lum, a)
    return out


def nine(src: Image.Image, width: int, height: int) -> Image.Image:
    """3-slice horizontal assembly: native caps + stretched middle."""
    left = src.crop((0, 0, CAP, src.height)).resize((CAP, height), Image.BILINEAR)
    right = src.crop((src.width - CAP, 0, src.width, src.height)).resize((CAP, height), Image.BILINEAR)
    midw = max(1, width - 2 * CAP)
    mid = src.crop((CAP, 0, src.width - CAP, src.height)).resize((midw, height), Image.BILINEAR)
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    out.alpha_composite(left, (0, 0))
    out.alpha_composite(mid, (CAP, 0))
    out.alpha_composite(right, (width - CAP, 0))
    return out


def build():
    frame_src = Image.open(os.path.join(BARS, "bar_frame.png")).convert("RGBA")
    fill_src = _grayscale(Image.open(os.path.join(BARS, "bar_fill_gold.png")).convert("RGBA"))
    n = 0
    for v in range(STEPS + 1):
        bar = nine(frame_src, W, H)                      # recessed track
        if v > 0:
            fill_w = max(2 * CAP, round(v / STEPS * W))   # >= both caps so the pill reads
            fill_w = min(fill_w, W)
            bar.alpha_composite(nine(fill_src, fill_w, H), (0, 0))
        bar.save(os.path.join(BARS, f"bar_{v}.png"))
        n += 1
    print(f"wrote {n} stat bars ({W}x{H}) -> {BARS}")


if __name__ == "__main__":
    build()
