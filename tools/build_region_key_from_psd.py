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


if __name__ == "__main__":
    raise SystemExit(main())
