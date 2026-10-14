"""UXR-3 fixes — the frame census (Pre-Deploy S12 part 2, October 14, 2026).

    .venv/Scripts/python.exe -X utf8 tools/uxr3_frame_census.py INDEX.json [--record OUT.json]

Reads what the capture harness records on every frame
(`tools/iq10_surface_screenshot.gd`) and states what the readers'
eyes and the instruments' marks do not measure directly:

    cut_lines      UXR3-F3: a line cut in half at a scroll's edge — the
                   harness's `frame["cut_lines"]` (a RichTextLabel inside a
                   ScrollContainer, whose window is the container's whole
                   rect, or one that scrolls itself)
    grip_overlaps  UXR3-F4: a resize grip or a corner ornament whose rect
                   overlaps a text's or a control's rect on its own layer
                   (`frame["grips"]` against `frame["texts"]` and
                   `frame["buttons"]`)
    tick_overlaps  UXR3-F1: a bar's centre tick (`kind: tick`) whose rect
                   overlaps a text on its layer (the war-detail score)
    verdict_gaps   UXR-X9: on every tableau frame, the room between the
                   verdict's box (`…/Verdict`) and the nameplate's first line
                   (`…/Nameplate/…`), in logical px — negative is an overlap
    map_overlaps   UXR-X28 (Pre-Deploy S12b): every pair of map-tier rows
                   whose screen rects overlap — the map's furniture (the
                   marshals' names, the stacks, the fogged chips and their
                   names, the garrison chips, the sail counts: text rows
                   inside the map's SubViewport, each with the screen `rect`
                   the harness records) and the place names the label layer
                   drew (`frame["map_labels"]`)
    map_hidden     what the map's furniture layout hid on that frame
                   (`frame["map_furniture"]["hidden"]`), so a 0 above is
                   never bought silently

Each finding names the shot, the resolution, the paths and the overlap. The
census judges nothing a row did not already state: it reads the rect records.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

MIN_AREA = 1.0     # px² of overlap that counts (a shared edge does not)


def _rect(r) -> tuple[float, float, float, float] | None:
    if not r or len(r) < 4:
        return None
    return float(r[0]), float(r[1]), float(r[2]), float(r[3])


def overlap(a, b) -> float:
    a, b = _rect(a), _rect(b)
    if a is None or b is None:
        return 0.0
    w = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    h = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return w * h if w > 0 and h > 0 else 0.0


def frames(index_path: pathlib.Path):
    # The rows' own results, as the other instruments read them, so a merged
    # index (tools/uxr3_merge_index.py) is read with its re-shot surfaces.
    index = json.loads(index_path.read_text(encoding="utf-8"))
    for row in index.get("rows", []):
        for rec in row.get("results", []):
            sid, _, res = str(rec.get("id", "")).partition("__")
            for fr in rec.get("frames", []):
                if fr.get("suffix"):
                    continue    # an intermediate step's frame, not the surface
                yield sid, res, fr


def census(index_path: pathlib.Path) -> dict:
    index = json.loads(index_path.read_text(encoding="utf-8"))
    out = {"tool": "tools/uxr3_frame_census.py", "source": str(index_path),
           "client_commit": index.get("client_commit", ""), "frames": 0, "frames_without_record": [],
           "cut_lines": [], "grip_overlaps": [], "tick_overlaps": [], "verdict_gaps": [],
           "map_frames": 0, "map_overlaps": [], "map_hidden": []}
    for sid, res, fr in frames(index_path):
        out["frames"] += 1
        if "cut_lines" not in fr or "grips" not in fr:
            out["frames_without_record"].append(f"{sid} {res}")
            continue
        for c in fr["cut_lines"]:
            out["cut_lines"].append({"surface": sid, "res": res, "path": c["path"], "kind": c.get("kind", ""),
                                     "cut_top_px": c["cut_top_px"], "cut_bottom_px": c["cut_bottom_px"]})
        texts = [t for t in fr.get("texts", []) if str(t.get("text", t.get("path", ""))).strip()]
        verdict = [t for t in texts if str(t.get("path", "")).endswith("/Verdict")]
        plate = [t for t in texts if "/Nameplate/" in str(t.get("path", ""))]
        if verdict and plate:
            v, top = verdict[0]["rect"], min(float(t["rect"][1]) for t in plate)
            out["verdict_gaps"].append({"surface": sid, "res": res,
                                        "gap_px": round(top - (float(v[1]) + float(v[3])), 1)})
        if "map_labels" in fr:
            _map_census(out, sid, res, fr)
        buttons = fr.get("buttons", [])
        for g in fr["grips"]:
            if g.get("kind") not in ("grip", "ornament", "tick"):
                continue
            for t in texts:
                if t.get("layer") != g.get("layer") or t.get("path") == g.get("path"):
                    continue
                area = overlap(g["rect"], t.get("rect") or t.get("rect_raw"))
                if area >= MIN_AREA:
                    row = {"surface": sid, "res": res, "kind": g["kind"], "path": g["path"],
                           "over": t.get("path", ""), "what": "text", "area_px2": round(area, 1)}
                    (out["tick_overlaps"] if g["kind"] == "tick" else out["grip_overlaps"]).append(row)
            if g["kind"] == "tick":
                continue
            for b in buttons:
                if b.get("layer") != g.get("layer") or b.get("path") == g.get("path"):
                    continue
                area = overlap(g["rect"], b.get("rect_raw"))
                if area >= MIN_AREA:
                    out["grip_overlaps"].append({"surface": sid, "res": res, "kind": g["kind"], "path": g["path"],
                                                 "over": b.get("path", ""), "what": "control",
                                                 "area_px2": round(area, 1)})
    return out


def map_rows(fr: dict) -> list[dict]:
    """The map tier of one frame: the furniture's text rows (with their
    screen rects) and the place names the label layer drew."""
    rows = []
    for t in fr.get("texts", []):
        if t.get("tier") != "map" or not t.get("rect") or not str(t.get("text", "")).strip():
            continue
        rows.append({"kind": t.get("map_kind") or "furniture", "text": str(t.get("text", "")),
                     "path": t.get("path", ""), "rect": t["rect"]})
    for m in fr.get("map_labels", []):
        rows.append({"kind": m.get("tier") or "place", "text": str(m.get("text", "")),
                     "path": "MapLabelLayer", "rect": m["rect"]})
    return rows


def _map_census(out: dict, sid: str, res: str, fr: dict) -> None:
    out["map_frames"] += 1
    rows = map_rows(fr)
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            area = overlap(a["rect"], b["rect"])
            if area >= MIN_AREA:
                out["map_overlaps"].append({"surface": sid, "res": res, "a": f"{a['kind']}:{a['text']}",
                                            "b": f"{b['kind']}:{b['text']}", "area_px2": round(area, 1)})
    for h in (fr.get("map_furniture") or {}).get("hidden", []):
        out["map_hidden"].append({"surface": sid, "res": res, "what": h})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("index")
    ap.add_argument("--record", default="")
    args = ap.parse_args(argv)
    out = census(pathlib.Path(args.index))
    print(f"frames {out['frames']} (without a record: {len(out['frames_without_record'])}); "
          f"cut lines {len(out['cut_lines'])}; grip overlaps {len(out['grip_overlaps'])}; "
          f"tick overlaps {len(out['tick_overlaps'])}; verdict gaps "
          f"{min((g['gap_px'] for g in out['verdict_gaps']), default=None)} px at the least "
          f"({len(out['verdict_gaps'])} tableaux); map overlaps {len(out['map_overlaps'])} "
          f"over {out['map_frames']} map frames ({len(out['map_hidden'])} furniture hidden)")
    for key in ("cut_lines", "grip_overlaps", "tick_overlaps", "map_overlaps", "map_hidden"):
        for row in out[key][:12]:
            print(f"  {key}: {json.dumps(row, ensure_ascii=False)[:220]}")
    if args.record:
        pathlib.Path(args.record).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                             encoding="utf-8", newline="\n")
        print("wrote", args.record)
    return 0


if __name__ == "__main__":
    sys.exit(main())
