"""UXR-D1 "Text size" (Pre-Deploy S9b) — the reader that pairs two physical runs.

    .venv/Scripts/python.exe -X utf8 tools/uxr2b_text_size_check.py \
        --base <run at --text-size 1.0>/index.json \
        --scaled <run at --text-size 1.5>/index.json \
        [--record docs/audits/uxr0/readability_text150_named_<date>.json]

Both runs are `tools/iq10_run_captures.py --physical --physical-scale 1.0` over
the same surfaces, one at the shipped theme and one at a Text size. The done-
when of UXR-D1 (`docs/DESIGN_REFINEMENT.md` §UXR) is read off the pair:

* **0 RED / 0 P1** at the Text size — the floor of `uxr0_readability_report`;
* **the slider moves every text node the census sees** — every text row of the
  scaled run whose twin (same node path, same text) is in the base run carries
  `round(base font size x factor)`; a row that kept its size is listed by path
  (the eighteen named raw overrides would be the only lawful ones, and none of
  them is on the named surfaces);
* **and no panel rect** — every top-level surface (`frame["surfaces"]`, a
  Control whose parent is a CanvasLayer or the shot's scene root) keeps its
  logical rect; a moved one is listed with both rects;
* nothing clipped and no button off-screen (the harness's own per-frame flags).

The record is compact (counts, and the offending rows / rects in full) so the
pin in `tests/test_uxr2b_text_size.py` runs on committed numbers, never on
Godot.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from uxr0_readability_report import classify  # noqa: E402


def _frames(index_paths: list) -> dict:
    """{(base_id, "WxH"): last frame + the result row} for one run — or for a
    run and its partial re-shoots, a later index overriding an earlier one
    surface by surface (the first index's provenance is kept)."""
    index = json.loads(pathlib.Path(index_paths[0]).read_text(encoding="utf-8"))
    rows = []
    for extra in index_paths:
        rows.extend(json.loads(pathlib.Path(extra).read_text(encoding="utf-8")).get("rows", []))
    out = {}
    for row in rows:
        base = str(row.get("base_id") or row.get("id"))
        for res in row.get("results", []):
            frames = res.get("frames") or []
            if not frames:
                continue
            win = res.get("window") or [0, 0]
            out[(base, "%dx%d" % (int(win[0]), int(win[1])))] = {
                "frame": frames[-1], "ok": bool(res.get("ok", False)),
                "scale": float(res.get("scale", 1.0)),
                "text_size": float(res.get("text_size", 1.0) or 1.0),
            }
    return {"index": index, "frames": out}


def _rows(frame: dict) -> dict:
    """{(path, text): row} for every censused text row (the map tier aside:
    it is the world-space furniture, sized by the camera — UXR-X4)."""
    out = {}
    for t in frame.get("texts") or []:
        if "em_px" not in t or t.get("tier") == "map":
            continue
        out[(str(t.get("path", "")), str(t.get("text", ""))[:80])] = t
    return out


def _rect_moved(a: list, b: list, tol: float = 0.51) -> bool:
    return any(abs(float(x) - float(y)) > tol for x, y in zip(a, b))


def compare(base_index: list, scaled_index: list) -> dict:
    base, scaled = _frames(base_index), _frames(scaled_index)
    factor = float(scaled["index"].get("text_size", 1.0) or 1.0)
    record: dict = {
        "factor": factor,
        "base_source": [str(p) for p in base_index],
        "scaled_source": [str(p) for p in scaled_index],
        "client_commit": scaled["index"].get("client_commit", ""),
        "physical_scale": scaled["index"].get("physical_scale"),
        "surfaces": {},
    }
    for key, s in sorted(scaled["frames"].items()):
        b = base["frames"].get(key)
        sid, res = key
        sf = s["frame"]
        counts = {"rows": 0, "red": 0, "p1": 0, "ok": 0, "map": 0,
                  "paired": 0, "scaled": 0, "unscaled": 0}
        flagged, unscaled = [], []
        for (path, text), t in _rows(sf).items():
            verdict = classify(t)
            counts["rows"] += 1
            counts[verdict] = counts.get(verdict, 0) + 1
            if verdict in ("red", "p1"):
                flagged.append({"path": path, "text": text[:40], "em": round(float(t["em_px"]), 2),
                                "verdict": verdict})
            twin = _rows(b["frame"]).get((path, text)) if b else None
            if twin is None:
                continue
            counts["paired"] += 1
            # GDScript's round() is half-away-from-zero (24.5 -> 25); Python's
            # is the banker's (24.5 -> 24) — use the engine's rule.
            want = int(math.floor(int(twin.get("font_size", 0)) * factor + 0.5))
            if int(t.get("font_size", 0)) == want:
                counts["scaled"] += 1
            else:
                counts["unscaled"] += 1
                unscaled.append({"path": path, "text": text[:40],
                                 "base": twin.get("font_size"), "scaled": t.get("font_size"),
                                 "want": want})
        counts["map"] = sum(1 for t in (sf.get("texts") or []) if t.get("tier") == "map")
        moved = []
        if b:
            bs = b["frame"].get("surfaces") or {}
            for path, rect in (sf.get("surfaces") or {}).items():
                if path in bs and _rect_moved(bs[path], rect):
                    moved.append({"path": path, "base": bs[path], "scaled": rect})
        reading = {
            "window": [int(v) for v in res.split("x")], "scale": s["scale"],
            "text_size": s["text_size"], "ok": s["ok"] and bool(b and b["ok"]),
            "counts": counts, "flagged": flagged, "unscaled": unscaled,
            "surfaces_moved": moved,
            "surfaces_seen": len(sf.get("surfaces") or {}),
            "clipped_text": len(sf.get("clipped_text") or []),
            "buttons_offscreen": len(sf.get("buttons_offscreen") or []),
        }
        record["surfaces"].setdefault(sid, {"readings": {}})["readings"][res] = reading
    return record


def summary(record: dict) -> dict:
    t = {"readings": 0, "rows": 0, "red": 0, "p1": 0, "paired": 0, "scaled": 0,
         "unscaled": 0, "moved": 0, "clipped": 0, "offscreen": 0}
    for surf in record["surfaces"].values():
        for r in surf["readings"].values():
            t["readings"] += 1
            for k in ("rows", "red", "p1", "paired", "scaled", "unscaled"):
                t[k] += int(r["counts"].get(k, 0))
            t["moved"] += len(r["surfaces_moved"])
            t["clipped"] += r["clipped_text"]
            t["offscreen"] += r["buttons_offscreen"]
    return t


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="index.json[,re-shoot index.json…]")
    ap.add_argument("--scaled", required=True, help="index.json[,re-shoot index.json…]")
    ap.add_argument("--record", default="")
    args = ap.parse_args(argv)
    record = compare([p for p in args.base.split(",") if p], [p for p in args.scaled.split(",") if p])
    t = summary(record)
    print(f"Text size x{record['factor']:.2f}: {t}")
    for sid, surf in record["surfaces"].items():
        for res, r in surf["readings"].items():
            bad = (r["counts"]["red"] or r["counts"]["p1"] or r["unscaled"] or r["surfaces_moved"]
                   or r["clipped_text"] or r["buttons_offscreen"] or not r["ok"])
            if bad:
                print(f"  {sid:24} {res:10} RED {r['counts']['red']} P1 {r['counts']['p1']} "
                      f"unscaled {len(r['unscaled'])} moved {len(r['surfaces_moved'])} "
                      f"clipped {r['clipped_text']} offscreen {r['buttons_offscreen']} ok {r['ok']}")
                for u in r["unscaled"][:4]:
                    print(f"      unscaled {u}")
                for m in r["surfaces_moved"][:4]:
                    print(f"      moved {m}")
    if args.record:
        p = pathlib.Path(args.record)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"record: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
