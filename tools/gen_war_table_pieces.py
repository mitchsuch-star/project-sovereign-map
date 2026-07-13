"""War-Table Pieces (UI-4) — tin-flat-on-round-base generator.

Renders infantry / cavalry / artillery as engraved-relief Zinnfigur "flats"
standing in a round base disc, per docs/UI_VISUAL_FOUNDATION_SPEC.md §7.
100% ORIGINAL procedural art — no third-party pixels are used or derived (the
tin-flat aesthetic is only *informed* by the §7 public reference photos).

OFFLINE dev tool — NOT run by CI or the game. Regenerate the sprites after any
tuning here. Requires Pillow + numpy (dev-only; not in requirements.txt):
    .venv/Scripts/python.exe -m pip install Pillow numpy

Usage:
    python tools/gen_war_table_pieces.py            # export 24 sprites -> assets/ui/pieces/
    python tools/gen_war_table_pieces.py export DIR # export into DIR
    python tools/gen_war_table_pieces.py qa DIR      # write a QA contact sheet into DIR

Pipeline (2D — flats don't need real 3D):
  * draw at SS x supersample, downscale LANCZOS for antialiasing
  * broadside (dead side profile), nose-right; L facing = horizontal mirror
  * baked relief pass: rim light on lit edges + core shadow + dark contour, so
    the flat reads as engraved pewter (§7 "engraved-line rim")
  * layers per arm/facing (bottom->top): base (ochre disc) / shadow (line) /
    coat (the faction tint-mask — coat mass + colour on light-gray so Godot
    `modulate` multiplies it to the nation hue) / body (neutral metal+flesh+
    gear + the baked relief). Metal/base stay neutral so "tin" survives any hue.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIECES_DEST = os.path.join(
    _REPO, "godot-client", "project-sovereign", "assets", "ui", "pieces")
OUT = os.environ.get("PIECES_QA_OUT", os.path.join(os.path.dirname(__file__), "_qa"))

FRAME = 256          # exported px per side
SS = 4               # supersample
W = FRAME * SS
GY = 210 * SS        # ground line (base-disc centre y)
CX = 128 * SS        # frame centre x

# ── palette (neutral "tin" channels; coat is faction-tinted elsewhere) ──────
STEEL       = (196, 202, 210, 255)
STEEL_DK    = (86, 92, 102, 255)
BRONZE      = (176, 138, 84, 255)
BRONZE_DK   = (120, 92, 52, 255)
WOOD        = (120, 86, 50, 255)
WOOD_DK     = (78, 54, 30, 255)
BLACK_GEAR  = (44, 44, 52, 255)
BLACK_HI    = (92, 92, 104, 255)
FLESH       = (216, 170, 128, 255)
FLESH_DK    = (168, 120, 84, 255)
BREECH      = (222, 216, 200, 255)   # white breeches -> warm off-white
BREECH_DK   = (170, 162, 142, 255)
HORSE       = (122, 96, 68, 255)     # bay
HORSE_DK    = (78, 58, 40, 255)
HORSE_MANE  = (54, 40, 28, 255)
SLATE       = (86, 98, 116, 255)     # body-layer coat fallback
SLATE_DK    = (54, 64, 80, 255)
RIM         = (245, 240, 228, 235)   # bright pewter rim light

# coat mask (multiplied by nation colour): near-white base, darker grooves
COAT_HI     = (244, 244, 244, 255)
COAT_MID    = (214, 214, 214, 255)
COAT_LO     = (168, 168, 168, 255)

BASE_TOP    = (188, 150, 92, 255)    # ochre ground, lit top face
BASE_MID    = (150, 116, 66, 255)
BASE_RIM    = (104, 78, 42, 255)
BASE_HI     = (222, 196, 146, 235)

SHADOW_COL  = (18, 14, 10)


# ── geometry helpers ────────────────────────────────────────────────────────
def catmull(pts, samples=16, closed=True):
    """Smooth a control polyline into a dense point list (Catmull-Rom)."""
    p = list(pts)
    if closed:
        p = [p[-1]] + p + [p[0], p[1]]
    else:
        p = [p[0]] + p + [p[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for t in range(samples):
            s = t / samples
            s2, s3 = s * s, s * s * s
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * s +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * s2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * s3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * s +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * s2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * s3)
            out.append((x, y))
    return out


def new_layer():
    return Image.new("RGBA", (W, W), (0, 0, 0, 0))


def smooth_fill(layer, pts, color, tension_samples=16):
    ImageDraw.Draw(layer).polygon(catmull(pts, tension_samples), fill=color)


def hard_fill(layer, pts, color):
    ImageDraw.Draw(layer).polygon([(x, y) for x, y in pts], fill=color)


def stroke(layer, pts, color, width, closed=False, smooth=False):
    d = ImageDraw.Draw(layer)
    p = catmull(pts) if smooth else [(x, y) for x, y in pts]
    if closed:
        p = p + [p[0]]
    d.line(p, fill=color, width=int(width), joint="curve")
    r = width / 2
    for (x, y) in (p[0], p[-1]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)


def disc(layer, cx, cy, rx, ry, color):
    ImageDraw.Draw(layer).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color)


def line(layer, a, b, color, width):
    d = ImageDraw.Draw(layer)
    d.line([a, b], fill=color, width=int(width))
    r = width / 2
    for (x, y) in (a, b):
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)


# ── shared pieces: base disc + contact shadow ───────────────────────────────
def make_base(width_frac):
    """Round base disc, slight top-down so the ellipse reads as a footprint."""
    lay = new_layer()
    rx = width_frac * W * 0.5
    ry = rx * 0.34
    cy = GY
    disc(lay, CX, cy + 3 * SS, rx, ry, BASE_RIM)          # thickness / drop shadow
    disc(lay, CX, cy, rx, ry, BASE_MID)                    # side
    disc(lay, CX, cy - 2 * SS, rx * 0.96, ry * 0.9, BASE_TOP)   # lit top face
    # upper-rim highlight arc
    ImageDraw.Draw(lay).arc(
        [CX - rx * 0.96, cy - 2 * SS - ry * 0.9, CX + rx * 0.96, cy - 2 * SS + ry * 0.9],
        200, 340, fill=BASE_HI, width=int(2.5 * SS))
    return lay


def make_shadow(width_frac):
    """Narrow line-shaped contact shadow hugging the feet, feathered to rim."""
    lay = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    rx = width_frac * W * 0.5 * 0.82
    ry = rx * 0.20
    d = ImageDraw.Draw(lay)
    d.ellipse([CX - rx, GY - ry - 2 * SS, CX + rx, GY + ry - 2 * SS],
              fill=SHADOW_COL + (150,))
    d.ellipse([CX - rx * 0.6, GY - ry * 0.7 - 2 * SS, CX + rx * 0.6, GY + ry * 0.7 - 2 * SS],
              fill=SHADOW_COL + (210,))
    return lay.filter(ImageFilter.GaussianBlur(6 * SS))


# ── coat helper: paint the same silhouette into body(slate) + coat(mask) ─────
def paint_coat(body, coat, pts, groove=None):
    """Paint the coat mass into the coat mask only (faction-tinted downstream).

    The body layer is left transparent here so the tinted coat shows through;
    the relief pass bakes the coat's lit/shaded EDGE lines into the body on top.
    """
    smooth_fill(coat, pts, COAT_HI)
    dense = catmull(pts)
    ys = [p[1] for p in dense]
    ymid = (min(ys) + max(ys)) * 0.5
    lower = [p for p in dense if p[1] > ymid]          # bottom-half volume shade
    if len(lower) > 2:
        ImageDraw.Draw(coat).polygon(lower, fill=COAT_MID)
    if groove:
        for g in groove:
            stroke(coat, g, COAT_LO, 2.0 * SS, smooth=True)


# =============================================================================
#  INFANTRY  — rank of shako figures + a taller colour/eagle bearer
# =============================================================================
def foot_soldier(body, coat, cx, s=1.0, bearer=False):
    u = SS
    gy = GY
    # --- legs (marching stride, off-white breeches + black boots) ---
    # back leg (slightly trailing) — tight marching stance, not a wide straddle
    smooth_fill(body, [
        (cx - 2 * u * s, gy - 40 * u * s), (cx - 7 * u * s, gy - 22 * u * s),
        (cx - 8 * u * s, gy - 3 * u * s), (cx - 3 * u * s, gy - 2 * u * s),
        (cx - 1 * u * s, gy - 20 * u * s), (cx + 2 * u * s, gy - 34 * u * s),
    ], BREECH_DK)
    hard_fill(body, [(cx - 9 * u * s, gy - 5 * u * s), (cx - 9 * u * s, gy),
                     (cx - 1 * u * s, gy), (cx - 2 * u * s, gy - 5 * u * s)], BLACK_GEAR)
    # front leg (slightly forward)
    smooth_fill(body, [
        (cx + 3 * u * s, gy - 40 * u * s), (cx + 8 * u * s, gy - 24 * u * s),
        (cx + 9 * u * s, gy - 3 * u * s), (cx + 4 * u * s, gy - 2 * u * s),
        (cx + 2 * u * s, gy - 22 * u * s), (cx - 1 * u * s, gy - 34 * u * s),
    ], BREECH)
    hard_fill(body, [(cx + 3 * u * s, gy - 5 * u * s), (cx + 4 * u * s, gy),
                     (cx + 11 * u * s, gy), (cx + 10 * u * s, gy - 5 * u * s)], BLACK_GEAR)

    # --- coat (torso + tails) : the tintable mass ---
    coat_pts = [
        (cx - 6 * u * s, gy - 66 * u * s),   # back shoulder
        (cx + 8 * u * s, gy - 66 * u * s),   # front shoulder
        (cx + 10 * u * s, gy - 50 * u * s),  # chest
        (cx + 9 * u * s, gy - 40 * u * s),   # front hip
        (cx + 3 * u * s, gy - 36 * u * s),
        (cx - 7 * u * s, gy - 37 * u * s),   # tail bottom
        (cx - 12 * u * s, gy - 44 * u * s),  # coat-tail flare (back)
        (cx - 9 * u * s, gy - 58 * u * s),
    ]
    paint_coat(body, coat, coat_pts,
               groove=[[(cx + 2 * u * s, gy - 64 * u * s), (cx + 3 * u * s, gy - 40 * u * s)]])
    # cross-belt (white) over coat
    stroke(body, [(cx - 7 * u * s, gy - 64 * u * s), (cx + 9 * u * s, gy - 46 * u * s)],
           BREECH, 2.6 * u * s)

    # --- head: flesh + black shako with peak + plume ---
    disc(body, cx + 2 * u * s, gy - 71 * u * s, 6 * u * s, 6.5 * u * s, FLESH)   # face
    # shako (cylinder)
    hard_fill(body, [
        (cx - 4 * u * s, gy - 74 * u * s), (cx + 8 * u * s, gy - 74 * u * s),
        (cx + 8 * u * s, gy - 90 * u * s), (cx - 4 * u * s, gy - 90 * u * s),
    ], BLACK_GEAR)
    hard_fill(body, [(cx + 6 * u * s, gy - 76 * u * s), (cx + 12 * u * s, gy - 74 * u * s),
                     (cx + 12 * u * s, gy - 72 * u * s), (cx + 6 * u * s, gy - 73 * u * s)],
              BLACK_GEAR)  # peak
    disc(body, cx + 2 * u * s, gy - 90 * u * s, 5.5 * u * s, 2.2 * u * s, BLACK_HI)  # top band
    # plume
    stroke(body, [(cx + 2 * u * s, gy - 90 * u * s), (cx + 1 * u * s, gy - 102 * u * s)],
           BREECH, 3.4 * u * s)

    if bearer:
        # flagpole rising well above the rank + a colour (in coat mask -> faction)
        px = cx + 4 * u * s
        line(body, (px, gy - 52 * u * s), (px, gy - 128 * u * s), WOOD, 2.6 * u * s)
        disc(body, px, gy - 130 * u * s, 3 * u * s, 3 * u * s, BRONZE)  # eagle finial
        # the colour is part of the tint-mask -> becomes a faction-hued banner
        flag = [(px, gy - 126 * u * s), (px + 26 * u * s, gy - 122 * u * s),
                (px + 22 * u * s, gy - 112 * u * s), (px + 26 * u * s, gy - 104 * u * s),
                (px, gy - 108 * u * s)]
        smooth_fill(coat, flag, COAT_HI)
        stroke(coat, [(px + 5 * u * s, gy - 123 * u * s), (px + 5 * u * s, gy - 109 * u * s)],
               COAT_LO, 1.6 * u * s)
    else:
        # shouldered musket -> vertical barrel breaking the top line
        mx = cx + 9 * u * s
        line(body, (mx, gy - 44 * u * s), (mx + 2 * u * s, gy - 104 * u * s), WOOD_DK, 2.4 * u * s)
        line(body, (mx + 1 * u * s, gy - 90 * u * s), (mx + 2 * u * s, gy - 108 * u * s),
             STEEL, 2.0 * u * s)  # barrel/bayonet tip


def build_infantry():
    body, coat = new_layer(), new_layer()
    # back-to-front so overlaps read (painter's order)
    foot_soldier(body, coat, CX - 30 * SS, s=0.94)
    foot_soldier(body, coat, CX + 26 * SS, s=0.98)
    foot_soldier(body, coat, CX - 2 * SS, s=1.06, bearer=True)   # centre bearer, tallest
    return {"base": make_base(0.80), "shadow": make_shadow(0.80),
            "body": body, "coat": coat}


# =============================================================================
#  CAVALRY  — single horse + rider in side profile, sabre raised
# =============================================================================
def build_cavalry():
    body, coat = new_layer(), new_layer()
    u = SS
    gy = GY
    cx = CX
    # --- horse body (galloping, legs extended) ---
    horse = [
        (cx - 34 * u, gy - 44 * u),   # rump top
        (cx - 6 * u, gy - 52 * u),    # back
        (cx + 22 * u, gy - 50 * u),   # withers
        (cx + 40 * u, gy - 46 * u),   # neck base
        (cx + 30 * u, gy - 40 * u),   # chest
        (cx + 30 * u, gy - 26 * u),   # front upper leg
        (cx + 2 * u, gy - 34 * u),    # belly
        (cx - 30 * u, gy - 30 * u),   # flank
        (cx - 40 * u, gy - 40 * u),   # hindquarter
    ]
    smooth_fill(body, horse, HORSE)
    # lower belly shade
    ImageDraw.Draw(body).polygon(
        [(cx - 30 * u, gy - 30 * u), (cx + 30 * u, gy - 26 * u),
         (cx + 26 * u, gy - 20 * u), (cx - 28 * u, gy - 22 * u)], fill=HORSE_DK)
    # --- legs: front pair reaching forward, hind pair driving back ---
    for (hip, knee, hoof, wd) in [
        ((cx + 26 * u, gy - 30 * u), (cx + 36 * u, gy - 14 * u), (cx + 44 * u, gy - 1 * u), 7.0),  # fore-lead
        ((cx + 22 * u, gy - 30 * u), (cx + 20 * u, gy - 16 * u), (cx + 16 * u, gy - 1 * u), 6.2),  # fore-trail
        ((cx - 30 * u, gy - 34 * u), (cx - 40 * u, gy - 18 * u), (cx - 46 * u, gy - 1 * u), 7.0),  # hind-drive
        ((cx - 24 * u, gy - 34 * u), (cx - 18 * u, gy - 18 * u), (cx - 12 * u, gy - 1 * u), 6.2),  # hind-trail
    ]:
        stroke(body, [hip, knee, hoof], HORSE_DK, wd * u, smooth=True)
        disc(body, hoof[0], hoof[1], 3.0 * u, 2.6 * u, BLACK_GEAR)
    # --- neck + head reaching forward ---
    neck = [(cx + 34 * u, gy - 48 * u), (cx + 50 * u, gy - 56 * u),
            (cx + 60 * u, gy - 52 * u), (cx + 58 * u, gy - 42 * u),
            (cx + 46 * u, gy - 40 * u), (cx + 36 * u, gy - 40 * u)]
    smooth_fill(body, neck, HORSE)
    head = [(cx + 56 * u, gy - 56 * u), (cx + 68 * u, gy - 52 * u),
            (cx + 70 * u, gy - 44 * u), (cx + 62 * u, gy - 40 * u),
            (cx + 54 * u, gy - 44 * u)]
    smooth_fill(body, head, HORSE)
    # mane + tail
    stroke(body, [(cx + 30 * u, gy - 52 * u), (cx + 48 * u, gy - 58 * u), (cx + 58 * u, gy - 56 * u)],
           HORSE_MANE, 3.5 * u, smooth=True)
    smooth_fill(body, [(cx - 38 * u, gy - 46 * u), (cx - 50 * u, gy - 42 * u),
                       (cx - 58 * u, gy - 22 * u), (cx - 54 * u, gy - 12 * u),
                       (cx - 50 * u, gy - 24 * u), (cx - 44 * u, gy - 38 * u),
                       (cx - 36 * u, gy - 42 * u)], HORSE_MANE)  # streaming tail

    # --- rider ---
    rx = cx - 2 * u
    ry = gy - 52 * u
    # legs astride
    stroke(body, [(rx + 4 * u, ry + 2 * u), (rx + 12 * u, ry + 12 * u), (rx + 16 * u, ry + 22 * u)],
           SLATE_DK, 5 * u, smooth=True)
    # torso coat (tint)
    torso = [(rx - 8 * u, ry - 2 * u), (rx + 8 * u, ry - 2 * u),
             (rx + 10 * u, ry - 18 * u), (rx + 4 * u, ry - 24 * u),
             (rx - 6 * u, ry - 22 * u), (rx - 12 * u, ry - 12 * u)]
    paint_coat(body, coat, torso)
    stroke(body, [(rx - 8 * u, ry - 20 * u), (rx + 8 * u, ry - 6 * u)], BREECH, 2.4 * u)  # belt
    # head + helmet
    disc(body, rx + 4 * u, ry - 26 * u, 5 * u, 5.5 * u, FLESH)
    hard_fill(body, [(rx - 1 * u, ry - 28 * u), (rx + 9 * u, ry - 28 * u),
                     (rx + 9 * u, ry - 38 * u), (rx - 1 * u, ry - 38 * u)], BLACK_GEAR)
    stroke(body, [(rx + 4 * u, ry - 38 * u), (rx + 2 * u, ry - 48 * u)], BREECH, 3 * u)  # plume
    # near arm raised with sabre, clearing the helmet
    sh = (rx + 2 * u, ry - 16 * u)
    hand = (rx + 20 * u, ry - 40 * u)
    stroke(body, [sh, (rx + 14 * u, ry - 24 * u), hand], SLATE_DK, 4 * u, smooth=True)
    line(body, hand, (rx + 40 * u, ry - 74 * u), STEEL, 2.6 * u)     # sabre blade
    disc(body, hand[0], hand[1], 2.4 * u, 2.4 * u, BRONZE)          # hilt
    return {"base": make_base(0.58), "shadow": make_shadow(0.62),
            "body": body, "coat": coat}


# =============================================================================
#  ARTILLERY — broadside gun (big spoked wheel + barrel + trail) + crew
# =============================================================================
def build_artillery():
    body, coat = new_layer(), new_layer()
    u = SS
    gy = GY
    cx = CX
    # --- trail (tail beam to the left, with ground spike) ---
    smooth_fill(body, [
        (cx - 2 * u, gy - 32 * u), (cx - 50 * u, gy - 11 * u),
        (cx - 60 * u, gy - 4 * u), (cx - 58 * u, gy + 1 * u),
        (cx - 48 * u, gy - 3 * u), (cx - 2 * u, gy - 23 * u),
    ], WOOD)
    # --- carriage cheek ---
    smooth_fill(body, [
        (cx - 6 * u, gy - 40 * u), (cx + 20 * u, gy - 34 * u),
        (cx + 22 * u, gy - 20 * u), (cx - 2 * u, gy - 22 * u),
    ], WOOD_DK)
    # --- barrel: tapering, pointing up-right over the wheel ---
    barrel = [
        (cx - 2 * u, gy - 34 * u), (cx + 40 * u, gy - 54 * u),   # muzzle top
        (cx + 44 * u, gy - 48 * u), (cx + 6 * u, gy - 26 * u),   # muzzle bottom
    ]
    smooth_fill(body, barrel, BRONZE)
    stroke(body, [(cx - 2 * u, gy - 32 * u), (cx + 42 * u, gy - 51 * u)], BRONZE_DK, 1.8 * u)
    disc(body, cx + 42 * u, gy - 51 * u, 4 * u, 4 * u, BRONZE_DK)   # muzzle mouth
    disc(body, cx + 42 * u, gy - 51 * u, 2.2 * u, 2.2 * u, (30, 24, 18, 255))
    disc(body, cx - 2 * u, gy - 30 * u, 5 * u, 5 * u, BRONZE)       # cascabel/breech

    # --- big spoked wheel ---
    wx, wy, wr = cx + 6 * u, gy - 14 * u, 24 * u
    disc(body, wx, wy, wr, wr, WOOD_DK)                 # felloe (rim)
    disc(body, wx, wy, wr - 3.5 * u, wr - 3.5 * u, (150, 112, 66, 255))  # inner
    for k in range(10):                                 # spokes
        a = math.pi * k / 10
        x2, y2 = wx + (wr - 4 * u) * math.cos(a), wy + (wr - 4 * u) * math.sin(a)
        x1, y1 = wx - (wr - 4 * u) * math.cos(a), wy - (wr - 4 * u) * math.sin(a)
        line(body, (x1, y1), (x2, y2), WOOD, 2.2 * u)
    disc(body, wx, wy, 5 * u, 5 * u, STEEL_DK)          # hub
    disc(body, wx, wy, 2.4 * u, 2.4 * u, (204, 200, 190, 255))  # neutral steel cap

    # --- crew: an upright gunner behind the trail, ramrod raised to the muzzle ---
    def gunner(gx):
        smooth_fill(body, [(gx - 4 * u, gy - 30 * u), (gx - 7 * u, gy - 3 * u),
                           (gx - 2 * u, gy - 2 * u), (gx, gy - 28 * u)], BREECH_DK)  # back leg
        hard_fill(body, [(gx - 8 * u, gy - 4 * u), (gx - 8 * u, gy), (gx - 1 * u, gy),
                         (gx - 1 * u, gy - 4 * u)], BLACK_GEAR)
        smooth_fill(body, [(gx + 2 * u, gy - 30 * u), (gx + 6 * u, gy - 4 * u),
                           (gx + 9 * u, gy - 3 * u), (gx + 5 * u, gy - 28 * u)], BREECH)  # front leg
        hard_fill(body, [(gx + 4 * u, gy - 4 * u), (gx + 4 * u, gy), (gx + 11 * u, gy),
                         (gx + 11 * u, gy - 4 * u)], BLACK_GEAR)
        torso = [(gx - 5 * u, gy - 50 * u), (gx + 6 * u, gy - 48 * u),
                 (gx + 6 * u, gy - 30 * u), (gx - 5 * u, gy - 31 * u)]
        paint_coat(body, coat, torso)
        disc(body, gx + 1 * u, gy - 54 * u, 5 * u, 5.5 * u, FLESH)               # face
        hard_fill(body, [(gx - 4 * u, gy - 55 * u), (gx + 6 * u, gy - 55 * u),
                         (gx + 6 * u, gy - 66 * u), (gx - 4 * u, gy - 66 * u)], BLACK_GEAR)  # shako
        # ramrod raised toward the muzzle (up-right, in-plane against the gun)
        stroke(body, [(gx + 5 * u, gy - 42 * u), (gx + 34 * u, gy - 60 * u)], WOOD, 2.2 * u)
        disc(body, gx + 34 * u, gy - 60 * u, 2.2 * u, 2.2 * u, STEEL)

    gunner(cx - 36 * u)
    return {"base": make_base(0.86), "shadow": make_shadow(0.86),
            "body": body, "coat": coat}


# ── relief pass: bake engraved-tin lighting from the figure silhouette ──────
def add_relief(body, coat):
    """Return body with a baked rim light / core shadow / dark contour so the
    flat reads as engraved pewter. Light from upper-right (fronts of the
    nose-right figures catch it). Computed at working resolution → antialiases.
    """
    ba = np.array(body)
    ca = np.array(coat)
    union = (ba[:, :, 3] > 30) | (ca[:, :, 3] > 30)
    uL = Image.fromarray((union * 255).astype("uint8"), "L")

    k = 2 * SS + 1
    eroded = np.array(uL.filter(ImageFilter.MinFilter(k))) > 128
    edge = union & ~eroded                                   # inner contour band
    outer = (np.array(uL.filter(ImageFilter.MaxFilter(k))) > 128) & ~union

    K = 3 * SS

    def shift(m, dx, dy):
        m = np.roll(m, dy, axis=0)
        m = np.roll(m, dx, axis=1)
        return m

    lit = edge & shift(union, -K, +K)     # up-right-facing edge  -> highlight
    drk = edge & shift(union, +K, -K)     # down-left-facing edge -> shade

    fx = np.zeros((W, W, 4), dtype=np.uint8)
    fx[outer] = (22, 18, 14, 210)         # crisp dark contour (separation)
    fx[drk] = (30, 24, 18, 120)           # core shadow (semi -> darkens)
    fx[lit] = RIM                         # bright pewter rim
    fx_img = Image.fromarray(fx, "RGBA")
    return Image.alpha_composite(body, fx_img)


# ── assembly / export ───────────────────────────────────────────────────────
ARMS = {"infantry": build_infantry, "cavalry": build_cavalry, "artillery": build_artillery}
LAYER_ORDER = ["shadow", "base", "coat", "body"]  # bottom -> top (body edges over coat)


def downscale(img):
    return img.resize((FRAME, FRAME), Image.LANCZOS)


def tint_coat(coat_small, color):
    """Multiply the light-gray coat mask by a nation colour (preview only)."""
    r, g, b = color
    px = coat_small.load()
    out = coat_small.copy()
    o = out.load()
    for y in range(FRAME):
        for x in range(FRAME):
            cr, cg, cb, ca = px[x, y]
            o[x, y] = (cr * r // 255, cg * g // 255, cb * b // 255, ca)
    return out


def composite(layers, tint=None):
    img = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    for name in LAYER_ORDER:
        lay = layers[name]
        if name == "coat" and tint is not None:
            lay = tint_coat(lay, tint)
        img = Image.alpha_composite(img, lay)
    return img


FACTIONS = {  # a few Utils.NATION_COLORS entries, 0-255, for the tint preview
    "France": (65, 105, 225), "Britain": (220, 20, 60),
    "Austria": (255, 215, 0), "Russia": (51, 128, 51), "Prussia": (60, 60, 66),
}


def build_all():
    """Render each arm at working res, bake relief, downscale, mirror to L."""
    out = {}
    for arm, fn in ARMS.items():
        raw = fn()
        raw["body"] = add_relief(raw["body"], raw["coat"])
        R = {k: downscale(v) for k, v in raw.items()}
        Lf = {k: v.transpose(Image.FLIP_LEFT_RIGHT) for k, v in R.items()}
        out[arm] = {"r": R, "l": Lf}
    return out


LAYERS = ("base", "shadow", "coat", "body")


def export_pieces(dest):
    """Write the 24 canonical piece sprites: {arm}_{layer}_{facing}.png."""
    os.makedirs(dest, exist_ok=True)
    art = build_all()
    n = 0
    for arm, facings in art.items():
        for f, layers in facings.items():
            for layer in LAYERS:
                layers[layer].save(os.path.join(dest, f"{arm}_{layer}_{f}.png"))
                n += 1
    print(f"exported {n} sprites -> {dest}")


def write_contact_sheet(out):
    """QA montage: neutral | France R | France L | Austria | coat-mask | 64px map."""
    os.makedirs(out, exist_ok=True)
    art = build_all()
    labels = ["infantry", "cavalry", "artillery"]
    BG = (30, 32, 40, 255)
    sheet = Image.new("RGBA", (FRAME * 6, FRAME * 3), BG)
    for row, arm in enumerate(labels):
        R, Lf = art[arm]["r"], art[arm]["l"]
        neutral = composite(R)                       # standalone tin
        fr = composite(R, tint=FACTIONS["France"])   # faction right
        fl = composite(Lf, tint=FACTIONS["France"])  # faction left
        mask = Image.alpha_composite(Image.new("RGBA", (FRAME, FRAME), BG), R["coat"])
        terrain = Image.new("RGBA", (FRAME, FRAME), (74, 96, 66, 255))
        small64 = composite(R, tint=FACTIONS["France"]).resize((72, 72), Image.LANCZOS)
        terrain.alpha_composite(small64, (FRAME // 2 - 36, FRAME // 2 - 36))
        aus = composite(R, tint=FACTIONS["Austria"])
        for col, im in enumerate([neutral, fr, fl, aus, mask, terrain]):
            tile = Image.alpha_composite(Image.new("RGBA", (FRAME, FRAME), BG), im)
            sheet.paste(tile, (col * FRAME, row * FRAME))
    dst = os.path.join(out, "_contact_sheet.png")
    sheet.convert("RGB").save(dst)
    print("wrote", dst)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "export"
    if mode == "export":
        export_pieces(sys.argv[2] if len(sys.argv) > 2 else PIECES_DEST)
    elif mode == "qa":
        write_contact_sheet(sys.argv[2] if len(sys.argv) > 2 else OUT)
    else:
        raise SystemExit(f"unknown mode {mode!r}; use: export [DIR] | qa [DIR]")


if __name__ == "__main__":
    main()
