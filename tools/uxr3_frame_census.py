"""UXR-3 fixes — the frame census (Pre-Deploy S12 part 2, October 14, 2026).

    .venv/Scripts/python.exe -X utf8 tools/uxr3_frame_census.py INDEX.json [--record OUT.json]

Reads what the capture harness records on every frame
(`tools/iq10_surface_screenshot.gd`) and states three things the readers'
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
    index = json.loads(index_path.read_text(encoding="utf-8"))
    result = json.loads(pathlib.Path(index["result"]).read_text(encoding="utf-8"))
    for rec in result.get("results", []):
        sid, _, res = str(rec.get("id", "")).partition("__")
        for fr in rec.get("frames", []):
            if fr.get("suffix"):
                continue    # an intermediate step's frame, not the surface
            yield sid, res, fr
    return


def census(index_path: pathlib.Path) -> dict:
    index = json.loads(index_path.read_text(encoding="utf-8"))
    out = {"tool": "tools/uxr3_frame_census.py", "source": str(index_path),
           "client_commit": index.get("client_commit", ""), "frames": 0, "frames_without_record": [],
           "cut_lines": [], "grip_overlaps": [], "tick_overlaps": []}
    for sid, res, fr in frames(index_path):
        out["frames"] += 1
        if "cut_lines" not in fr or "grips" not in fr:
            out["frames_without_record"].append(f"{sid} {res}")
            continue
        for c in fr["cut_lines"]:
            out["cut_lines"].append({"surface": sid, "res": res, "path": c["path"], "kind": c.get("kind", ""),
                                     "cut_top_px": c["cut_top_px"], "cut_bottom_px": c["cut_bottom_px"]})
        texts = [t for t in fr.get("texts", []) if str(t.get("text", t.get("path", ""))).strip()]
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("index")
    ap.add_argument("--record", default="")
    args = ap.parse_args(argv)
    out = census(pathlib.Path(args.index))
    print(f"frames {out['frames']} (without a record: {len(out['frames_without_record'])}); "
          f"cut lines {len(out['cut_lines'])}; grip overlaps {len(out['grip_overlaps'])}; "
          f"tick overlaps {len(out['tick_overlaps'])}")
    for key in ("cut_lines", "grip_overlaps", "tick_overlaps"):
        for row in out[key][:12]:
            print(f"  {key}: {json.dumps(row, ensure_ascii=False)[:220]}")
    if args.record:
        pathlib.Path(args.record).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                             encoding="utf-8", newline="\n")
        print("wrote", args.record)
    return 0


if __name__ == "__main__":
    sys.exit(main())
