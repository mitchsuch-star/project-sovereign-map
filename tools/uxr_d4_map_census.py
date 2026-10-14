"""UXR-X28 — the map census record (Pre-Deploy S12b, October 14, 2026).

    .venv/Scripts/python.exe -X utf8 tools/uxr_d4_map_census.py \
        --board before=RUN/index.json --board dock_closed=RUN2/index.json@war_room_boot \
        [--note dock_closed="…"] [--out docs/audits/uxr_d4/map_census.json]

A board may name the surfaces it reads after an `@` (comma-separated), so
one shoot's index serves several boards (the Side Desk's `dock_open` reads
`side_desk_ledger` and `side_desk_generals`, `dock_closed` reads
`war_room_boot`).

Reads each run's frames with `tools/uxr3_frame_census.py`'s map census
(`map_overlaps`: every pair of map-tier rows — the furniture's text rows and
the place names the label layer drew — whose screen rects overlap by at
least 1 px²; `map_hidden`: what the furniture layout hid) and writes ONE
record, a board per run. A board already in the record is replaced; the
others are kept, so a later slice adds its board (the Side Desk's
`dock_open`) beside the earlier ones.

A board names the client it shot (`client_commit`, the run index's own git
HEAD) and, when the run was not of a committed tree, says so in its `note`.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import uxr3_frame_census as FC  # noqa: E402

DEFAULT_OUT = REPO / "docs" / "audits" / "uxr_d4" / "map_census.json"


def board(index_path: pathlib.Path, note: str = "", only: list[str] | None = None) -> dict:
    out = FC.census(index_path)
    if only:
        out["map_overlaps"] = [o for o in out["map_overlaps"] if o["surface"] in only]
        out["map_hidden"] = [h for h in out["map_hidden"] if h["surface"] in only]
        out["map_frames"] = sum(1 for sid, _r, fr in FC.frames(index_path)
                                if sid in only and "map_labels" in fr)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    resolutions, surfaces = [], []
    for sid, res, fr in FC.frames(index_path):
        if only and sid not in only:
            continue
        if "map_labels" in fr:
            resolutions.append(res)
            if sid not in surfaces:
                surfaces.append(sid)
    per_res = collections.Counter(o["res"] for o in out["map_overlaps"])
    pairs = collections.Counter(
        " / ".join(sorted([o["a"].split(":")[0], o["b"].split(":")[0]])) for o in out["map_overlaps"])
    return {
        "source": index_path.name,
        "client_commit": index.get("client_commit", ""),
        "physical_scale": index.get("physical_scale"),
        "hud_width": index.get("hud_width"),
        "note": note,
        "surfaces": surfaces,
        "resolutions": resolutions,
        "map_frames": out["map_frames"],
        "map_overlaps_count": len(out["map_overlaps"]),
        "map_overlaps_by_resolution": {r: per_res.get(r, 0) for r in dict.fromkeys(resolutions)},
        "map_overlaps_by_kind": dict(sorted(pairs.items())),
        "map_overlaps": out["map_overlaps"],
        "map_hidden": out["map_hidden"],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", action="append", default=[], help="NAME=path/to/index.json")
    ap.add_argument("--note", action="append", default=[], help="NAME=text")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args(argv)
    notes = dict(n.split("=", 1) for n in args.note)
    out_path = pathlib.Path(args.out)
    record = {"tool": "tools/uxr_d4_map_census.py", "row": "UXR-X28", "boards": {}}
    if out_path.exists():
        record = json.loads(out_path.read_text(encoding="utf-8"))
    for spec in args.board:
        name, path = spec.split("=", 1)
        path, _, only = path.partition("@")
        record["boards"][name] = board(pathlib.Path(path), notes.get(name, ""),
                                       [s for s in only.split(",") if s] or None)
        b = record["boards"][name]
        print(f"{name}: {b['map_overlaps_count']} overlaps over {b['map_frames']} frames "
              f"{b['map_overlaps_by_resolution']}; hidden {len(b['map_hidden'])}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
