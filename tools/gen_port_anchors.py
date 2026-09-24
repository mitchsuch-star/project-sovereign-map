"""NUI-2 "The Fleet Rides at Anchor" — derive each coastal province's
`port_anchor` from the painted map, and audit `is_coastal` against the art.

WHY THIS EXISTS (Sept 24, 2026). The live review found Holland's dockyard,
Amsterdam, drawn inland; the audit that followed found France's Channel yard
(Flanders) and Russia's only yard (the province named Estonia) inland too, and
every fleet piece drawn at its province's CENTRE — Russia's 260 px from the
nearest water. A fleet belongs on the water off its own coast.

WHAT IT READS
  europe_lookup.png   province colours; black (0,0,0) = no province
  europe_visual.png   the painted map; sea is grey-blue paint (R-B < 45),
                      land and the unmapped rim are tan (R-B ~60-75)
  europe.json         the registry this tool writes `port_anchor` into

WHAT "SEA" MEANS HERE
  water  = black in the lookup AND sea-coloured paint in the visual
  sea    = the water bodies of at least SEA_BODY_MIN_PX pixels. On the shipped
           art that is exactly one body (the connected ocean, the Baltic, the
           Mediterranean and the Black Sea, 1.54M px); the next largest is 246 px
           (the lake pocket behind the province named Estonia). Everything
           smaller is a lake or a speck.
  a province is ART-COASTAL when at least MIN_CONTACT_PX of its pixels lie
  within TOUCH_R px of the sea (the lookup stops a pixel or two short of the
  painted shoreline, so contact is measured across that gap).

WHAT IT WRITES
  `port_anchor` [x, y] on every `is_coastal` province: the base of the fleet
  piece, on open water off that province's own shore — the nearest province to
  the point is the province itself, the point is at most MAX_OFFSHORE px out,
  and the whole piece (hull, sail count and the blockade glyph beside it) fits
  on water. Among the points that qualify, the one nearest the province's
  anchor wins, weighted to hug the coast. Deterministic: the same art gives
  the same anchors, byte for byte.

USAGE (dev-only, Pillow + numpy — not in requirements, like
tools/gen_war_table_pieces.py; the suite pins the RESULT with the stdlib PNG
decoder in tools/validate_province_map.py and never runs this):

    .venv\\Scripts\\python.exe -m tools.gen_port_anchors --audit
    .venv\\Scripts\\python.exe -m tools.gen_port_anchors --write
    .venv\\Scripts\\python.exe -m tools.gen_port_anchors --check
    .venv\\Scripts\\python.exe -m tools.gen_port_anchors --preview out.png

`--audit` prints every province whose flag disagrees with the art, every
dockyard, camp and sea-link end that does not touch the sea, and exits 1 on
any disagreement not recorded in ART_EXCEPTIONS. `--check` also exits 1 when
the registry's anchors differ from what the art derives. Never touches
adjacency (never re-run build_region_key_from_psd.py --adjacency-only).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
MAPS = REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
REGISTRY = MAPS / "europe.json"
SCENARIO = MAPS / "europe_1805.json"
LOOKUP = MAPS / "europe_lookup.png"
VISUAL = MAPS / "europe_visual.png"

SEA_RB_MAX = 45          # painted sea is R-B ~10-30; land/rim ~60-75
SEA_BODY_MIN_PX = 5000   # a smaller body is a lake or a speck
TOUCH_R = 4              # contact is measured across the lookup's shore gap
MIN_CONTACT_PX = 100     # fewer = a corner touch, not a coast. The shipped
                         # art has a clean gap: Wessex 29 px and Volhynia
                         # 50 px (a pinpoint where three borders meet the
                         # water), then the first real coast at 236 px.
MAX_OFFSHORE = 40        # the anchor lies at most this far off its own shore

# The fleet piece, relative to its base (the anchor): the hull and sail count
# rise above it, the blockade glyph sits to its right (map_renderer_base.gd
# FLEET_PIECE_* / PORT_GLYPH_BESIDE_SHIP). The first box that fits wins.
PIECE_BOXES: List[Tuple[int, int, int, int]] = [
    (-18, 33, -36, 4),   # hull + sail count + glyph beside it
    (-14, 28, -30, 3),   # a narrower water: the piece's core
    (-8, 8, -12, 2),     # a strait: at least the base on water
]
COAST_WEIGHT = 2.0       # score = |P - anchor| + COAST_WEIGHT * offshore
MIN_SEPARATION = 40      # px between two provinces' anchors (a ship is 36 wide)

# Provinces where the flag deliberately disagrees with the art. Each carries
# its reason; `--audit` fails on any disagreement not listed here, and the
# suite pins this list (tests/test_nui2_the_fleet_rides_at_anchor.py).
_DEF8 = ("DEF-8 (July 2, 2026): the stylised art carries the Adriatic north to "
         "the Alpine provinces; the flag follows the real, landlocked place")
ART_EXCEPTIONS: Dict[str, str] = {
    "Bern": _DEF8,
    "Franche-Comte": _DEF8,
    "Milan": _DEF8,
    "Munich": _DEF8,
    "Tyrol": _DEF8,
    "Estonia": (
        "DEF-7 (July 2, 2026) made Finland-Estonia the Gulf of Finland "
        "crossing, and rule G3 (tools/validate_province_map.py) keeps a "
        "sea-link end coastal. The art gives Estonia a lake pocket, not a "
        "shore, so it hosts no yard and no fleet stands off it: Russia's "
        "Baltic yard is Livonia (Riga)."),
}


def _need_imaging():
    try:
        import numpy  # noqa: F401
        from PIL import Image  # noqa: F401
    except ImportError:  # pragma: no cover - dev-only tool
        sys.exit("gen_port_anchors needs Pillow + numpy (dev-only): "
                 "pip install pillow numpy")


def load_art():
    """(key, sea, contact_ok) arrays: the lookup colour key per pixel, the
    open-sea mask, and the shore-contact mask (within TOUCH_R of the sea)."""
    import numpy as np
    from PIL import Image

    look = np.array(Image.open(LOOKUP).convert("RGB")).astype(np.int64)
    vis = np.array(Image.open(VISUAL).convert("RGB")).astype(np.int64)
    key = (look[..., 0] << 16) | (look[..., 1] << 8) | look[..., 2]
    water = (key == 0) & ((vis[..., 0] - vis[..., 2]) < SEA_RB_MAX)
    sea = _big_bodies(water, SEA_BODY_MIN_PX)
    near = _dilate(sea, TOUCH_R)
    return key, sea, near


def _big_bodies(mask, min_px: int):
    """The 4-connected components of `mask` of at least `min_px` pixels —
    run-length union-find, one pass over the rows."""
    import numpy as np

    height = mask.shape[0]
    parent: List[int] = []

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    runs: List[Tuple[int, int, int, int]] = []
    prev: List[Tuple[int, int, int]] = []
    for y in range(height):
        row = mask[y].astype(np.int8)
        d = np.diff(np.concatenate(([0], row, [0])))
        starts = np.flatnonzero(d == 1).tolist()
        ends = np.flatnonzero(d == -1).tolist()
        cur = []
        for x0, x1 in zip(starts, ends):
            rid = len(parent)
            parent.append(rid)
            cur.append((x0, x1, rid))
            runs.append((y, x0, x1, rid))
        i = j = 0
        while i < len(prev) and j < len(cur):
            a0, a1, aid = prev[i]
            b0, b1, bid = cur[j]
            if a0 < b1 and b0 < a1:
                ra, rb = find(aid), find(bid)
                if ra != rb:
                    parent[max(ra, rb)] = min(ra, rb)
            if a1 < b1:
                i += 1
            else:
                j += 1
        prev = cur
    area: Dict[int, int] = {}
    for _y, x0, x1, rid in runs:
        root = find(rid)
        area[root] = area.get(root, 0) + (x1 - x0)
    keep = {root for root, px in area.items() if px >= min_px}
    out = np.zeros_like(mask)
    for y, x0, x1, rid in runs:
        if find(rid) in keep:
            out[y, x0:x1] = True
    return out


def _shift(mask, dy: int, dx: int):
    import numpy as np

    h, w = mask.shape
    out = np.zeros_like(mask)
    ys = slice(max(dy, 0), h + min(dy, 0))
    yd = slice(max(-dy, 0), h + min(-dy, 0))
    xs = slice(max(dx, 0), w + min(dx, 0))
    xd = slice(max(-dx, 0), w + min(-dx, 0))
    out[ys, xs] = mask[yd, xd]
    return out


def _dilate(mask, r: int):
    out = mask.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dy * dy + dx * dx <= r * r:
                out |= _shift(mask, dy, dx)
    return out


def _grow(seed, iterations: int):
    """Octagonal distance from `seed`, capped at `iterations` (alternating
    the 4- and 8-neighbourhoods approximates the Euclidean circle)."""
    import numpy as np

    dist = np.full(seed.shape, np.inf)
    dist[seed] = 0.0
    front = seed.copy()
    reached = seed.copy()
    for step in range(1, iterations + 1):
        nxt = (_shift(front, 1, 0) | _shift(front, -1, 0)
               | _shift(front, 0, 1) | _shift(front, 0, -1))
        if step % 2 == 0:
            nxt |= (_shift(front, 1, 1) | _shift(front, 1, -1)
                    | _shift(front, -1, 1) | _shift(front, -1, -1))
        nxt &= ~reached
        dist[nxt] = float(step)
        reached |= nxt
        front = nxt
        if not front.any():
            break
    return dist


def _box_clear(sea, box: Tuple[int, int, int, int]):
    """clear[y, x] = every pixel of `box` placed at (x, y) is sea."""
    import numpy as np

    x0, x1, y0, y1 = box
    land = (~sea).astype(np.int32)
    h, w = land.shape
    integral = np.zeros((h + 1, w + 1), dtype=np.int64)
    integral[1:, 1:] = land.cumsum(0).cumsum(1)
    ys = np.arange(h)
    xs = np.arange(w)
    ya = np.clip(ys + y0, 0, h)
    yb = np.clip(ys + y1 + 1, 0, h)
    xa = np.clip(xs + x0, 0, w)
    xb = np.clip(xs + x1 + 1, 0, w)
    total = (integral[yb][:, xb] - integral[ya][:, xb]
             - integral[yb][:, xa] + integral[ya][:, xa])
    inside = ((ys + y0 >= 0) & (ys + y1 < h))[:, None] & \
             ((xs + x0 >= 0) & (xs + x1 < w))[None, :]
    clear = (total == 0) & inside & sea
    return clear


def coast_contact(key, near, regions: dict) -> Dict[str, int]:
    """Province pixels within TOUCH_R of the open sea, per province NAME."""
    import numpy as np

    colour_to_name = {}
    for entry in regions.values():
        c = entry["lookup_color"]
        colour_to_name[(c[0] << 16) | (c[1] << 8) | c[2]] = entry["name"]
    touching = key[near & (key != 0)]
    values, counts = np.unique(touching, return_counts=True)
    contact = {name: 0 for name in colour_to_name.values()}
    for value, count in zip(values.tolist(), counts.tolist()):
        name = colour_to_name.get(int(value))
        if name is not None:
            contact[name] = int(count)
    return contact


def port_candidates(key, clear_by_box, entry: dict):
    """Per piece-box level, the qualifying bases off `entry`'s shore as
    (xs, ys, scores) sorted best-first — empty lists when the province does
    not reach the open sea at all."""
    import numpy as np

    c = entry["lookup_color"]
    colour = (c[0] << 16) | (c[1] << 8) | c[2]
    own = key == colour
    ys, xs = np.nonzero(own)
    levels = []
    if ys.size == 0:
        return levels
    pad = MAX_OFFSHORE + 40
    h, w = key.shape
    y0, y1 = max(0, int(ys.min()) - pad), min(h, int(ys.max()) + pad + 1)
    x0, x1 = max(0, int(xs.min()) - pad), min(w, int(xs.max()) + pad + 1)
    sub_key = key[y0:y1, x0:x1]
    sub_own = own[y0:y1, x0:x1]
    sub_other = (sub_key != 0) & ~sub_own
    d_own = _grow(sub_own, MAX_OFFSHORE + 1)
    d_other = _grow(sub_other, MAX_OFFSHORE + 1)
    ours = (d_own <= MAX_OFFSHORE) & (d_own < d_other)
    ax, ay = entry["anchor"]
    for clear in clear_by_box:
        cand = clear[y0:y1, x0:x1] & ours
        cy, cx = np.nonzero(cand)
        gx, gy = cx + x0, cy + y0
        score = (np.hypot(gx - ax, gy - ay)
                 + COAST_WEIGHT * d_own[cy, cx])
        # Deterministic order: lowest score, then y, then x.
        order = np.lexsort((gx, gy, score))
        levels.append((gx[order], gy[order], score[order]))
    return levels


def place_anchors(candidates: Dict[str, list], first=frozenset()):
    """Greedy placement with spacing: the provinces in `first` (the shipped
    scenario's dockyards — the anchors a fleet piece or a blockade glyph is
    actually drawn at) choose before the rest; within each group the province
    with the fewest places to moor chooses first (then by name —
    deterministic), and each keeps at least MIN_SEPARATION px from every
    anchor already placed, trying the widest piece box first. A province with
    no spaced place left takes its best place and is reported as CROWDED
    (never silently)."""
    import numpy as np

    def room(name: str) -> int:
        levels = candidates[name]
        return sum(int(lv[0].size) for lv in levels)

    placed: Dict[str, List[int]] = {}
    crowded: List[str] = []
    for name in sorted(candidates,
                       key=lambda n: (n not in first, room(n), n)):
        levels = candidates[name]
        if not any(lv[0].size for lv in levels):
            continue
        chosen = None
        taken = np.array(list(placed.values()), dtype=float).reshape(-1, 2)
        for gx, gy, _score in levels:
            if gx.size == 0:
                continue
            if taken.size:
                dx = gx[:, None] - taken[None, :, 0]
                dy = gy[:, None] - taken[None, :, 1]
                spaced = (np.hypot(dx, dy) >= MIN_SEPARATION).all(axis=1)
            else:
                spaced = np.ones(gx.size, dtype=bool)
            idx = np.flatnonzero(spaced)
            if idx.size:
                chosen = [int(gx[idx[0]]), int(gy[idx[0]])]
                break
        if chosen is None:
            for gx, gy, _score in levels:
                if gx.size:
                    chosen = [int(gx[0]), int(gy[0])]
                    crowded.append(name)
                    break
        placed[name] = chosen
    return placed, crowded


def scenario_dockyards(scenario: dict) -> frozenset:
    """Every dockyard the scenario authors, any nation."""
    yards = set()
    for rec in (scenario.get("navies") or {}).values():
        if isinstance(rec, dict):
            yards.update(str(p) for p in rec.get("dockyards") or [])
    return frozenset(yards)


def derive_all(registry: dict, scenario: Optional[dict] = None):
    """({name: port_anchor}, {name: contact_px}, [crowded]) for the registry.
    The scenario's dockyards moor first (`place_anchors`)."""
    key, sea, near = load_art()
    regions = registry["regions"]
    contact = coast_contact(key, near, regions)
    clear_by_box = [_box_clear(sea, box) for box in PIECE_BOXES]
    candidates = {}
    for entry in regions.values():
        if entry.get("is_coastal"):
            candidates[entry["name"]] = port_candidates(key, clear_by_box, entry)
    anchors, crowded = place_anchors(
        candidates, first=scenario_dockyards(scenario or {}))
    return anchors, contact, crowded


def audit(registry: dict, scenario: dict, contact: Dict[str, int],
          anchors: Dict[str, List[int]]) -> List[str]:
    """Every disagreement between the registry/scenario and the art."""
    problems: List[str] = []
    regions = registry["regions"]
    by_name = {e["name"]: e for e in regions.values()}
    for name, entry in sorted(by_name.items()):
        art = contact.get(name, 0) >= MIN_CONTACT_PX
        flag = bool(entry.get("is_coastal"))
        if art != flag and name not in ART_EXCEPTIONS:
            problems.append(
                f"{name}: is_coastal={flag} but the art says "
                f"{'coastal' if art else 'inland'} (contact {contact.get(name, 0)} px)")
        if flag and name not in anchors and name not in ART_EXCEPTIONS:
            problems.append(f"{name}: is_coastal but no water fits a fleet off its shore")
    for nation, rec in sorted((scenario.get("navies") or {}).items()):
        if not isinstance(rec, dict):
            continue
        for field in ("dockyards",):
            for prov in rec.get(field) or []:
                entry = by_name.get(prov)
                if entry is None:
                    problems.append(f"{nation} {field}: {prov} is not a province")
                elif not entry.get("is_coastal"):
                    problems.append(f"{nation} dockyard {prov} is inland")
                elif prov not in anchors:
                    problems.append(
                        f"{nation} dockyard {prov} does not reach open water")
    ids = {rid: e["name"] for rid, e in regions.items()}
    for a, b in registry.get("sea_links", []):
        for idx in (a, b):
            name = ids.get("Region_%03d" % idx)
            if name and not by_name[name].get("is_coastal"):
                problems.append(f"sea link end {name} is inland")
    return problems


def write_anchors(registry: dict, anchors: Dict[str, List[int]]) -> dict:
    """The registry with `port_anchor` placed right after `building_anchor`
    on coastal provinces and removed from inland ones (key order kept, so
    the file diff is the anchors and nothing else)."""
    for rid, entry in list(registry["regions"].items()):
        point = anchors.get(entry["name"])
        rebuilt = {}
        for field, value in entry.items():
            if field == "port_anchor":
                continue
            rebuilt[field] = value
            if field == "building_anchor" and point is not None:
                rebuilt["port_anchor"] = list(point)
        if point is not None and "port_anchor" not in rebuilt:
            rebuilt["port_anchor"] = list(point)
        registry["regions"][rid] = rebuilt
    return registry


def dump_registry(registry: dict) -> str:
    return json.dumps(registry, indent=2) + "\n"


def render_preview(registry: dict, anchors: Dict[str, List[int]], path: str):
    """A review image: every coastal province's anchor (red) and its fleet
    piece's box + glyph at the port anchor (blue)."""
    from PIL import Image, ImageDraw

    img = Image.open(VISUAL).convert("RGB")
    draw = ImageDraw.Draw(img)
    for entry in registry["regions"].values():
        point = anchors.get(entry["name"])
        if point is None:
            continue
        ax, ay = entry["anchor"]
        x, y = point
        draw.line((ax, ay, x, y), fill=(200, 60, 60), width=1)
        draw.rectangle((x - 18, y - 36, x + 18, y + 4), outline=(20, 40, 200), width=2)
        draw.ellipse((x + 26 - 7, y - 12 - 7, x + 26 + 7, y - 12 + 7),
                     outline=(200, 30, 30), width=2)
        draw.text((x - 18, y + 6), entry["name"], fill=(0, 0, 0))
    img.save(path)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--preview", default="")
    args = parser.parse_args(argv)
    _need_imaging()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
    anchors, contact, crowded = derive_all(registry, scenario)
    problems = audit(registry, scenario, contact, anchors)
    for line in problems:
        print("MISMATCH", line)
    for name in crowded:
        print("CROWDED (no spaced mooring; shares water)", name)
    if args.audit:
        for name in sorted(contact):
            print(f"  {name:<18} contact={contact[name]:>5} "
                  f"port_anchor={anchors.get(name)}")
    rc = 1 if problems else 0
    if args.check:
        stale = [e["name"] for e in registry["regions"].values()
                 if e.get("port_anchor") != anchors.get(e["name"])]
        for name in stale:
            print("STALE port_anchor", name)
        rc = 1 if (problems or stale) else 0
    if args.write:
        REGISTRY.write_text(dump_registry(write_anchors(registry, anchors)),
                            encoding="utf-8", newline="\n")
        print(f"wrote {len(anchors)} port anchors to {REGISTRY.name}")
    if args.preview:
        render_preview(registry, anchors, args.preview)
        print("preview", args.preview)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
