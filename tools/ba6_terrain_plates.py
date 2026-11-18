"""Row BA, BA-6 — the ground on the table, from real period surveys.

The user (November 17, 2026): "make sure the terrain background does not look
ai genned even get assets if needed". BA-5 drew the ground in code on the felt
(see-through triangles for mountains, domes for hills, a patchwork of soft
rectangles for fields) and it read as generated. This tool builds the ground
from REAL hand-drawn military surveys of the period instead — each a crop of a
public-domain scan, graded "by lamplight" into the felt's own dark range so the
engraver's lines show while every caption the table sets over them keeps its
contrast:

    plains / forest / hills / urban / river_crossing
        Joseph de Ferraris, Carte de cabinet des Pays-Bas autrichiens
        (1771-78), the hand-coloured Austrian military survey of the very
        country the armies of 1792-1815 marched over (KBR scans, Wikimedia
        Commons, public domain)
    mountains
        Peter Anich and Blasius Hueber, Atlas Tyrolensis (1774), the engraved
        survey of the Tyrol (Wikimedia Commons, public domain)
A fleet action keeps its chart-blue table: the only period charts found were
Gallica/BnF scans, which the project's licence policy refuses
(THIRD_PARTY_LICENSES.md).

No pixel is generated: every line on a plate was drawn by a surveyor or an
engraver between 1771 and 1778; the tool crops, scales and grades them. The
sources are Wikimedia Commons' standard 1920-px renderings of the scans (the
full scans were out of reach: Commons rate-limited the session), so a crop is
about 1,000 px — about 1 : 1 on the 948-px stage at the shipped size.

    .venv/Scripts/python.exe -I tools/ba6_terrain_plates.py <sources dir> [--out DIR]

The sources dir holds the scans under the file names of SOURCES (download them
from the page URLs below; any resolution — the plates are 1896x880, twice the
stage). It writes the plates as JPEG into the out dir (default the client's
assets/textures/battle/) with `plates.json` (source, crop, licence of each).
Pillow and numpy only.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np
from PIL import Image, ImageFilter

Image.MAX_IMAGE_PIXELS = None

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "godot-client" / "project-sovereign" / "assets" / "textures" / "battle"
SIZE = (1896, 880)            # twice the stage's 948 x 440

FERRARIS = "Joseph de Ferraris, Carte de cabinet des Pays-Bas autrichiens (1771-78), KBR"
SOURCES = {
    "mons": {"file": "ferraris_mons.jpg", "commons": "Mons, par Joseph de Ferraris, KBR.jpg",
             "work": FERRARIS},
    "huy": {"file": "ferraris_huy.jpg", "commons": "Huy, par Joseph de Ferraris, KBR.jpg",
            "work": FERRARIS},
    "liege": {"file": "ferraris_liege.jpg", "commons": "Liège, par Joseph de Ferraris, KBR.jpg",
              "work": FERRARIS},
    "tintigny": {"file": "ferraris_tintigny.jpg", "commons": "Tintigny, par Joseph de Ferraris, KBR.jpg",
                 "work": FERRARIS},
    "namur": {"file": "ferraris_namur.jpg", "commons": "Namur, par Joseph de Ferraris, KBR.jpg",
              "work": FERRARIS},
    "hannut": {"file": "ferraris_hannut.jpg", "commons": "Hannut, par Joseph de Ferraris, KBR.jpg",
               "work": FERRARIS},
    "anich": {"file": "anich_atlas_tyrolensis_1.jpg", "commons": "Atlas Tyrolensis-1.jpg",
              "work": "Peter Anich and Blasius Hueber, Atlas Tyrolensis (1774)"},
}

# Each plate: the ground kind it serves, its source, the crop as FRACTIONS of
# the whole sheet (x0, y0, x1, y1 — at the stage's 2.15 : 1 on the sheet's own
# pixels), the grade, and — for a kind whose feature lies on ONE half — the
# half it lies on (`side`): a wood or a town is the defender's ground, so the
# client lays the plate whose feature is on his half. Open country, hills,
# mountains and a river span the table and serve either side. A plate is never
# mirrored: a survey's lettering would read backwards. Crops avoid the sheets'
# big lettering, borders and scale bars; the fold of their four joined
# quarters is the map's own and may cross a plate.
PLATES = [
    {"name": "plains_1", "kind": "plains", "source": "mons", "crop": (0.600, 0.235, 0.957, 0.495), "grade": "survey"},
    {"name": "plains_2", "kind": "plains", "source": "hannut", "crop": (0.220, 0.300, 0.600, 0.578), "grade": "survey"},
    {"name": "plains_3", "kind": "plains", "source": "tintigny", "crop": (0.560, 0.640, 0.940, 0.917), "grade": "survey"},
    {"name": "forest_1", "kind": "forest", "side": "right", "source": "huy", "crop": (0.590, 0.640, 0.985, 0.928),
     "grade": "survey"},
    {"name": "forest_2", "kind": "forest", "side": "left", "source": "tintigny", "crop": (0.020, 0.640, 0.400, 0.917),
     "grade": "survey"},
    {"name": "hills_1", "kind": "hills", "source": "liege", "crop": (0.520, 0.490, 0.900, 0.768), "grade": "survey"},
    {"name": "hills_2", "kind": "hills", "source": "tintigny", "crop": (0.560, 0.040, 0.940, 0.317), "grade": "survey"},
    {"name": "mountains_1", "kind": "mountains", "source": "anich", "crop": (0.300, 0.520, 0.960, 0.819), "grade": "engraving"},
    {"name": "mountains_2", "kind": "mountains", "source": "anich", "crop": (0.080, 0.300, 0.740, 0.599), "grade": "engraving"},
    {"name": "urban_1", "kind": "urban", "side": "right", "source": "namur", "crop": (0.420, 0.380, 0.800, 0.657),
     "grade": "survey"},
    {"name": "urban_2", "kind": "urban", "side": "left", "source": "namur", "crop": (0.600, 0.370, 0.980, 0.647),
     "grade": "survey"},
    {"name": "river_crossing_1", "kind": "river_crossing", "source": "namur", "crop": (0.540, 0.490, 0.920, 0.767),
     "grade": "survey"},
]

# The table's palette (linear light): the felt the plates are laid on, and the
# inks the grades lean toward. The felt is Utils.UI_DIORAMA_BAIZE.
FELT = np.array([0.129, 0.208, 0.153]) ** 2.2
SEPIA_GREEN = np.array([0.22, 0.26, 0.17]) ** 2.2
SEA = np.array([0.098, 0.153, 0.216]) ** 2.2

# The lamplight: paper reads at Y1, the engraver's darkest ink at Y0 (linear
# luminance). The ceiling keeps crimson (d7635e, the tightest ink) at 3 to 1 over the
# brightest common paper and bone (c9c2b2) and gold (d9c08c) at 6 to 1 — the captions
# the table sets on the sheet — and the vignette darkens the corners and the band where
# the day's title and its toll stand.
Y0, Y1, GAMMA = 0.008, 0.048, 1.15
GRADES = {
    "survey": {"keep": 0.70, "lean": SEPIA_GREEN, "lean_by": 0.22},
    "engraving": {"keep": 0.0, "lean": SEPIA_GREEN, "lean_by": 1.0},
    "chart": {"keep": 0.25, "lean": SEA, "lean_by": 0.65},
}


def _linear(rgb: np.ndarray) -> np.ndarray:
    return np.clip(rgb, 0.0, 1.0) ** 2.2


def _srgb(lin: np.ndarray) -> np.ndarray:
    return np.clip(lin, 0.0, 1.0) ** (1.0 / 2.2)


def _luma(lin: np.ndarray) -> np.ndarray:
    return lin[..., 0] * 0.2126 + lin[..., 1] * 0.7152 + lin[..., 2] * 0.0722


def crop_of(im: Image.Image, frac) -> Image.Image:
    w, h = im.size
    x0, y0, x1, y1 = frac
    return im.crop((int(round(x0 * w)), int(round(y0 * h)), int(round(x1 * w)), int(round(y1 * h))))


def grade(im: Image.Image, how: str) -> Image.Image:
    """The lamplight: the sheet's own tone mapped into [Y0, Y1], its colour
    kept in part and leant toward the table's ink, a vignette over all."""
    g = GRADES[how]
    rgb = np.asarray(im.convert("RGB"), dtype=np.float64) / 255.0
    lin = _linear(rgb)
    y = _luma(lin)
    paper, ink = np.percentile(y, 92), np.percentile(y, 3)
    tone = np.clip((y - ink) / max(1e-6, paper - ink), 0.0, 1.0) ** GAMMA
    target = Y0 + (Y1 - Y0) * tone
    # the colour: the sheet's own chroma (each pixel at unit luminance), kept
    # at `keep` against grey, then leant toward the grade's ink
    chroma = lin / np.maximum(y, 1e-4)[..., None]
    chroma = 1.0 + (chroma - 1.0) * g["keep"]
    lean = g["lean"] / max(1e-6, float(_luma(g["lean"][None, None, :])[0, 0]))
    chroma = chroma * (1.0 - g["lean_by"]) + lean[None, None, :] * g["lean_by"]
    out = chroma * target[..., None]
    out *= (target / np.maximum(_luma(out), 1e-6))[..., None]      # luminance exactly the target
    # the vignette: corners to 72 %, the upper band (title and toll) to 86 %
    h, w = y.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / np.sqrt(2)
    vignette = 1.0 - 0.28 * np.clip(r, 0.0, 1.0) ** 1.6
    band = 1.0 - 0.14 * np.clip(1.0 - yy / (0.32 * h), 0.0, 1.0)
    out *= (vignette * band)[..., None]
    return Image.fromarray((_srgb(out) * 255.0 + 0.5).astype(np.uint8), "RGB")


FELT_SOURCE = {"file": "Fabric034_1K-JPG_Color.jpg",
               "work": "ambientCG, Fabric034 (felt), photographed fabric",
               "licence": "CC0 1.0 (public domain)", "page": "https://ambientcg.com/a/Fabric034"}


def felt(src_dir: pathlib.Path, out_dir: pathlib.Path) -> dict:
    """The baize under the sheet: a photographed felt (ambientCG Fabric034,
    CC0), its nap kept at under half its contrast and laid on the table's own
    green (Utils.UI_DIORAMA_BAIZE). Seamless: 1024 -> 512 keeps the tile."""
    path = src_dir / FELT_SOURCE["file"]
    if not path.exists():
        print(f"skip felt: no {path.name} in {src_dir}")
        return {}
    im = Image.open(path).convert("RGB").resize((512, 512), Image.LANCZOS)
    lin = _linear(np.asarray(im, dtype=np.float64) / 255.0)
    y = _luma(lin)
    nap = 1.0 + (y / max(1e-6, float(y.mean())) - 1.0) * 0.45
    out = FELT[None, None, :] * nap[..., None]
    dest = out_dir / "felt_baize.jpg"
    Image.fromarray((_srgb(out) * 255.0 + 0.5).astype(np.uint8), "RGB").save(
        dest, "JPEG", quality=90, optimize=True)
    print(f"wrote {dest.name} (from {path.name})")
    return {"file": dest.name, **FELT_SOURCE}


def build(src_dir: pathlib.Path, out_dir: pathlib.Path, only=None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    record = {"_note": ("Row BA, BA-6: the ground on the table, cut from period surveys and charts "
                        "(public domain scans, Wikimedia Commons) by tools/ba6_terrain_plates.py. "
                        "A wood's or a town's plate has its feature on one half (`side`); the client "
                        "lays the plate whose feature lies on the defender's half, never a mirror."),
              "size": list(SIZE), "plates": {}}
    for plate in PLATES:
        if only and plate["name"] not in only:
            continue
        source = SOURCES[plate["source"]]
        path = src_dir / source["file"]
        if not path.exists():
            print(f"skip {plate['name']}: no {path.name} in {src_dir}")
            continue
        im = Image.open(path)
        cut = crop_of(im, plate["crop"])
        if plate.get("flip"):
            cut = cut.transpose(Image.FLIP_LEFT_RIGHT)
        cut = cut.convert("RGB").resize(SIZE, Image.LANCZOS)
        # a little of the scan's own grain survives the downscale; a faint
        # unsharp mask keeps the engraver's line at the stage's size
        cut = cut.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
        plate_im = grade(cut, plate["grade"])
        dest = out_dir / f"{plate['name']}.jpg"
        plate_im.save(dest, "JPEG", quality=88, optimize=True, progressive=True)
        record["plates"][plate["name"]] = {
            "kind": plate["kind"], "side": plate.get("side", "both"), "file": dest.name,
            "source": source["commons"],
            "work": source["work"], "crop": list(plate["crop"]), "flip": bool(plate.get("flip")),
            "grade": plate["grade"], "source_pixels": list(im.size),
            "licence": "Public domain (PD-old / PD-Art), Wikimedia Commons",
            "page": "https://commons.wikimedia.org/wiki/File:" + source["commons"].replace(" ", "_"),
        }
        print(f"wrote {dest.name}  ({plate['kind']}, from {source['file']} {im.size}, crop {plate['crop']})")
    if not only or "felt" in only:
        made = felt(src_dir, out_dir)
        if made:
            record["felt"] = made
    (out_dir / "plates.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n",
                                         encoding="utf-8")
    return record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = [n for n in args.only.split(",") if n]
    build(pathlib.Path(args.sources), pathlib.Path(args.out), only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
