"""Build a flat province-lookup PNG + draft registry from the commissioned PSD.

Pulls the ``County Colors`` layer out of the layered source file, hardens it into
a valid-by-construction region-key (one flat unique color per province, sea =
pure black), composited onto the full canvas so it is pixel-aligned with the
visual export. Also emits a draft ``europe.json`` registry the renderer +
``validate_province_map.py`` consume.

Stdlib-only (matches the project's no-Pillow map tooling). Re-run whenever the
artist redelivers the PSD.

    .venv\\Scripts\\python.exe tools/build_region_key_from_psd.py

Outputs land in ``tools/mapgen_out/`` for review before promotion to
``assets/maps/``.
"""
# Dense binary PSD/PNG codec + union-find: compact multi-statement lines are
# deliberate for locality. (This tool is outside the pre-commit ruff scope,
# which lints backend/ only; this keeps a manual `ruff check` quiet too.)
# ruff: noqa: E701, E702
from __future__ import annotations

import colorsys
import json
import struct
import zlib
from array import array
from pathlib import Path

PSD_PATH = Path("C:/Users/User/Downloads/map final1.psd")
LAYER_NAME = "County Colors"
OUT_DIR = Path("tools/mapgen_out")

# Tunables -------------------------------------------------------------------
ANCHOR_AREA_FRACTION = 0.992  # colors covering this fraction of fill are "real"
MIN_PROVINCE_PIXELS = 500     # components smaller than this are dropped to sea
SENTINEL = (0, 0, 0)

# Adjacency derivation (Slice 1) --------------------------------------------
# Inter-province gaps in the lookup are cleanly bimodal (Map Plan review pass 3:
# land <=~15px = 73.6%, sea >=41px = 23.5%). Land is auto-derived; the 16-40px
# dead zone is ignored; sea gaps are emitted as hand-review CANDIDATES only
# (decision #5: no auto sea-heuristic -- it over-connects every coast-facing pair).
DEFAULT_LAND_GAP_MAX = 15   # sentinel gap (px) <= this between two provinces => land edge
DEFAULT_SEA_GAP_MIN = 41    # gap in [SEA_MIN, SEA_MAX] => hand-review sea candidate
DEFAULT_SEA_GAP_MAX = 400   # generous window; candidates are curated by hand in Slice 2


# --- PSD parsing ------------------------------------------------------------
def _u16(b, o): return struct.unpack(">H", b[o:o + 2])[0]
def _u32(b, o): return struct.unpack(">I", b[o:o + 4])[0]


def _unpackbits(src: bytes, expected: int) -> bytes:
    out = bytearray()
    i, n = 0, len(src)
    while i < n and len(out) < expected:
        h = src[i]; i += 1
        if h >= 128:
            h -= 256
        if h >= 0:
            out += src[i:i + h + 1]; i += h + 1
        elif h != -128:
            out += bytes([src[i]]) * (1 - h); i += 1
    return bytes(out[:expected])


def extract_layer(psd: bytes, target: str):
    """Return (canvas_w, canvas_h, layer_left, layer_top, lw, lh, R, G, B, A)."""
    canvas_h, canvas_w = _u32(psd, 14), _u32(psd, 18)
    p = 26
    p += 4 + _u32(psd, p)  # color mode data
    p += 4 + _u32(psd, p)  # image resources
    _lm_len = _u32(psd, p); p += 4
    _li_len = _u32(psd, p); p += 4
    count = abs(struct.unpack(">h", psd[p:p + 2])[0]); p += 2

    records = []
    for _ in range(count):
        top, left, bottom, right = struct.unpack(">iiii", psd[p:p + 16]); p += 16
        nch = _u16(psd, p); p += 2
        chans = []
        for _c in range(nch):
            cid = struct.unpack(">h", psd[p:p + 2])[0]
            clen = _u32(psd, p + 2)
            chans.append((cid, clen)); p += 6
        p += 4 + 4 + 1 + 1 + 1 + 1  # sig+blend+opacity+clip+flags+filler
        extra_len = _u32(psd, p); p += 4; extra_end = p + extra_len
        p += 4 + _u32(psd, p)  # layer mask
        p += 4 + _u32(psd, p)  # blending ranges
        nlen = psd[p]; p += 1
        name = psd[p:p + nlen].decode("latin-1", "replace"); p += nlen
        pad = (nlen + 1) % 4
        if pad:
            p += 4 - pad
        p = extra_end
        records.append({"name": name, "box": (left, top, right, bottom), "chans": chans})

    # Channel image data follows in record order.
    for rec in records:
        total = sum(cl for _, cl in rec["chans"])
        if rec["name"] != target:
            p += total
            continue
        left, top, right, bottom = rec["box"]
        lw, lh = right - left, bottom - top
        planes = {}
        cp = p
        for cid, clen in rec["chans"]:
            comp = _u16(psd, cp)
            if comp == 0:
                raw = psd[cp + 2:cp + 2 + lw * lh]
            elif comp == 1:
                counts = struct.unpack(">%dH" % lh, psd[cp + 2:cp + 2 + lh * 2])
                rle = psd[cp + 2 + lh * 2:cp + clen]
                raw = bytearray(); off = 0
                for c in counts:
                    raw += _unpackbits(rle[off:off + c], lw); off += c
                raw = bytes(raw)
            else:
                raise SystemExit(f"channel {cid} uses unsupported compression {comp}")
            planes[cid] = raw
            cp += clen
        return (canvas_w, canvas_h, left, top, lw, lh,
                planes[0], planes[1], planes[2], planes.get(-1))
    raise SystemExit(f"layer {target!r} not found")


# --- connected components via run-length union-find -------------------------
def label_components(idx: array, W: int, H: int, sentinel_idx: int):
    parent, size = array("i"), array("i")

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if size[ra] < size[rb]:
            ra, rb = rb, ra
        parent[rb] = ra; size[ra] += size[rb]

    run_label = array("i", [0]) * 0
    all_runs = []
    prev = []
    for y in range(H):
        base = y * W
        cur = []
        x = 0
        while x < W:
            v = idx[base + x]
            if v == sentinel_idx:
                x += 1; continue
            xs = x
            while x < W and idx[base + x] == v:
                x += 1
            xe = x - 1
            lbl = len(parent)
            parent.append(lbl); size.append(xe - xs + 1)
            all_runs.append((y, xs, xe, v))
            for pxs, pxe, pv, plbl in prev:
                if pv == v and not (pxe < xs or pxs > xe):
                    union(lbl, plbl)
            cur.append((xs, xe, v, lbl))
        prev = cur
    return parent, size, all_runs, find


def main() -> int:
    psd = PSD_PATH.read_bytes()
    (W, H, lx, ly, lw, lh, R, G, B, A) = extract_layer(psd, LAYER_NAME)
    print(f"canvas {W}x{H}  layer @({lx},{ly}) {lw}x{lh}")

    # 1. histogram of opaque, non-black fill colors -> anchor palette
    from collections import Counter
    hist = Counter()
    NL = lw * lh
    for i in range(NL):
        if A and A[i] < 128:
            continue
        c = (R[i], G[i], B[i])
        if c == SENTINEL:
            continue
        hist[c] += 1
    opaque = sum(hist.values())
    anchors, cum = [], 0
    for c, n in hist.most_common():
        anchors.append(c); cum += n
        if cum >= ANCHOR_AREA_FRACTION * opaque:
            break
    print(f"opaque={opaque:,}  distinct={len(hist)}  anchors={len(anchors)}")

    # snap every distinct source color -> nearest anchor (cache: only ~211 keys)
    anchor_idx = {c: k for k, c in enumerate(anchors)}
    snap_cache = {}

    def snap(c):
        k = snap_cache.get(c)
        if k is not None:
            return k
        if c in anchor_idx:
            k = anchor_idx[c]
        else:
            best, bd = 0, 1 << 30
            cr, cg, cb = c
            for j, (ar, ag, ab) in enumerate(anchors):
                d = (cr - ar) ** 2 + (cg - ag) ** 2 + (cb - ab) ** 2
                if d < bd:
                    bd, best = d, j
            k = best
        snap_cache[c] = k
        return k

    SENT = len(anchors)  # sentinel index
    idx = array("i", [SENT]) * (W * H)
    for y in range(lh):
        for x in range(lw):
            li = y * lw + x
            if A and A[li] < 128:
                continue
            c = (R[li], G[li], B[li])
            if c == SENTINEL:
                continue
            idx[(y + ly) * W + (x + lx)] = snap(c)

    # 2. connected components (provinces split even when sharing an anchor hue)
    parent, size, all_runs, find = label_components(idx, W, H, SENT)
    roots = {}
    for ridx, (y, xs, xe, v) in enumerate(all_runs):
        r = find(ridx)
        roots.setdefault(r, [0, 0, 0])  # area, sum_x, sum_y
        roots[r][0] += xe - xs + 1
        roots[r][1] += (xs + xe) * (xe - xs + 1) // 2
        roots[r][2] += y * (xe - xs + 1)
    provinces = [(r, a, sx, sy) for r, (a, sx, sy) in roots.items() if a >= MIN_PROVINCE_PIXELS]
    provinces.sort(key=lambda t: -t[1])
    dropped = len(roots) - len(provinces)
    print(f"components={len(roots)}  provinces>={MIN_PROVINCE_PIXELS}px={len(provinces)}  dropped={dropped}")

    # 3. unique output color per province (distinct hues, never black)
    used = set()
    palette = {}
    for n, (r, a, sx, sy) in enumerate(provinces):
        hue = (n * 0.6180339887) % 1.0
        val = 0.78 + 0.20 * ((n // 12) % 2)
        rr, gg, bb = colorsys.hsv_to_rgb(hue, 0.62, val)
        col = (int(rr * 255), int(gg * 255), int(bb * 255))
        while col in used or col == SENTINEL:
            col = ((col[0] + 7) % 256, (col[1] + 13) % 256, (col[2] + 29) % 256)
        used.add(col); palette[r] = col

    root_of_run = [find(i) for i in range(len(all_runs))]
    keep = set(palette)

    # 4. paint flat canvas: provinces -> their color, everything else -> black
    rgb = bytearray(W * H * 3)  # zero-init == pure black sentinel
    for ridx, (y, xs, xe, v) in enumerate(all_runs):
        r = root_of_run[ridx]
        if r not in keep:
            continue
        col = palette[r]
        base = (y * W + xs) * 3
        for _ in range(xe - xs + 1):
            rgb[base] = col[0]; rgb[base + 1] = col[1]; rgb[base + 2] = col[2]
            base += 3

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_png(OUT_DIR / "europe_lookup.png", W, H, rgb)

    # 5. draft registry
    regions = {}
    for n, (r, a, sx, sy) in enumerate(provinces):
        cx, cy = sx // a, sy // a
        pid = f"prov_{n:03d}"
        regions[f"Region_{n:03d}"] = {
            "province_id": pid,
            "anchor": [cx, cy],
            "unit_anchor": [cx, cy],
            "label_anchor": [cx, cy],
            "garrison_anchor": [cx, cy],
            "building_anchor": [cx, cy],
            "radius": max(20, int((a / 3.14159) ** 0.5)),
            "lookup_color": list(palette[r]),
            "visual_tint": list(palette[r]),
            "is_coastal": False,
            # Smoke draft: every province renders full-color + hoverable. Real
            # wiring scope (which provinces become playable vs. grey "not yet in
            # play") is decided in the map implementation plan.
            "wired": True,
            "interactive": True,
        }
    registry = {
        "version": 2, "schema_version": 2, "padding": 140,
        "no_province_color": list(SENTINEL),
        "source": "map final1.psd :: County Colors (auto-generated draft)",
        "note": "Auto-generated smoke draft. Names are placeholders; wiring scope "
                "and real names are assigned in the map implementation plan.",
        "regions": regions,
    }
    # Slice 1: derive land adjacency + sea candidates from the freshly-painted key.
    color_keys = _rgb_bytes_to_color_keys(rgb)
    land, sea = apply_adjacency_to_registry(registry, color_keys, W, H)
    print(f"adjacency: {len(land)} land edges, {len(sea)} sea candidates")
    (OUT_DIR / "europe.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(f"wrote {OUT_DIR/'europe_lookup.png'} and {OUT_DIR/'europe.json'} ({len(regions)} regions)")
    return 0


def _write_png(path: Path, W: int, H: int, rgb: bytearray) -> None:
    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data
                + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                     + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


# --- adjacency derivation (Slice 1) -----------------------------------------
def _rgb_int(rgb) -> int:
    return (int(rgb[0]) << 16) | (int(rgb[1]) << 8) | int(rgb[2])


def _rgb_bytes_to_color_keys(rgb_bytes) -> array:
    keys = array("I")
    ap = keys.append
    for base in range(0, len(rgb_bytes), 3):
        ap((rgb_bytes[base] << 16) | (rgb_bytes[base + 1] << 8) | rgb_bytes[base + 2])
    return keys


def _scan_axis(color_keys, start, stride, count, province_keys, sentinel_key,
               land_gap_max, sea_gap_min, sea_gap_max, land, sea):
    """One scanline (row or column) of run-length adjacency detection.

    Walks maximal runs; when two DISTINCT province runs are separated only by a
    sentinel gap, classifies the gap width. An unknown (non-sentinel non-province)
    color breaks the chain so no edge is drawn across it.
    """
    prev = None; gap = 0; t = 0
    while t < count:
        k = color_keys[start + t * stride]
        j = t + 1
        while j < count and color_keys[start + j * stride] == k:
            j += 1
        if k in province_keys:
            if prev is not None and prev != k:
                a, b = (prev, k) if prev < k else (k, prev)
                if gap <= land_gap_max:
                    land.add((a, b))
                elif sea_gap_min <= gap <= sea_gap_max:
                    cur = sea.get((a, b))
                    if cur is None or gap < cur:
                        sea[(a, b)] = gap
            prev = k; gap = 0
        elif k == sentinel_key:
            gap += j - t
        else:
            prev = None; gap = 0
        t = j


def derive_adjacency(color_keys, width, height, province_keys, sentinel_key, *,
                     land_gap_max=DEFAULT_LAND_GAP_MAX,
                     sea_gap_min=DEFAULT_SEA_GAP_MIN,
                     sea_gap_max=DEFAULT_SEA_GAP_MAX):
    """Derive symmetric land adjacency + sea-gap candidates from a lookup grid.

    Horizontal + vertical scanlines cross the black moats: two distinct province
    colors separated by <= ``land_gap_max`` sentinel px are land-adjacent; a gap
    in ``[sea_gap_min, sea_gap_max]`` is emitted as a hand-review sea candidate.
    Pure function over a flat RGB-int color-key grid (unit-tested on synthetic
    lookups). Returns ``(land, sea)`` where ``land`` is a set of normalized
    ``(lo_key, hi_key)`` pairs and ``sea`` maps such a pair -> minimum gap px.
    """
    province_keys = set(province_keys)
    land: set = set()
    sea: dict = {}
    for y in range(height):
        _scan_axis(color_keys, y * width, 1, width, province_keys, sentinel_key,
                   land_gap_max, sea_gap_min, sea_gap_max, land, sea)
    for x in range(width):
        _scan_axis(color_keys, x, width, height, province_keys, sentinel_key,
                   land_gap_max, sea_gap_min, sea_gap_max, land, sea)
    # A pair seen as land on ANY axis is land, never a sea candidate.
    for pair in list(sea):
        if pair in land:
            del sea[pair]
    return land, sea


def apply_adjacency_to_registry(registry, color_keys, width, height, *,
                                land_gap_max=DEFAULT_LAND_GAP_MAX,
                                sea_gap_min=DEFAULT_SEA_GAP_MIN,
                                sea_gap_max=DEFAULT_SEA_GAP_MAX):
    """Derive adjacency from ``color_keys`` and write it into ``registry`` in place.

    Adds a sorted ``adjacent`` list to every region, a top-level ``sea_candidates``
    list (hand-curated in Slice 2), and an ``adjacency_derivation`` metadata block.
    """
    sentinel_key = _rgb_int(registry["no_province_color"])
    key_to_region = {_rgb_int(e["lookup_color"]): name
                     for name, e in registry["regions"].items()}
    land, sea = derive_adjacency(
        color_keys, width, height, set(key_to_region), sentinel_key,
        land_gap_max=land_gap_max, sea_gap_min=sea_gap_min, sea_gap_max=sea_gap_max)

    adj = {name: set() for name in registry["regions"]}
    for a, b in land:
        na, nb = key_to_region[a], key_to_region[b]
        adj[na].add(nb); adj[nb].add(na)
    for name, entry in registry["regions"].items():
        entry["adjacent"] = sorted(adj[name])

    sea_candidates = []
    for (a, b), g in sea.items():
        na, nb = key_to_region[a], key_to_region[b]
        lo, hi = (na, nb) if na < nb else (nb, na)
        sea_candidates.append({"a": lo, "b": hi, "gap": g})
    sea_candidates.sort(key=lambda d: (d["a"], d["b"]))
    registry["sea_candidates"] = sea_candidates
    registry["adjacency_derivation"] = {
        "land_gap_max": land_gap_max,
        "sea_gap_min": sea_gap_min,
        "sea_gap_max": sea_gap_max,
        "land_edges": len(land),
        "sea_candidates": len(sea_candidates),
    }
    return land, sea


def rederive_adjacency(registry_path, lookup_path, **gaps):
    """Re-derive adjacency into an existing registry from its lookup PNG.

    The cheap path: no PSD, no PNG rewrite -- just reads the flat region-key and
    injects ``adjacent`` / ``sea_candidates`` into the registry JSON in place.
    """
    try:
        from tools.validate_province_map import read_png_rgb_bytes
    except ImportError:  # direct `python tools/...` run: tools/ is sys.path[0]
        from validate_province_map import read_png_rgb_bytes
    registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    w, h, rgb_bytes = read_png_rgb_bytes(Path(lookup_path))
    color_keys = _rgb_bytes_to_color_keys(rgb_bytes)
    land, sea = apply_adjacency_to_registry(registry, color_keys, w, h, **gaps)
    Path(registry_path).write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(f"adjacency: {len(land)} land edges, {len(sea)} sea candidates "
          f"-> {registry_path}")
    return registry


# --- letters-layer inspection (Slice 1 naming seed for Slice 2) --------------
def list_layer_names(psd: bytes) -> list:
    """Return the PSD layer names in record order (header walk, no pixel data)."""
    p = 26
    p += 4 + _u32(psd, p)  # color mode data
    p += 4 + _u32(psd, p)  # image resources
    p += 4  # layer+mask length
    p += 4  # layer info length
    count = abs(struct.unpack(">h", psd[p:p + 2])[0]); p += 2
    names = []
    for _ in range(count):
        p += 16  # rect
        nch = _u16(psd, p); p += 2
        p += nch * 6
        p += 4 + 4 + 1 + 1 + 1 + 1  # sig+blend+opacity+clip+flags+filler
        extra_len = _u32(psd, p); p += 4; extra_end = p + extra_len
        p += 4 + _u32(psd, p)  # layer mask
        p += 4 + _u32(psd, p)  # blending ranges
        nlen = psd[p]; p += 1
        names.append(psd[p:p + nlen].decode("latin-1", "replace")); p += nlen
        pad = (nlen + 1) % 4
        if pad:
            p += 4 - pad
        p = extra_end
    return names


def inspect_letters(psd_path=PSD_PATH, out_dir=OUT_DIR) -> int:
    """Dump the ``letters`` layer as a white-composited crop PNG naming seed.

    Investigative (Slice 1): the layer is rasterized single-character glyphs, not
    province names -- a weak initial-letter hint for the Slice 2 geography pass.
    """
    psd = psd_path.read_bytes()
    names = list_layer_names(psd)
    target = next((nm for nm in names if "letter" in nm.lower()), None)
    if target is None:
        print("no 'letters' layer found. available layers:")
        for nm in names:
            print("   ", nm)
        return 1
    (W, H, lx, ly, lw, lh, R, G, B, A) = extract_layer(psd, target)
    print(f"letters layer {target!r} @({lx},{ly}) {lw}x{lh}")
    rgb = bytearray(b"\xff" * (lw * lh * 3))  # white background
    for i in range(lw * lh):
        a = A[i] if A else 255
        if a == 0:
            continue
        f = a / 255.0
        inv = 255 * (1.0 - f)
        rgb[i * 3] = int(R[i] * f + inv)
        rgb[i * 3 + 1] = int(G[i] * f + inv)
        rgb[i * 3 + 2] = int(B[i] * f + inv)
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_png(out_dir / "letters_layer.png", lw, lh, rgb)
    print(f"wrote {out_dir / 'letters_layer.png'} -- naming seed for Slice 2 "
          f"(rasterized single glyphs, NOT province names)")
    return 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        prog="build_region_key_from_psd",
        description="Build the province lookup+registry from the PSD, or "
                    "(re)derive adjacency / inspect the letters layer.")
    ap.add_argument("--adjacency-only", action="store_true",
                    help="Re-derive adjacency into an existing registry from its "
                         "lookup PNG (no PSD, no PNG rewrite).")
    ap.add_argument("--inspect-letters", action="store_true",
                    help="Dump the PSD letters layer as a Slice-2 naming seed.")
    ap.add_argument("--registry", default=str(OUT_DIR / "europe.json"))
    ap.add_argument("--lookup", default=str(OUT_DIR / "europe_lookup.png"))
    ap.add_argument("--land-gap-max", type=int, default=DEFAULT_LAND_GAP_MAX)
    ap.add_argument("--sea-gap-min", type=int, default=DEFAULT_SEA_GAP_MIN)
    ap.add_argument("--sea-gap-max", type=int, default=DEFAULT_SEA_GAP_MAX)
    args = ap.parse_args()

    if args.inspect_letters:
        raise SystemExit(inspect_letters())
    if args.adjacency_only:
        rederive_adjacency(args.registry, args.lookup,
                           land_gap_max=args.land_gap_max,
                           sea_gap_min=args.sea_gap_min,
                           sea_gap_max=args.sea_gap_max)
        raise SystemExit(0)
    raise SystemExit(main())
