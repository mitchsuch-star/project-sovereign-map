"""UXR-D2 "High contrast" (Pre-Deploy S9b) — the contrast instrument (UXR-3's R3).

    .venv/Scripts/python.exe -X utf8 tools/uxr2b_contrast_report.py <run>/index.json \
        [--surfaces a,b,c] [--record docs/audits/uxr0/contrast_<label>.json]

`tools/iq10_run_captures.py` shoots the frames; the harness records, for every
visible text row, its logical rect (clipped to the scroll that shows it) and
the colours it DECLARES: a Label / Button / LineEdit's resolved `font_color`, a
RichTextLabel's `default_color` and every `[color=…]` span of its BBCode, each
times the node's modulate chain — and a chip's `[bgcolor=…][color=…]` pair.

WCAG's contrast ratio is defined on the text's colour and the colour behind
it. The text colour is the declared one (a glyph's antialiased rim never
reaches it, so sampling ink would under-read thin type); the colour BEHIND is
read off the frame — the per-channel median of the row's rect in the PNG
(glyphs cover a minority of a text box) — because panels stack textures,
fills and translucent strips no declared colour describes. A declared colour
with alpha is blended over that background first. A chip's span is measured
against its own bgcolor. The row's ratio is the worst of its colours.

The floor (the done-when of UXR-D2, `docs/DESIGN_REFINEMENT.md` §UXR, and
UXR-3's R3 item): body text >= 4.5 : 1, caption-class text >= 3 : 1. Disabled
buttons (WCAG's inactive components) and the map's world-space tier are not
measured.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np
from PIL import Image

BODY_FLOOR = 4.5
CAPTION_FLOOR = 3.0
# Utils.bb_chip_disabled's pill: present-but-locked, an inactive component.
DISABLED_CHIP = ("20242cff", "6f7480ff")


def _lin(c: np.ndarray) -> np.ndarray:
    c = np.asarray(c, dtype=float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def luminance(rgb) -> float:
    r, g, b = _lin(np.asarray(rgb[:3], dtype=float))
    return float(0.2126 * r + 0.7152 * g + 0.0722 * b)


def ratio(fg, bg) -> float:
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def _hex(h: str) -> tuple:
    h = h.lstrip("#")
    if len(h) == 6:
        h += "ff"
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4, 6))


def blend(fg, bg) -> tuple:
    a = fg[3] if len(fg) > 3 else 1.0
    return tuple(fg[i] * a + bg[i] * (1.0 - a) for i in range(3))


def background(img: np.ndarray, rect, scale: float):
    """The median colour of the row's rect in the frame (physical px)."""
    x0, y0, w, h = rect
    X0, Y0 = int(round(x0 * scale)), int(round(y0 * scale))
    X1, Y1 = int(round((x0 + w) * scale)), int(round((y0 + h) * scale))
    X0, Y0 = max(X0, 0), max(Y0, 0)
    X1, Y1 = min(X1, img.shape[1]), min(Y1, img.shape[0])
    if X1 - X0 < 2 or Y1 - Y0 < 2:
        return None
    crop = img[Y0:Y1, X0:X1, :3].reshape(-1, 3) / 255.0
    return tuple(float(v) for v in np.median(crop, axis=0))


def measure_row(row: dict, img: np.ndarray, scale: float):
    """(worst ratio, its colour, the background) for one census row, or None
    when it is not measured."""
    if row.get("tier") == "map" or row.get("disabled") or not row.get("rect"):
        return None
    bg = background(img, row["rect"], scale)
    if bg is None:
        return None
    worst = None
    for col in row.get("colors") or []:
        c = _hex(col)
        r = ratio(blend(c, bg), bg)
        if worst is None or r < worst[0]:
            worst = (r, col, bg)
    for pair in row.get("chips") or []:
        if tuple(pair) == DISABLED_CHIP:
            continue   # Utils.bb_chip_disabled: an inactive control, WCAG-exempt
        chip_bg = blend(_hex(pair[0]), bg)
        r = ratio(blend(_hex(pair[1]), chip_bg), chip_bg)
        if worst is None or r < worst[0]:
            worst = (r, pair[1] + " on " + pair[0], chip_bg)
    return worst


def floor_for(row: dict) -> float:
    return CAPTION_FLOOR if row.get("tier") == "caption" else BODY_FLOOR


def read_run(index_path: pathlib.Path, surfaces: set | None = None) -> dict:
    index = json.loads(index_path.read_text(encoding="utf-8"))
    out = {"source": str(index_path), "client_commit": index.get("client_commit", ""),
           "physical_scale": index.get("physical_scale"), "high_contrast": index.get("high_contrast", False),
           "surfaces": {}}
    for row in index.get("rows", []):
        base = str(row.get("base_id") or row.get("id"))
        if surfaces and base not in surfaces:
            continue
        for res in row.get("results", []):
            frames = res.get("frames") or []
            if not frames:
                continue
            frame = frames[-1]
            png = frame.get("png", "")
            if not png or not pathlib.Path(png).is_file():
                continue
            img = np.asarray(Image.open(png).convert("RGB"))
            scale = float(res.get("scale", res.get("content_scale_factor", 1.0)))
            win = res.get("window") or [0, 0]
            key = "%dx%d@%.2f" % (int(win[0]), int(win[1]), scale)
            counts = {"rows": 0, "measured": 0, "under": 0}
            under = []
            for t in frame.get("texts") or []:
                counts["rows"] += 1
                m = measure_row(t, img, scale)
                if m is None:
                    continue
                counts["measured"] += 1
                fl = floor_for(t)
                if m[0] < fl - 1e-6:
                    counts["under"] += 1
                    under.append({"path": str(t.get("path", "")).split("/")[-1][:48],
                                  "text": str(t.get("text", ""))[:40], "tier": t.get("tier"),
                                  "ratio": round(m[0], 2), "floor": fl, "color": m[1],
                                  "bg": "%02x%02x%02x" % tuple(int(round(v * 255)) for v in m[2])})
            under.sort(key=lambda u: u["ratio"])
            out["surfaces"].setdefault(base, {"readings": {}})["readings"][key] = {
                "window": [int(win[0]), int(win[1])], "scale": scale, "ok": res.get("ok", False),
                "counts": counts, "under": under}
    return out


def totals(record: dict) -> dict:
    t = {"readings": 0, "measured": 0, "under": 0}
    for s in record["surfaces"].values():
        for r in s["readings"].values():
            t["readings"] += 1
            t["measured"] += r["counts"]["measured"]
            t["under"] += r["counts"]["under"]
    return t


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("index")
    ap.add_argument("--surfaces", default="")
    ap.add_argument("--record", default="")
    args = ap.parse_args(argv)
    surfaces = {s.strip() for s in args.surfaces.split(",") if s.strip()} or None
    record = read_run(pathlib.Path(args.index), surfaces)
    print("contrast:", totals(record))
    worst = sorted(((u["ratio"], sid, key, u) for sid, s in record["surfaces"].items()
                    for key, r in s["readings"].items() for u in r["under"]), key=lambda x: x[0])
    for rr, sid, key, u in worst[:25]:
        print(f"  {rr:5.2f} < {u['floor']} {sid:22} {key:18} {u['color']:>18} on {u['bg']}  {u['path']} — {u['text']!r}")
    if args.record:
        p = pathlib.Path(args.record)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
        print("record:", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
