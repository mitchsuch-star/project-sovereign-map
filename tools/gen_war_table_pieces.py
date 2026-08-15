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

# ── palette — CARVED WOOD (July 13 rework) ──────────────────────────────────
# The figure is now one turned/carved wooden object: tone-only differentiation
# (light oak -> dark walnut) so it reads as wood, NOT a painted tin soldier. The
# faction colour lives on the base-rim band + flag/shabraque/guidon (the coat
# tint-mask), never on the figure. The per-part variable names are KEPT from the
# old tin palette so every drawing call is unchanged — only the values move to
# wood, and value-contrast between parts is preserved so the carving still reads.
OAK_HI      = (202, 160, 108, 255)   # lit wood (legs, face, belt, plume, highlights)
OAK         = (170, 126, 80, 255)    # mid wood (coat mass, horse)
OAK_DK      = (130, 94, 58, 255)     # shadowed wood
WALNUT      = (96, 66, 40, 255)      # dark wood (boots, shako, hair, hooves, metal)
WALNUT_DK   = (64, 44, 26, 255)      # darkest carved accents

STEEL       = (214, 178, 126, 255)   # "bright" carved wood (bayonet/sabre/hub glint)
STEEL_DK    = WALNUT
BRONZE      = (178, 132, 76, 255)    # warm wood (cannon barrel, hilt, finial)
BRONZE_DK   = WALNUT
WOOD        = OAK_DK                  # flagpole, musket stock, gun trail beam
WOOD_DK     = WALNUT
BLACK_GEAR  = WALNUT                  # boots / shako -> dark carved wood (not black)
BLACK_HI    = OAK_DK                  # shako top band
FLESH       = (206, 164, 112, 255)   # face -> light wood
FLESH_DK    = OAK
BREECH      = OAK_HI                  # breeches / plume / crossbelt -> lit wood
BREECH_DK   = OAK
HORSE       = OAK                     # horse body
HORSE_DK    = OAK_DK
HORSE_MANE  = WALNUT
SLATE       = OAK                     # rider coat fallback
SLATE_DK    = OAK_DK
RIM         = (228, 196, 146, 235)   # warm wood rim light (was cool pewter)

# coat mask (multiplied by nation colour): near-white base, darker grooves.
# Now carries ONLY the faction accents (base-rim band + flag / shabraque / guidon).
COAT_HI     = (244, 244, 244, 255)
COAT_MID    = (210, 210, 210, 255)
COAT_LO     = (168, 168, 168, 255)

BASE_TOP    = (168, 126, 78, 255)    # turned-wood base, lit top face
BASE_MID    = (128, 92, 54, 255)
BASE_RIM    = (86, 60, 34, 255)
BASE_HI     = (208, 174, 122, 235)

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
    """Soft contact shadow grounding the piece on the terrain.

    NOTE: the base disc (drawn ON TOP of this layer) is opaque, so a shadow
    tucked *under* it is invisible — earlier it used 0.82x the base radius and
    never showed a pixel. This draws it slightly WIDER than the base and dropped
    below centre, so a feathered halo peeks past the base's lower rim and reads
    as the piece casting a shadow on the ground.
    """
    lay = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    base_rx = width_frac * W * 0.5
    rx = base_rx * 1.08                 # past the base rim so the halo shows
    ry = rx * 0.26
    cy = GY + 9 * SS                     # dropped below the base so it reads as ground
    d = ImageDraw.Draw(lay)
    d.ellipse([CX - rx, cy - ry, CX + rx, cy + ry], fill=SHADOW_COL + (130,))
    d.ellipse([CX - rx * 0.62, cy - ry * 0.72, CX + rx * 0.62, cy + ry * 0.72],
              fill=SHADOW_COL + (185,))
    return lay.filter(ImageFilter.GaussianBlur(8 * SS))


# ── coat / faction helpers ──────────────────────────────────────────────────
def paint_wood_coat(body, pts, groove=None):
    """Paint the coat mass into the BODY as carved wood (mid oak + a lower-half
    shade + walnut grooves). The figure is now wood, not a faction-tinted mass —
    faction colour rides the base-rim + flag/shabraque accents instead."""
    smooth_fill(body, pts, OAK)
    dense = catmull(pts)
    ys = [p[1] for p in dense]
    ymid = (min(ys) + max(ys)) * 0.5
    lower = [p for p in dense if p[1] > ymid]          # bottom-half volume shade
    if len(lower) > 2:
        ImageDraw.Draw(body).polygon(lower, fill=OAK_DK)
    # carved-edge contour: defines the coat as a turned mass AND separates
    # overlapping infantry figures (which share one wood tone) from each other.
    stroke(body, pts, WALNUT_DK, 1.4 * SS, closed=True, smooth=True)
    if groove:
        for g in groove:
            stroke(body, g, WALNUT, 2.0 * SS, smooth=True)


def faction_fill(coat, pts, groove=None):
    """Paint a faction accent (flag / shabraque / guidon) into the coat tint-mask
    — near-white so Godot `modulate` multiplies it to the nation hue."""
    smooth_fill(coat, pts, COAT_HI)
    dense = catmull(pts)
    ys = [p[1] for p in dense]
    ymid = (min(ys) + max(ys)) * 0.5
    lower = [p for p in dense if p[1] > ymid]
    if len(lower) > 2:
        ImageDraw.Draw(coat).polygon(lower, fill=COAT_MID)
    if groove:
        for g in groove:
            stroke(coat, g, COAT_LO, 1.6 * SS, smooth=True)


def faction_base_rim(coat, width_frac):
    """A painted rim band around the base's top-face edge — the tell of a painted
    wooden wargame base, and the widest, most legible faction signal at map zoom.
    Drawn into the coat tint-mask so it takes the nation hue."""
    rx = width_frac * W * 0.5
    ry = rx * 0.34
    cy = GY - 2 * SS                                    # matches make_base lit top face
    ImageDraw.Draw(coat).ellipse(
        [CX - rx * 0.96, cy - ry * 0.9, CX + rx * 0.96, cy + ry * 0.9],
        outline=COAT_HI, width=int(5 * SS))


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
    # habit-long: shoulders a touch wider, tails to upper thigh, so the
    # faction hue owns a real mass at 64px map scale (the U4 coat read thin)
    coat_pts = [
        (cx - 7 * u * s, gy - 66 * u * s),   # back shoulder
        (cx + 9 * u * s, gy - 66 * u * s),   # front shoulder
        (cx + 11 * u * s, gy - 50 * u * s),  # chest
        (cx + 10 * u * s, gy - 36 * u * s),  # front hip
        (cx + 3 * u * s, gy - 32 * u * s),
        (cx - 8 * u * s, gy - 33 * u * s),   # tail bottom
        (cx - 13 * u * s, gy - 40 * u * s),  # coat-tail flare (back)
        (cx - 10 * u * s, gy - 58 * u * s),
    ]
    paint_wood_coat(body, coat_pts,
                    groove=[[(cx + 2 * u * s, gy - 64 * u * s), (cx + 3 * u * s, gy - 38 * u * s)]])
    # cross-belt (white) over coat
    stroke(body, [(cx - 7 * u * s, gy - 64 * u * s), (cx + 10 * u * s, gy - 44 * u * s)],
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
    # back-to-front so overlaps read (painter's order); figures sized up ~12%
    # from U4 so the rank fills the frame and survives the 64px map read
    foot_soldier(body, coat, CX - 39 * SS, s=1.05)
    foot_soldier(body, coat, CX + 34 * SS, s=1.10)
    foot_soldier(body, coat, CX - 2 * SS, s=1.19, bearer=True)   # centre bearer, tallest
    faction_base_rim(coat, 0.80)                                  # painted base band
    return {"base": make_base(0.80), "shadow": make_shadow(0.80),
            "body": body, "coat": coat}


# =============================================================================
#  CAVALRY  — single horse + rider in side profile, sabre raised
#  (U4-review rework: the first pass read as a sprawl of thin legs with a
#   muddled head; this pass = deep-chested barrel, arched neck into a wedge
#   head with ears, two clean leg PAIRS in a classic gallop, a bigger rider,
#   and a faction-tinted shabraque so the nation hue reads at 64px)
# =============================================================================
def build_cavalry():
    body, coat = new_layer(), new_layer()
    u = SS
    gy = GY
    cx = CX

    # --- far-side legs first (darker, behind the barrel) ---
    for (hip, knee, hoof, wd) in [
        ((cx + 20 * u, gy - 36 * u), (cx + 34 * u, gy - 22 * u), (cx + 47 * u, gy - 10 * u), 5.6),  # far fore
        ((cx - 30 * u, gy - 38 * u), (cx - 42 * u, gy - 18 * u), (cx - 50 * u, gy - 2 * u), 5.6),   # far hind
    ]:
        stroke(body, [hip, knee, hoof], HORSE_DK, wd * u, smooth=True)
        disc(body, hoof[0], hoof[1], 2.6 * u, 2.2 * u, BLACK_GEAR)

    # --- streaming tail (behind the rump) ---
    smooth_fill(body, [
        (cx - 46 * u, gy - 56 * u), (cx - 62 * u, gy - 52 * u),
        (cx - 72 * u, gy - 38 * u), (cx - 67 * u, gy - 28 * u),
        (cx - 58 * u, gy - 40 * u), (cx - 48 * u, gy - 48 * u),
    ], HORSE_MANE)

    # --- barrel: deep chest, round rump ---
    torso = [
        (cx - 44 * u, gy - 56 * u),   # top of rump
        (cx - 18 * u, gy - 62 * u),   # back
        (cx + 8 * u, gy - 62 * u),    # withers
        (cx + 24 * u, gy - 58 * u),   # neck-base top
        (cx + 30 * u, gy - 46 * u),   # chest front
        (cx + 24 * u, gy - 32 * u),   # girth
        (cx - 4 * u, gy - 29 * u),    # belly
        (cx - 30 * u, gy - 33 * u),   # flank
        (cx - 48 * u, gy - 42 * u),   # hindquarter
    ]
    smooth_fill(body, torso, HORSE)
    # lower belly shade (volume)
    ImageDraw.Draw(body).polygon(
        [(cx - 30 * u, gy - 33 * u), (cx + 24 * u, gy - 32 * u),
         (cx + 18 * u, gy - 25 * u), (cx - 28 * u, gy - 26 * u)], fill=HORSE_DK)

    # --- near-side legs (over the barrel): classic gallop ---
    for (hip, knee, hoof, wd) in [
        ((cx + 22 * u, gy - 38 * u), (cx + 42 * u, gy - 28 * u), (cx + 58 * u, gy - 18 * u), 6.6),  # near fore, reaching
        ((cx - 34 * u, gy - 40 * u), (cx - 50 * u, gy - 22 * u), (cx - 62 * u, gy - 2 * u), 6.6),   # near hind, driving
    ]:
        stroke(body, [hip, knee, hoof], HORSE, wd * u, smooth=True)
        disc(body, hoof[0], hoof[1], 2.8 * u, 2.4 * u, BLACK_GEAR)

    # --- arched neck rising to the poll ---
    neck = [
        (cx + 16 * u, gy - 62 * u),   # base at withers
        (cx + 36 * u, gy - 80 * u),   # crest
        (cx + 46 * u, gy - 88 * u),   # poll
        (cx + 50 * u, gy - 80 * u),   # forehead front
        (cx + 40 * u, gy - 60 * u),   # throat
        (cx + 30 * u, gy - 46 * u),   # chest join
    ]
    smooth_fill(body, neck, HORSE)
    # wedge head: poll -> muzzle pointing forward-down
    head = [
        (cx + 42 * u, gy - 90 * u),
        (cx + 52 * u, gy - 87 * u),
        (cx + 64 * u, gy - 75 * u),   # muzzle top
        (cx + 62 * u, gy - 69 * u),   # lip
        (cx + 49 * u, gy - 72 * u),   # jaw
        (cx + 39 * u, gy - 79 * u),
    ]
    smooth_fill(body, head, HORSE)
    # ears (the "horse" tell in pure silhouette)
    stroke(body, [(cx + 43 * u, gy - 90 * u), (cx + 40 * u, gy - 98 * u)], HORSE_DK, 2.4 * u)
    stroke(body, [(cx + 48 * u, gy - 89 * u), (cx + 48 * u, gy - 97 * u)], HORSE_DK, 2.4 * u)
    # mane along the crest
    stroke(body, [(cx + 12 * u, gy - 63 * u), (cx + 32 * u, gy - 79 * u), (cx + 44 * u, gy - 90 * u)],
           HORSE_MANE, 4.0 * u, smooth=True)

    # --- shabraque (saddle cloth) : faction-tinted mass under the rider ---
    rx_ = cx - 4 * u
    ry_ = gy - 62 * u                 # rider hip / saddle point
    shab = [(rx_ - 13 * u, ry_ + 1 * u), (rx_ + 13 * u, ry_ + 1 * u),
            (rx_ + 15 * u, ry_ + 16 * u), (rx_ - 16 * u, ry_ + 16 * u)]
    faction_fill(coat, shab)          # saddle-cloth carries the nation hue

    # --- rider (bigger than U4 so he owns the top half) ---
    # near leg over the shabraque
    stroke(body, [(rx_ + 2 * u, ry_ + 2 * u), (rx_ + 8 * u, ry_ + 14 * u), (rx_ + 10 * u, ry_ + 26 * u)],
           SLATE_DK, 5 * u, smooth=True)
    disc(body, rx_ + 10 * u, ry_ + 27 * u, 3 * u, 2.4 * u, BLACK_GEAR)   # boot
    # torso coat (tint mass)
    torso_r = [(rx_ - 10 * u, ry_ + 2 * u), (rx_ + 10 * u, ry_ + 2 * u),
               (rx_ + 12 * u, ry_ - 16 * u), (rx_ + 6 * u, ry_ - 26 * u),
               (rx_ - 8 * u, ry_ - 24 * u), (rx_ - 14 * u, ry_ - 10 * u)]
    paint_wood_coat(body, torso_r)
    stroke(body, [(rx_ - 8 * u, ry_ - 22 * u), (rx_ + 10 * u, ry_ - 4 * u)], BREECH, 2.6 * u)  # crossbelt
    # reins: hand to the muzzle
    stroke(body, [(rx_ + 11 * u, ry_ - 6 * u), (cx + 58 * u, gy - 73 * u)], BLACK_GEAR, 1.5 * u)
    # head + shako + plume
    disc(body, rx_ + 2 * u, ry_ - 30 * u, 5 * u, 5.5 * u, FLESH)
    hard_fill(body, [(rx_ - 4 * u, ry_ - 32 * u), (rx_ + 8 * u, ry_ - 32 * u),
                     (rx_ + 8 * u, ry_ - 45 * u), (rx_ - 4 * u, ry_ - 45 * u)], BLACK_GEAR)
    disc(body, rx_ + 2 * u, ry_ - 45 * u, 5.5 * u, 2.0 * u, BLACK_HI)   # top band
    stroke(body, [(rx_ + 2 * u, ry_ - 45 * u), (rx_ + 0 * u, ry_ - 57 * u)], BREECH, 3.2 * u)  # plume
    # near arm raised, curved sabre clearing the shako
    sh = (rx_ + 6 * u, ry_ - 18 * u)
    hand = (rx_ + 22 * u, ry_ - 44 * u)
    stroke(body, [sh, (rx_ + 16 * u, ry_ - 30 * u), hand], SLATE_DK, 4.2 * u, smooth=True)
    stroke(body, [hand, (rx_ + 33 * u, ry_ - 62 * u), (rx_ + 40 * u, ry_ - 78 * u)],
           STEEL, 2.8 * u, smooth=True)                                   # curved blade
    disc(body, hand[0], hand[1], 2.6 * u, 2.6 * u, BRONZE)                # hilt
    faction_base_rim(coat, 0.58)                                          # painted base band
    return {"base": make_base(0.58), "shadow": make_shadow(0.66),
            "body": body, "coat": coat}


# =============================================================================
#  ARTILLERY — broadside gun (big spoked wheel + barrel + trail) + crew
# =============================================================================
def build_artillery():
    body, coat = new_layer(), new_layer()
    u = SS * 1.1   # U4 review: the gun sat small in frame — +10% for the map read
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
        torso = [(gx - 7 * u, gy - 51 * u), (gx + 7 * u, gy - 49 * u),
                 (gx + 8 * u, gy - 36 * u), (gx + 4 * u, gy - 28 * u),
                 (gx - 6 * u, gy - 29 * u), (gx - 8 * u, gy - 38 * u)]
        paint_wood_coat(body, torso)
        stroke(body, [(gx - 5 * u, gy - 49 * u), (gx + 7 * u, gy - 37 * u)],
               BREECH, 2.2 * u)                                                  # crossbelt
        disc(body, gx + 1 * u, gy - 55 * u, 5 * u, 5.5 * u, FLESH)               # face
        hard_fill(body, [(gx - 4 * u, gy - 56 * u), (gx + 6 * u, gy - 56 * u),
                         (gx + 6 * u, gy - 68 * u), (gx - 4 * u, gy - 68 * u)], BLACK_GEAR)  # shako
        disc(body, gx + 1 * u, gy - 68 * u, 5 * u, 1.8 * u, BLACK_HI)            # top band
        stroke(body, [(gx + 1 * u, gy - 68 * u), (gx, gy - 78 * u)], BREECH, 2.8 * u)  # plume
        # ramrod raised toward the muzzle (up-right, in-plane against the gun)
        stroke(body, [(gx + 5 * u, gy - 42 * u), (gx + 34 * u, gy - 60 * u)], WOOD, 2.2 * u)
        disc(body, gx + 34 * u, gy - 60 * u, 2.2 * u, 2.2 * u, STEEL)

    gunner(cx - 36 * u)
    # faction guidon on a short staff planted behind the gun (the arm's colour hit)
    gpx = cx - 54 * u
    line(body, (gpx, gy - 2 * u), (gpx, gy - 76 * u), WOOD, 2.2 * u)      # staff
    disc(body, gpx, gy - 78 * u, 2.2 * u, 2.2 * u, BRONZE)               # finial
    faction_fill(coat, [(gpx, gy - 74 * u), (gpx + 22 * u, gy - 70 * u),
                        (gpx + 17 * u, gy - 62 * u), (gpx + 22 * u, gy - 54 * u),
                        (gpx, gy - 58 * u)])
    faction_base_rim(coat, 0.86)                                         # painted base band
    return {"base": make_base(0.86), "shadow": make_shadow(0.86),
            "body": body, "coat": coat}


# =============================================================================
#  SHIP OF THE LINE  (NV-7) — a carved two-decker for the naval diorama
# =============================================================================
# Same carved-timber language as the three land arms, and deliberately the same
# turned base disc: this is a WAR-TABLE piece, not an illustration of the sea.
# The faction accent is the ensign at the mizzen peak plus the painted base rim
# — the two places every other arm puts it. Only ever rendered on the diorama
# stage (no map arm exists for fleets: NAVAL_SPEC Q1(a) keeps the model to one
# national record, so there is nothing on the map for a ship piece to BE).
def build_ship():
    # NV-8a (Aug 2, 2026, user visual pass): REBUILT UNDER SAIL. The first
    # cut furled every sail to its yard, and at 58px a stack of furled yards
    # reads as pancakes — worse when the figure fell, when the mast-and-yard
    # assembly read as spoked WHEELS on the tableau. A ship of the line is
    # recognised by her pyramid of set canvas, so she now carries it:
    # courses and topsails drawn full, a jib to the bowsprit, a gaff
    # spanker aft, the faction ensign at the spanker peak. Canvas is pale
    # carved timber (the piece stays a carved object, not a painting).
    body, coat = new_layer(), new_layer()
    u = SS * 1.05
    # The hull sits ON the turned base, not in it (first-pass lesson kept):
    # gy is the SHIP's waterline; make_base/faction_base_rim keep using GY.
    gy, cx = GY - 11 * SS, CX
    CANVAS = (222, 204, 168, 255)     # pale carved canvas
    CANVAS_DK = (192, 172, 136, 255)  # sail foot shade / outline

    # --- hull: long two-decker, bow to the RIGHT ---
    hull = [
        (cx - 64 * u, gy - 28 * u),                       # stern taffrail
        (cx - 58 * u, gy - 4 * u), (cx - 26 * u, gy + 2 * u),
        (cx + 24 * u, gy + 2 * u), (cx + 52 * u, gy - 5 * u),
        (cx + 64 * u, gy - 17 * u),                       # beakhead
        (cx + 46 * u, gy - 22 * u), (cx - 42 * u, gy - 24 * u),
    ]
    smooth_fill(body, hull, OAK)
    stroke(body, hull, WALNUT_DK, 1.6 * SS, closed=True, smooth=True)
    # the two gun strakes with their ports — what makes her a LINER
    for k, dy in enumerate((11.0, 18.0)):
        stroke(body, [(cx - 56 * u, gy - dy * u),
                      (cx + 48 * u, gy - (dy + 3) * u)], WALNUT, 2.0 * SS)
        for port in range(9):
            px = cx - 50 * u + port * 12.0 * u
            py = gy - (dy + 0.28 * port) * u
            disc(body, px, py, 2.0 * u, 1.7 * u, WALNUT_DK)
    # stern gallery (the captain's windows) + rail
    smooth_fill(body, [
        (cx - 64 * u, gy - 28 * u), (cx - 56 * u, gy - 31 * u),
        (cx - 50 * u, gy - 23 * u), (cx - 56 * u, gy - 7 * u),
        (cx - 62 * u, gy - 9 * u),
    ], OAK_DK)
    stroke(body, [(cx - 60 * u, gy - 25 * u), (cx - 52 * u, gy - 25 * u)],
           OAK_HI, 1.4 * SS)
    # bowsprit, steeved up from the beakhead
    stroke(body, [(cx + 54 * u, gy - 21 * u), (cx + 88 * u, gy - 42 * u)],
           WOOD, 2.6 * SS)

    def square_sail(mx, y_top, half_head, half_foot, h):
        """One set square sail: head on its yard, foot billowing down-and-
        out. Big simple shapes — it must read at 58px."""
        pts = [
            (mx - half_head * u, y_top), (mx + half_head * u, y_top),
            (mx + half_foot * u, y_top + h * 0.78 * u),
            (mx, y_top + h * u),                    # curved billow at foot
            (mx - half_foot * u, y_top + h * 0.78 * u),
        ]
        smooth_fill(body, pts, CANVAS)
        stroke(body, pts, CANVAS_DK, 1.3 * SS, closed=True, smooth=True)
        # the yard the head is bent to
        stroke(body, [(mx - (half_head + 3) * u, y_top),
                      (mx + (half_head + 3) * u, y_top)], WOOD_DK, 1.8 * SS)

    # --- three masts (stern left → mizzen, main, fore), sails SET ---
    # Tuned at NV-8a round 2: the first set crowded — adjacent stacks
    # merged into one canvas blob at 58px. Each mast now owns a distinct
    # column (wider spacing, narrower sails, real gaps), the classic
    # three-pyramid silhouette with sky between the stacks.
    # (x, height above waterline, [(half_head, half_foot, sail_h), ...]
    #  listed topgallant-first, drawn downward)
    masts = [
        (cx - 44 * u, 82.0, [(9.0, 11.0, 14.0)]),                     # mizzen
        (cx - 2 * u, 120.0, [(7.0, 9.0, 11.0), (11.0, 13.0, 16.0),
                             (14.0, 17.0, 20.0)]),                    # main
        (cx + 36 * u, 102.0, [(9.0, 11.0, 14.0),
                              (12.0, 15.0, 18.0)]),                   # fore
    ]
    for mx, height, sails in masts:
        top = gy - height * u
        stroke(body, [(mx, gy - 22 * u), (mx, top)], WOOD, 2.6 * SS)
        # masthead visible above the top sail (the truck)
        y = top + 5 * u
        for half_head, half_foot, h in sails:   # topgallant down to course
            square_sail(mx, y, half_head, half_foot, h)
            y += (h + 5.0) * u

    # --- the spanker: gaff sail aft of the mizzen ---
    mz = cx - 44 * u
    gaff_peak = (mz - 24 * u, gy - 68 * u)
    spanker = [
        (mz, gy - 62 * u), gaff_peak,
        (mz - 20 * u, gy - 30 * u), (mz, gy - 28 * u),
    ]
    smooth_fill(body, spanker, CANVAS_DK)
    stroke(body, spanker, WALNUT, 1.3 * SS, closed=True, smooth=True)
    stroke(body, [(mz, gy - 62 * u), gaff_peak], WOOD_DK, 1.8 * SS)  # gaff

    # --- headsail: one modest jib between bowsprit and the fore course ---
    # (round 3: a full-height jib merged with the fore stack into one blob;
    # it stays BELOW the fore topsail so the fore column keeps its shape)
    jib = [(cx + 82 * u, gy - 38 * u), (cx + 54 * u, gy - 60 * u),
           (cx + 54 * u, gy - 26 * u)]
    smooth_fill(body, jib, CANVAS)
    stroke(body, jib, CANVAS_DK, 1.2 * SS, closed=True, smooth=True)

    # --- the ensign at the spanker peak: the faction's one colour hit ---
    ex, ey = gaff_peak
    faction_fill(coat, [
        (ex, ey), (ex - 20 * u, ey - 5 * u),
        (ex - 17 * u, ey + 4 * u), (ex - 20 * u, ey + 12 * u),
        (ex, ey + 9 * u),
    ])
    faction_base_rim(coat, 0.92)
    return {"base": make_base(0.92), "shadow": make_shadow(0.92),
            "body": body, "coat": coat}


# ── wood grain: multiply near-vertical timber grain into the figure ─────────
def add_grain(body):
    """Multiply subtle near-vertical wood grain into the figure so it reads as
    carved timber. RGB-only (alpha untouched -> relief geometry unaffected)."""
    ba = np.array(body).astype(np.float32)
    alpha = ba[:, :, 3] > 20
    xs = np.arange(W, dtype=np.float32)[None, :]
    ys = np.arange(W, dtype=np.float32)[:, None]
    warp = np.sin(ys * 0.010) * 5.0                  # gentle waver so grain isn't ruled
    g = (np.sin((xs + warp) * 0.22)
         + 0.55 * np.sin((xs + warp) * 0.51 + 1.7)
         + 0.30 * np.sin(xs * 0.09 + ys * 0.006))
    g = (g - g.min()) / (g.max() - g.min())          # 0..1
    factor = (0.88 + 0.17 * g)[:, :, None]           # 0.88 .. 1.05 tonal ripple
    rgb = np.clip(ba[:, :, :3] * factor, 0, 255)
    ba[:, :, :3] = np.where(alpha[:, :, None], rgb, ba[:, :, :3])
    return Image.fromarray(ba.astype(np.uint8), "RGBA")


# ── relief pass: bake carved-wood lighting from the figure silhouette ───────
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
    fx[outer] = (38, 24, 14, 205)         # warm dark contour (separation)
    fx[drk] = (44, 28, 16, 120)           # warm core shadow (semi -> darkens)
    fx[lit] = RIM                         # warm wood rim light
    fx_img = Image.fromarray(fx, "RGBA")
    return Image.alpha_composite(body, fx_img)


# =============================================================================
#  EMPEROR (NP-5, NAPOLEON_SPEC §9) — the sovereign's own map piece: ONE
#  figure where infantry is a rank, because the man IS the piece. The
#  silhouette is the two things Europe recognised at a mile: the bicorne
#  worn athwart (en bataille) and the long plain redingote with the hand
#  tucked. Same turned base, same carved-timber language, same faction
#  accents (coat mass + painted base rim). The backend arm derivation
#  branches on Marshal.is_sovereign FIRST — never cavalry=True, which
#  silently drags recklessness/charge/combined-arms (survey warning).
# =============================================================================
def build_emperor():
    body, coat = new_layer(), new_layer()
    u = SS
    gy, cx = GY, CX
    s = 1.45   # the tallest figure on the table — he must read at 64px

    # --- legs: standing at ease, breeches + boots ---
    smooth_fill(body, [
        (cx - 3 * u * s, gy - 38 * u * s), (cx - 7 * u * s, gy - 20 * u * s),
        (cx - 7 * u * s, gy - 3 * u * s), (cx - 2 * u * s, gy - 2 * u * s),
        (cx - 1 * u * s, gy - 20 * u * s), (cx + 1 * u * s, gy - 34 * u * s),
    ], BREECH_DK)
    hard_fill(body, [(cx - 8 * u * s, gy - 12 * u * s), (cx - 8 * u * s, gy),
                     (cx - 1 * u * s, gy), (cx - 1 * u * s, gy - 12 * u * s)],
              BLACK_GEAR)
    smooth_fill(body, [
        (cx + 2 * u * s, gy - 38 * u * s), (cx + 6 * u * s, gy - 20 * u * s),
        (cx + 7 * u * s, gy - 3 * u * s), (cx + 2 * u * s, gy - 2 * u * s),
        (cx + 1 * u * s, gy - 20 * u * s),
    ], BREECH)
    hard_fill(body, [(cx + 1 * u * s, gy - 12 * u * s), (cx + 1 * u * s, gy),
                     (cx + 9 * u * s, gy), (cx + 9 * u * s, gy - 12 * u * s)],
              BLACK_GEAR)

    # --- the redingote: one long carved mass to the knee, slightly
    #     flared — grey-wood like the man's own famous coat; the faction
    #     hue rides the grand cordon + base rim below ---
    coat_pts = [
        (cx - 9 * u * s, gy - 64 * u * s),    # back shoulder
        (cx + 10 * u * s, gy - 64 * u * s),   # front shoulder
        (cx + 13 * u * s, gy - 46 * u * s),   # breast
        (cx + 14 * u * s, gy - 26 * u * s),   # front skirt
        (cx + 4 * u * s, gy - 22 * u * s),    # hem centre
        (cx - 12 * u * s, gy - 24 * u * s),   # back skirt flare
        (cx - 12 * u * s, gy - 44 * u * s),
    ]
    paint_wood_coat(body, coat_pts,
                    groove=[[(cx + 1 * u * s, gy - 62 * u * s),
                             (cx + 3 * u * s, gy - 30 * u * s)]])
    # the grand cordon: the faction's sash from right shoulder to left
    # hip — the tint mass that owns the figure at 64px (with the rim).
    # body composites ABOVE coat, and ImageDraw.polygon REPLACES pixels,
    # so the band is PUNCHED out of the carved coat (transparent fill)
    # to reveal the tint-mask below — the flag/shabraque trick, worn.
    sash = [
        (cx + 6 * u * s, gy - 63 * u * s),
        (cx + 12 * u * s, gy - 58 * u * s),
        (cx - 5 * u * s, gy - 30 * u * s),
        (cx - 11 * u * s, gy - 35 * u * s),
    ]
    smooth_fill(body, sash, (0, 0, 0, 0))
    faction_fill(coat, sash)
    # the tucked right hand at the breast — THE gesture (over the sash)
    disc(body, cx + 8 * u * s, gy - 50 * u * s, 3.4 * u * s, 3.0 * u * s,
         FLESH)

    # --- head, sitting proud of the collar ---
    disc(body, cx + 1 * u * s, gy - 71 * u * s, 6.0 * u * s, 6.6 * u * s,
         FLESH)

    # --- THE BICORNE, worn athwart (en bataille): a dark lens seated ON
    #     the head, tips just past the shoulders ---
    smooth_fill(body, [
        (cx - 15 * u * s, gy - 78 * u * s),   # left tip
        (cx - 7 * u * s, gy - 86 * u * s),
        (cx + 1 * u * s, gy - 88 * u * s),    # crown
        (cx + 9 * u * s, gy - 86 * u * s),
        (cx + 17 * u * s, gy - 78 * u * s),   # right tip
        (cx + 8 * u * s, gy - 77 * u * s),
        (cx + 1 * u * s, gy - 76 * u * s),    # brim seats on the brow
        (cx - 6 * u * s, gy - 77 * u * s),
    ], BLACK_GEAR)
    disc(body, cx + 10 * u * s, gy - 81 * u * s, 2.0 * u * s, 2.0 * u * s,
         BREECH)  # the cockade at the cock of the hat

    faction_base_rim(coat, 0.80)
    return {"base": make_base(0.80), "shadow": make_shadow(0.80),
            "body": body, "coat": coat}


# ── assembly / export ───────────────────────────────────────────────────────
ARMS = {"infantry": build_infantry, "cavalry": build_cavalry,
        "artillery": build_artillery, "ship": build_ship,
        "emperor": build_emperor}
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
        raw["body"] = add_grain(raw["body"])
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
