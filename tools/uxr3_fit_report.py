"""UXR-3 R7 "Fit" — the instrument (Pre-Deploy S11, October 13, 2026).

    .venv/Scripts/python.exe -X utf8 tools/uxr3_fit_report.py <run>/index.json \
        [--record docs/audits/uxr3/fit_<label>.json]

Reads the capture harness's per-frame records (`tools/iq10_run_captures.py
--physical`; the harness fields `clipped_text`, `truncated_text`,
`buttons_offscreen`, `under_modal` and each text row's `rect_raw` /
`scroll_rect`) at the three resolutions R7 names, and applies R7's frozen rule
(`docs/UX_CHECKLIST_V1.json`):

  ✓ iff the surface has an ok reading at 1920x1080, 3840x2160 and 5120x1440
  and none of the three frames records
    (1) CLIPPED text — `clipped_text` (a RichTextLabel taller than its box
        outside a scroll) or `truncated_text` (a cut Label / Button line, a
        wrapped Label showing fewer lines than it holds, a non-wrapping
        RichTextLabel wider than its box, a text node in a zero-width box);
    (2) OVERFLOWING text or buttons — `buttons_offscreen`, or a text row whose
        rect (its ScrollContainer's, inside a scroll) leaves the logical
        viewport (`text_offscreen`, computed here);
    (3) anything UNDER A MODAL — `under_modal` (the harness applies the live
        frame and the drawing-control rule).

The map's world-space tier (rows inside the map's SubViewport) carries no
`rect_raw` and is not read, as R7 says.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

FIT_RESOLUTIONS = [(1920, 1080), (3840, 2160), (5120, 1440)]
TOLERANCE = 1.0


def _encloses(view: tuple[float, float], rect: list) -> bool:
    x, y, w, h = (float(v) for v in rect)
    return (x >= -TOLERANCE and y >= -TOLERANCE and x + w <= view[0] + TOLERANCE
            and y + h <= view[1] + TOLERANCE)


def text_offscreen(frame: dict) -> list[dict]:
    """Text rows outside the logical viewport — a row inside a scroll is judged
    by its ScrollContainer's rect, as the harness judges a button."""
    view = frame.get("logical_viewport") or [0, 0]
    vw, vh = float(view[0]), float(view[1])
    out = []
    for t in frame.get("texts") or []:
        raw = t.get("rect_raw")
        if not raw:
            continue                      # the map tier, or an older record
        rect = t.get("scroll_rect") or raw
        if float(rect[2]) <= 0.0 or float(rect[3]) <= 0.0:
            continue                      # drawn nowhere: truncated_text's zero_box
        if not _encloses((vw, vh), rect):
            out.append({"path": str(t.get("path", "")).split("/")[-1][:60],
                        "text": str(t.get("text", ""))[:40], "rect": [round(float(v)) for v in rect]})
    return out


def read_frame(res: dict) -> dict:
    frames = res.get("frames") or []
    if not frames:
        return {"ok": False, "missing": True}
    f = frames[-1]
    out = {
        "ok": bool(res.get("ok", False)),
        "errors": list(res.get("errors") or [])[:4],
        "clipped_text": f.get("clipped_text") or [],
        "truncated_text": f.get("truncated_text") or [],
        "buttons_offscreen": f.get("buttons_offscreen") or [],
        "text_offscreen": text_offscreen(f),
        "under_modal": f.get("under_modal") or [],
        "under_modal_count": int(f.get("under_modal_count", 0) or 0),
        "modal_layers": f.get("modal_layers"),
        "live_floor": f.get("live_floor"),
        "suspended_rows": f.get("suspended_rows"),
        "stray_input": f.get("stray_input"),
        "png": f.get("png", ""),
    }
    if "under_modal" not in f:
        out["ok"] = False
        out["errors"].append("the frame predates the R7 records (no under_modal field)")
    return out


def findings(reading: dict) -> int:
    return (len(reading.get("clipped_text", [])) + len(reading.get("truncated_text", []))
            + len(reading.get("buttons_offscreen", [])) + len(reading.get("text_offscreen", []))
            + int(reading.get("under_modal_count", 0)))


def read_run(index_path: pathlib.Path) -> dict:
    index = json.loads(index_path.read_text(encoding="utf-8"))
    record: dict = {"source": str(index_path), "client_commit": index.get("client_commit", ""),
                    "physical_scale": index.get("physical_scale"), "surfaces": {}}
    for row in index.get("rows", []):
        base = str(row.get("base_id") or row.get("id"))
        res_wh = tuple(row.get("resolution") or ())
        if res_wh not in FIT_RESOLUTIONS:
            continue
        surf = record["surfaces"].setdefault(base, {"readings": {}})
        for res in row.get("results", []):
            key = "%dx%d" % res_wh
            surf["readings"][key] = read_frame(res)
    for sid, surf in record["surfaces"].items():
        why = []
        for (w, h) in FIT_RESOLUTIONS:
            key = "%dx%d" % (w, h)
            r = surf["readings"].get(key)
            if r is None or r.get("missing"):
                why.append(f"{key}: no reading")
                continue
            if not r.get("ok"):
                why.append(f"{key}: the reading failed ({'; '.join(r.get('errors') or []) or 'not ok'})")
            n = findings(r)
            if n:
                parts = []
                for k in ("clipped_text", "truncated_text", "buttons_offscreen", "text_offscreen"):
                    if r.get(k):
                        parts.append(f"{len(r[k])} {k}")
                if r.get("under_modal_count"):
                    parts.append(f"{r['under_modal_count']} under_modal")
                why.append(f"{key}: " + ", ".join(parts))
        surf["pass"] = not why
        surf["why"] = why
    return record


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("index")
    ap.add_argument("--record", default="")
    args = ap.parse_args(argv)
    record = read_run(pathlib.Path(args.index))
    passed = sum(1 for s in record["surfaces"].values() if s["pass"])
    print(f"R7 fit: {passed} of {len(record['surfaces'])} surfaces pass at "
          f"{', '.join('%dx%d' % r for r in FIT_RESOLUTIONS)}")
    for sid, s in sorted(record["surfaces"].items()):
        if not s["pass"]:
            print(f"  ✗ {sid}: {' | '.join(s['why'])[:220]}")
    if args.record:
        p = pathlib.Path(args.record)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
        print("record:", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
