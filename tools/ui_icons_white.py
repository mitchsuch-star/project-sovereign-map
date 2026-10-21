"""The curated UI glyphs as white silhouettes (EA-E2, SF-RR5, October 21, 2026).

    .venv/Scripts/python.exe tools/ui_icons_white.py           # report
    .venv/Scripts/python.exe tools/ui_icons_white.py --write   # preprocess

Every road the client draws a curated glyph by TINTS it — a button's
`icon_*_color` (a gold chip, the notice rail's white pill silhouette), a
BBCode `[img color=…]` (`Utils.bb_icon`, a category hue). A tint multiplies,
so the source must be WHITE: UI-3 (July 12, 2026) preprocessed the ten glyphs
it used and later sessions drew forty more raw. Two raw forms draw black:

  * Phosphor's `currentColor`, which the SVG importer resolves to black —
    the map's zoom chips, the rail's glyphs, the log's sword / flag / coins,
    the Generals' audience chip;
  * game-icons.net's 512-px black background square
    (`<path d="M0 0h512v512H0z"/>`) — the Generals' Reward chip drew a black
    box round its glyph.

`--write` replaces `currentColor` with `#ffffff` and strips the square (its
glyph paths already carry `fill="#fff"`). Godot re-imports a changed SVG on
the next `--import` pass or editor launch. Pinned by
`tests/test_sf_rr5_the_frames.py::TestEAE2EveryGlyphIsAWhiteSilhouette`.
"""
from __future__ import annotations

import argparse
import pathlib

ICONS = (pathlib.Path(__file__).resolve().parents[1]
         / "godot-client" / "project-sovereign" / "assets" / "ui" / "icons")
BLACK_SQUARE = '<path d="M0 0h512v512H0z"/>'


def raw(path: pathlib.Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    why = []
    if "currentColor" in text:
        why.append("currentColor")
    if BLACK_SQUARE in text:
        why.append("black square")
    return why


def whiten(text: str) -> str:
    return text.replace("currentColor", "#ffffff").replace(BLACK_SQUARE, "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    found = [(p, raw(p)) for p in sorted(ICONS.glob("*/*.svg"))]
    found = [(p, why) for p, why in found if why]
    for p, why in found:
        print(f"{p.parent.name}/{p.name}: {', '.join(why)}")
        if args.write:
            # newline="" keeps each file's own line endings
            text = p.read_text(encoding="utf-8")
            p.write_text(whiten(text), encoding="utf-8", newline="")
    print(f"{len(found)} raw glyph(s){' whitened' if args.write and found else ''}")
    return 1 if found and not args.write else 0


if __name__ == "__main__":
    raise SystemExit(main())
