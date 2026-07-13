"""War-score bar art — gold-rimmed recessed track + glossy fill + centre gem.

Premium tug-of-war meter parts for the ACTIVE WARS panel, matching the game's
navy-and-gold chrome. 100% ORIGINAL procedural art (no third-party pixels).

OFFLINE dev tool — NOT run by CI or the game. Regenerate after tuning. Needs
Pillow + numpy (dev-only). Outputs 9-slice-ready textures into assets/ui/bars/:
  * warbar_track.png   — dark recessed slot with a brass/gold bevelled rim
  * warbar_fill.png    — grayscale glossy pill (modulated per nation in-engine)
  * warbar_gem.png     — small gold gem for the centre marker

Usage:
    python tools/gen_war_bars.py            # export -> assets/ui/bars/
    python tools/gen_war_bars.py qa DIR     # QA contact sheet into DIR
"""
from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS_DEST = os.path.join(
    _REPO, "godot-client", "project-sovereign", "assets", "ui", "bars")

SS = 4  # supersample


def _rrect_mask(w: int, h: int, r: float) -> Image.Image:
    """Anti-aliased rounded-rect alpha mask at supersample res."""
    m = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [0, 0, w * SS - 1, h * SS - 1], radius=r * SS, fill=255)
    return m


def _vgrad(w: int, h: int, stops) -> np.ndarray:
    """Vertical gradient RGB array (h*SS, w*SS, 3) from (pos, (r,g,b)) stops."""
    H = h * SS
    ys = np.linspace(0.0, 1.0, H)
    pos = np.array([s[0] for s in stops])
    cols = np.array([s[1] for s in stops], dtype=float)
    out = np.empty((H, 3))
    for c in range(3):
        out[:, c] = np.interp(ys, pos, cols[:, c])
    return np.repeat(out[:, None, :], w * SS, axis=1)


def gen_track(w: int = 96, h: int = 28) -> Image.Image:
    """Gold-rimmed recessed slot. Horizontal 3-slice (rounded L/R caps)."""
    r = h / 2.0
    outer = _rrect_mask(w, h, r)
    # Brass rim gradient (dark gold top edge -> bright -> dark bottom).
    brass = _vgrad(w, h, [
        (0.0, (150, 116, 52)), (0.18, (214, 176, 96)),
        (0.5, (176, 140, 70)), (0.82, (120, 92, 40)), (1.0, (92, 68, 30)),
    ])
    rim = Image.fromarray(np.dstack(
        [brass, np.array(outer)]).astype("uint8"), "RGBA")

    # Recessed dark slot, inset from the rim; darker at the TOP (inner shadow).
    inset = max(3, int(round(h * 0.14)))
    iw, ih = w - inset * 2, h - inset * 2
    ir = max(1.0, r - inset)
    slot_mask = _rrect_mask(iw, ih, ir)
    slot_rgb = _vgrad(iw, ih, [
        (0.0, (16, 17, 24)), (0.45, (30, 32, 44)), (1.0, (40, 43, 58)),
    ])
    slot = Image.fromarray(np.dstack(
        [slot_rgb, np.array(slot_mask)]).astype("uint8"), "RGBA")
    rim.alpha_composite(slot, (inset * SS, inset * SS))

    # Thin bright bevel highlight along the top inner rim.
    hl = Image.new("RGBA", rim.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).arc(
        [2 * SS, 2 * SS, (w - 2) * SS, (h * 1.4) * SS],
        190, 350, fill=(245, 226, 170, 150), width=int(1.4 * SS))
    rim.alpha_composite(hl)
    return rim.resize((w, h), Image.LANCZOS)


def gen_fill(w: int = 72, h: int = 22) -> Image.Image:
    """Grayscale glossy pill — near-white so `modulate` tints it to the nation
    hue while keeping the gloss. Rounded both ends (nests in the track)."""
    r = h / 2.0
    mask = _rrect_mask(w, h, r)
    body = _vgrad(w, h, [
        (0.0, (250, 250, 250)), (0.42, (214, 214, 214)),
        (0.5, (198, 198, 198)), (1.0, (150, 150, 150)),
    ])
    img = Image.fromarray(np.dstack(
        [body, np.array(mask)]).astype("uint8"), "RGBA")
    # Top gloss highlight (a soft bright lens in the upper third).
    gloss = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(gloss).rounded_rectangle(
        [int(2.5 * SS), int(2 * SS), (w - 2.5) * SS, int(h * 0.44) * SS],
        radius=int(h * 0.22) * SS, fill=(255, 255, 255, 90))
    gloss = gloss.filter(ImageFilter.GaussianBlur(1.6 * SS))
    img.alpha_composite(gloss)
    img.putalpha(Image.composite(img.getchannel("A"),
                                 Image.new("L", img.size, 0), mask))
    return img.resize((w, h), Image.LANCZOS)


def gen_gem(d: int = 26) -> Image.Image:
    """Small faceted gold gem for the centre marker."""
    D = d * SS
    img = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx, cy = D / 2, D / 2
    r = D * 0.42
    diamond = [(cx, cy - r), (cx + r * 0.72, cy), (cx, cy + r), (cx - r * 0.72, cy)]
    dr.polygon(diamond, fill=(206, 168, 86, 255), outline=(92, 68, 30, 255))
    # top-left facet highlight
    dr.polygon([(cx, cy - r), (cx + r * 0.72, cy), (cx, cy)],
               fill=(230, 200, 130, 255))
    dr.polygon([(cx, cy - r), (cx, cy), (cx - r * 0.72, cy)],
               fill=(244, 224, 168, 255))
    dr.line([(cx, cy - r), (cx, cy + r)], fill=(120, 92, 40, 180), width=SS)
    return img.resize((d, d), Image.LANCZOS)


PARTS = {"warbar_track": gen_track, "warbar_fill": gen_fill, "warbar_gem": gen_gem}


def export(dest: str) -> None:
    os.makedirs(dest, exist_ok=True)
    for name, fn in PARTS.items():
        fn().save(os.path.join(dest, f"{name}.png"))
    print(f"exported {len(PARTS)} bar textures -> {dest}")


def qa(out: str) -> None:
    """Contact sheet: parts + a composited tug-of-war preview at a few scores."""
    os.makedirs(out, exist_ok=True)
    track, fill, gem = gen_track(), gen_fill(), gen_gem()
    BG = (150, 120, 80, 255)
    PANEL = (22, 22, 31, 255)

    def preview(score: int, w: int = 240, h: int = 22) -> Image.Image:
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        # track (3-slice by hand: left cap | stretched centre | right cap)
        cap = track.height // 2
        t = Image.new("RGBA", (w, track.height), (0, 0, 0, 0))
        t.paste(track.crop((0, 0, cap, track.height)), (0, 0))
        t.paste(track.crop((track.width - cap, 0, track.width, track.height)),
                (w - cap, 0))
        mid = track.crop((cap, 0, track.width - cap, track.height)).resize(
            (w - 2 * cap, track.height))
        t.paste(mid, (cap, 0))
        im.alpha_composite(t.resize((w, h)))
        cx = w // 2
        if score != 0:
            frac = min(abs(score), 100) / 100.0
            fw = int(frac * (w / 2 - 6))
            col = (72, 110, 222) if score > 0 else (210, 80, 60)
            f = fill.resize((max(6, fw), h - 6))
            tint = Image.new("RGBA", f.size, col + (255,))
            f = Image.composite(tint, Image.new("RGBA", f.size, (0, 0, 0, 0)),
                                f.getchannel("A"))
            fg = fill.resize((max(6, fw), h - 6)).getchannel("A")
            f.putalpha(fg)
            im.alpha_composite(f, (cx if score > 0 else cx - fw, 3))
        g = gem.resize((h + 2, h + 2))
        im.alpha_composite(g, (cx - g.width // 2, h // 2 - g.height // 2))
        return im

    rows = [("0", 0), ("+35", 35), ("-60", -60), ("+90", 90)]
    pad = 14
    sheet = Image.new("RGBA", (320, 60 + len(rows) * 40), BG)
    d = ImageDraw.Draw(sheet)
    y = 10
    for label, sc in rows:
        card = Image.new("RGBA", (280, 30), PANEL)
        card.alpha_composite(preview(sc), (20, 4))
        sheet.alpha_composite(card, (pad, y))
        d.text((pad + 2, y + 9), label, fill=(240, 240, 240))
        y += 40
    # raw parts strip
    sheet.alpha_composite(track, (pad, y + 2))
    sheet.alpha_composite(fill, (pad + 110, y + 4))
    sheet.alpha_composite(gem, (pad + 200, y))
    dst = os.path.join(out, "_warbar_qa.png")
    sheet.convert("RGB").save(dst)
    print("wrote", dst)


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "export"
    if mode == "export":
        export(sys.argv[2] if len(sys.argv) > 2 else BARS_DEST)
    elif mode == "qa":
        qa(sys.argv[2] if len(sys.argv) > 2 else ".")
    else:
        raise SystemExit(f"unknown mode {mode!r}; use: export [DIR] | qa [DIR]")


if __name__ == "__main__":
    main()
