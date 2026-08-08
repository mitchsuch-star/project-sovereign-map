"""Ink & Iron application icon (Main Menu pass, position 6).

A crossed QUILL and SABRE — ink and iron — in the game's gold, inside a double
gold ring on navy leather. 100% ORIGINAL procedural art (no third-party pixels),
the gen_war_table_pieces.py pipeline: draw at SS supersample, LANCZOS downscale.

OFFLINE dev tool — NOT run by CI or the game. Requires Pillow + numpy (dev-only):
    .venv/Scripts/python.exe tools/gen_app_icon.py
Writes godot-client/project-sovereign/icon.png (256x256, window/taskbar icon).
"""
from __future__ import annotations

import math
import os

import numpy as np
from PIL import Image, ImageDraw

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(_REPO, "godot-client", "project-sovereign", "icon.png")

FRAME = 256
SS = 4
W = FRAME * SS
C = W // 2

NAVY_EDGE = (10, 14, 26)
NAVY_CORE = (24, 33, 58)
GOLD = (217, 191, 140, 255)
GOLD_DK = (138, 115, 64, 255)
BLADE = (232, 211, 164, 255)
VANE = (239, 227, 196, 255)
OUTLINE = (96, 76, 36, 255)


def radial_navy() -> Image.Image:
    """Navy leather disc-glow: dark edges, softly lit centre."""
    yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
    d = np.sqrt((xx - C) ** 2 + (yy - C * 0.92) ** 2) / (W * 0.62)
    d = np.clip(d, 0.0, 1.0) ** 1.4
    img = np.zeros((W, W, 3), dtype=np.float32)
    for ch in range(3):
        img[..., ch] = NAVY_CORE[ch] * (1 - d) + NAVY_EDGE[ch] * d
    return Image.fromarray(img.astype(np.uint8), "RGB").convert("RGBA")


def bezier(p0, p1, p2, n=120):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


def ribbon(pts, w_start, w_end, power=1.0):
    """Polygon band around a polyline with linearly tapering half-width."""
    left, right = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        hw = (w_start * (1 - t ** power) + w_end * t ** power) / 2.0
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        else:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        left.append((x + nx * hw, y + ny * hw))
        right.append((x - nx * hw, y - ny * hw))
    return left + right[::-1]


def ribbon_asym(pts, w_left, w_right):
    """Band with different half-widths per side (a feather's vane sits mostly
    on one side of its shaft). Width profile: nothing at the shaft end, fullest
    around two-thirds of the way up, rounding back to a point at the plume tip."""
    left, right = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        k = math.sin(min(1.0, t * 1.08) * math.pi) ** 0.65
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        else:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        left.append((x + nx * (w_left * k + 4), y + ny * (w_left * k + 4)))
        right.append((x - nx * (w_right * k + 4), y - ny * (w_right * k + 4)))
    return left + right[::-1]


def draw_sabre(dr: ImageDraw.ImageDraw):
    """Lower-left grip to upper-right tip; a light cavalry-sabre bow."""
    p0, p1, p2 = (330, 770), (570, 500), (770, 235)
    line = bezier(p0, p1, p2)
    blade = ribbon(line, 92, 10)
    dr.polygon(blade, fill=BLADE, outline=OUTLINE, width=7)
    # fuller (blood groove) — a darker channel along the blade
    groove = ribbon(line[8:-10], 26, 6)
    dr.polygon(groove, fill=(198, 172, 120, 255))
    # crossguard: a bar perpendicular to the grip direction
    gx, gy = p0
    dx, dy = line[6][0] - gx, line[6][1] - gy
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln, dx / ln
    g = 105
    dr.line([(gx - nx * g, gy - ny * g), (gx + nx * g, gy + ny * g)],
            fill=GOLD, width=38)
    # grip + pommel, angled away from the blade
    hx, hy = gx - dx / ln * 128, gy - dy / ln * 128
    dr.line([(gx, gy), (hx, hy)], fill=GOLD_DK, width=44)
    r = 34
    dr.ellipse([hx - r, hy - r, hx + r, hy + r], fill=GOLD, outline=OUTLINE, width=6)


def draw_quill(dr: ImageDraw.ImageDraw, base: Image.Image):
    """Lower-right nib to upper-left plume, crossing over the sabre."""
    p0, p1, p2 = (712, 780), (452, 508), (272, 232)
    line = bezier(p0, p1, p2)
    # the vane: a soft feather mass, fuller on the outer side of the shaft,
    # from a third of the way up to a rounded point at the plume tip
    vane_pts = line[36:]
    vane = ribbon_asym(vane_pts, 112, 54)
    dr.polygon(vane, fill=VANE, outline=OUTLINE, width=7)
    # three gentle notches on the trailing (outer) edge — enough to read
    # "feather" at 32px without turning the vane into a ladder
    nmax = len(vane_pts)
    for frac in (0.42, 0.62, 0.80):
        i = int(nmax * frac)
        x, y = vane_pts[i]
        dx, dy = vane_pts[i + 3][0] - x, vane_pts[i + 3][1] - y
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        k = math.sin(min(1.0, frac * 1.08) * math.pi) ** 0.65
        edge = (x + nx * (112 * k + 4), y + ny * (112 * k + 4))
        back = (x + dx / ln * -52 + nx * (112 * k * 0.45), y + dy / ln * -52 + ny * (112 * k * 0.45))
        dr.polygon([edge, back, (x + nx * (112 * k * 0.55), y + ny * (112 * k * 0.55))],
                   fill=NAVY_EDGE + (255,))
    # shaft up the middle of the vane + bare quill down to the nib
    dr.line([tuple(map(int, p)) for p in line[32:]], fill=GOLD_DK, width=15)
    dr.line([tuple(map(int, p)) for p in line[:38]], fill=GOLD, width=24)
    # nib: an angled point with a slit
    nx0, ny0 = line[0]
    dirx, diry = nx0 - line[5][0], ny0 - line[5][1]
    ln = math.hypot(dirx, diry) or 1.0
    dirx, diry = dirx / ln, diry / ln
    px, py = -diry, dirx
    tip = (nx0 + dirx * 62, ny0 + diry * 62)
    dr.polygon([(nx0 + px * 26, ny0 + py * 26),
                (nx0 - px * 26, ny0 - py * 26), tip],
               fill=GOLD, outline=OUTLINE, width=6)
    dr.line([((nx0 + tip[0]) / 2, (ny0 + tip[1]) / 2), tip], fill=OUTLINE, width=7)


def main() -> None:
    img = radial_navy()
    dr = ImageDraw.Draw(img)
    # double gold ring
    m1 = 26 * SS / 4
    dr.ellipse([m1, m1, W - m1, W - m1], outline=GOLD, width=int(20 * SS / 4))
    m2 = 62 * SS / 4
    dr.ellipse([m2, m2, W - m2, W - m2], outline=GOLD_DK, width=int(6 * SS / 4))
    draw_sabre(dr)
    draw_quill(dr, img)
    out = img.resize((FRAME, FRAME), Image.LANCZOS)
    out.save(DEST)
    print(f"wrote {DEST} ({FRAME}x{FRAME})")


if __name__ == "__main__":
    main()
