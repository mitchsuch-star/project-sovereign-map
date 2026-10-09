"""UXR-0 "The readability instrument" — the reader of the physical-pixel census.

    .venv/Scripts/python.exe tools/uxr0_readability_report.py <run>/index.json \
        [--record docs/audits/uxr0/readability_<label>.json] [--surfaces a,b,c]
    .venv/Scripts/python.exe tools/uxr0_readability_report.py --compare BEFORE.json AFTER.json

`tools/iq10_run_captures.py --physical` shoots every surface at the five
resolutions in PHYSICAL_RESOLUTIONS (the fifth is the user's own 5120x1440),
with Interface Scale as a player at that size would have it (`--physical-scale
auto` = `derive_ui_scale`, the Python twin of `UiSettings.derive_default_ui_scale`;
`1.0` = the shipped default, the BEFORE picture). The harness records, for every
visible text node, the em / cap-height / x-height of its resolved font in
physical pixels. THIS module holds the floor — in one place, so the test, the
report and the plan read the same numbers:

    body-class text     RED under BODY_RED em px,     a P1 under BODY_P1
    caption-class text  RED under CAPTION_RED em px,  a P1 under CAPTION_P1

Caption-class = a node whose `theme_type_variation` is Caption / CaptionRich /
CaptionButton (badges, hints, version lines — secondary by design, 0.85x body is
the typographic norm). Everything else is body-class. The floor is on the EM
(the industry statement — 16 px CSS body, 12 px Windows at 100%); the cap and x
heights are recorded beside it because the FACE is the other half of
legibility (EB Garamond's x-height is 0.44 em; a sans is 0.57).

The record this writes (`--record`) is the committed machine record
`tests/test_uxr0_readability.py` reads — a compact per-surface, per-resolution
table of counts plus every RED/P1 row — so the pin runs on the committed
numbers, never on Godot.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

# ── the floor (decision 2, docs/audits/UXR_ADJUSTABILITY_REVIEW_2026_10_09.md §6)
BODY_RED = 16.0
BODY_P1 = 13.0
CAPTION_RED = 14.0
CAPTION_P1 = 12.0

# ── the resolution set (decision 1) — (width, height); the user's own is fourth.
PHYSICAL_RESOLUTIONS = [(1920, 1080), (2560, 1440), (3440, 1440), (5120, 1440), (3840, 2160)]

# ── the scale formula (decision 3) — the Python twin of
#    UiSettings.derive_default_ui_scale (godot-client/.../scripts/ui_settings.gd).
#    A test pins the two on a table; change both or neither.
SCALE_MIN = 1.0
SCALE_MAX = 3.0
SCALE_ROUND = 0.05
ULTRA_WIDE_ASPECT = 3.0     # 32:9 (3.56) qualifies; 21:9 (2.39) does not
ULTRA_WIDE_BONUS = 0.25


def derive_ui_scale(width: int, height: int, dpi: float = 96.0) -> float:
    """The Interface Scale a player at this screen would have: never below
    the Windows scaling they chose (dpi/96), lifted toward the panel's pixel
    height, +0.25 on a 32:9 panel (sat further from; a 21:9 is a 27-inch's
    distance and gets none), clamped to [1, 3], rounded to 0.05."""
    if width <= 0 or height <= 0:
        return 1.0
    d = max(dpi, 1.0) / 96.0
    h = height / 1080.0
    s = max(d, (d + h) / 2.0)
    if width / height >= ULTRA_WIDE_ASPECT:
        s += ULTRA_WIDE_BONUS
    s = max(SCALE_MIN, min(SCALE_MAX, s))
    return round(round(s / SCALE_ROUND) * SCALE_ROUND, 2)


# ── reading a run ────────────────────────────────────────────────────────────

def classify(row: dict) -> str:
    """'p1' / 'red' / 'ok' / 'map' for one census row, by tier and em. The
    map tier (world-space furniture inside the map's SubViewport, sized by
    the camera) is counted beside the floor, never under it — UXR-X4."""
    em = row.get("em_px")
    if not isinstance(em, (int, float)):
        return "ok"
    if row.get("tier") == "map":
        return "map"
    if row.get("tier") == "caption":
        red, p1 = CAPTION_RED, CAPTION_P1
    else:
        red, p1 = BODY_RED, BODY_P1
    if em < p1 - 1e-6:
        return "p1"
    if em < red - 1e-6:
        return "red"
    return "ok"


def _compact(row: dict) -> dict:
    text = str(row.get("text", ""))
    return {
        "path": row.get("path", ""),
        "text": (text[:40] + "…") if len(text) > 40 else text,
        "class": row.get("class"),
        "tier": row.get("tier", "body"),
        "font": row.get("font"),
        "size": row.get("font_size"),
        "em": round(float(row.get("em_px", 0.0)), 2),
        "cap": round(float(row.get("cap_px", 0.0)), 2),
        "x": round(float(row.get("x_px", 0.0)), 2),
    }


def read_run(index_path: pathlib.Path, surfaces: set[str] | None = None,
             keep_flagged: int | None = None) -> dict:
    """index.json (the runner's) → {surface_id: {"WxH@S": {counts, rows}}}.
    `keep_flagged` caps the flagged rows kept per reading (the whole-client
    record is counts plus the worst few; the named record keeps every row)."""
    index = json.loads(index_path.read_text(encoding="utf-8"))
    out: dict = {"date": index.get("date"), "source": str(index_path), "surfaces": {},
                 "client_commit": index.get("client_commit", ""),
                 "physical_scale": index.get("physical_scale")}
    for row in index.get("rows", []):
        base = str(row.get("base_id") or row.get("id"))
        if surfaces and base not in surfaces:
            continue
        for res in row.get("results", []):
            frames = res.get("frames") or []
            if not frames:
                continue
            win = res.get("window") or [0, 0]
            scale = float(res.get("scale", res.get("content_scale_factor", 1.0)))
            key = "%dx%d@%.2f" % (int(win[0]), int(win[1]), scale)
            texts = frames[-1].get("texts") or []
            flagged = []
            counts = {"rows": 0, "red": 0, "p1": 0, "ok": 0, "map": 0, "map_small": 0}
            for t in texts:
                if "em_px" not in t:
                    continue
                verdict = classify(t)
                if verdict == "map":
                    counts["map"] += 1
                    if float(t.get("em_px", 0.0)) < BODY_RED:
                        counts["map_small"] += 1
                    continue
                counts["rows"] += 1
                counts[verdict] += 1
                if verdict != "ok":
                    c = _compact(t)
                    c["verdict"] = verdict
                    flagged.append(c)
            flagged.sort(key=lambda r: (0 if r["verdict"] == "p1" else 1, r["em"]))
            if keep_flagged is not None:
                flagged = flagged[:keep_flagged]
            surf = out["surfaces"].setdefault(base, {"surface": row.get("surface", base),
                                                     "readings": {}})
            surf["readings"][key] = {
                "window": [int(win[0]), int(win[1])], "scale": scale,
                "ok": res.get("ok", False), "counts": counts, "flagged": flagged,
            }
    return out


def totals(record: dict) -> dict:
    t = {"surfaces": 0, "readings": 0, "rows": 0, "red": 0, "p1": 0}
    for surf in record.get("surfaces", {}).values():
        t["surfaces"] += 1
        for r in surf.get("readings", {}).values():
            t["readings"] += 1
            for k in ("rows", "red", "p1"):
                t[k] += int(r["counts"].get(k, 0))
    return t


def print_table(record: dict, limit: int = 6) -> None:
    rows = []
    for sid, surf in record.get("surfaces", {}).items():
        for key, r in surf["readings"].items():
            rows.append((r["counts"]["p1"], r["counts"]["red"], sid, key, r))
    rows.sort(key=lambda x: (-x[0], -x[1], x[2], x[3]))
    print(f"{'surface':40} {'frame':16} {'rows':>5} {'RED':>5} {'P1':>5}")
    for p1, red, sid, key, r in rows:
        print(f"{sid[:40]:40} {key:16} {r['counts']['rows']:5d} {red:5d} {p1:5d}")
    t = totals(record)
    print(f"\nTOTAL surfaces={t['surfaces']} readings={t['readings']} rows={t['rows']} "
          f"RED={t['red']} P1={t['p1']}")
    worst = [(sid, key, f) for sid, surf in record.get("surfaces", {}).items()
             for key, r in surf["readings"].items() for f in r["flagged"]]
    worst.sort(key=lambda x: x[2]["em"])
    if worst:
        print(f"\nworst {min(limit, len(worst))} rows:")
        for sid, key, f in worst[:limit]:
            print(f"  {f['verdict']:3} {f['em']:6.2f}px em (x {f['x']:5.2f}) {sid} {key} "
                  f"{f['path']} — {f['text']!r}")


def compare(before: dict, after: dict) -> dict:
    tb, ta = totals(before), totals(after)
    print(f"RED {tb['red']} -> {ta['red']}   P1 {tb['p1']} -> {ta['p1']}   "
          f"(rows {tb['rows']} -> {ta['rows']}, readings {tb['readings']} -> {ta['readings']})")
    out = {"before": tb, "after": ta, "per_surface": {}}
    for sid in sorted(set(before.get("surfaces", {})) | set(after.get("surfaces", {}))):
        b = before.get("surfaces", {}).get(sid, {}).get("readings", {})
        a = after.get("surfaces", {}).get(sid, {}).get("readings", {})
        for key in sorted(set(b) | set(a)):
            cb = b.get(key, {}).get("counts", {})
            ca = a.get(key, {}).get("counts", {})
            if cb != ca:
                out["per_surface"][f"{sid} {key}"] = {"before": cb, "after": ca}
                print(f"  {sid:36} {key:16} RED {cb.get('red', '-')}->{ca.get('red', '-')}"
                      f"  P1 {cb.get('p1', '-')}->{ca.get('p1', '-')}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("index", nargs="?", help="a runner index.json")
    ap.add_argument("--record", default="", help="write the compact machine record here")
    ap.add_argument("--surfaces", default="", help="comma list of surface ids to keep")
    ap.add_argument("--keep-flagged", type=int, default=None,
                    help="cap the flagged rows kept per reading in the record (the "
                         "whole-client record: counts + the worst few)")
    ap.add_argument("--compare", nargs=2, metavar=("BEFORE", "AFTER"))
    ap.add_argument("--derive", nargs=2, type=int, metavar=("W", "H"),
                    help="print the derived scale for a screen (dpi 96)")
    args = ap.parse_args(argv)
    if args.derive:
        print(derive_ui_scale(args.derive[0], args.derive[1]))
        return 0
    if args.compare:
        b = json.loads(pathlib.Path(args.compare[0]).read_text(encoding="utf-8"))
        a = json.loads(pathlib.Path(args.compare[1]).read_text(encoding="utf-8"))
        compare(b, a)
        return 0
    if not args.index:
        ap.error("an index.json, --compare or --derive is required")
    surfaces = {s.strip() for s in args.surfaces.split(",") if s.strip()} or None
    record = read_run(pathlib.Path(args.index), surfaces, args.keep_flagged)
    print_table(record)
    if args.record:
        p = pathlib.Path(args.record)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"\nrecord: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
