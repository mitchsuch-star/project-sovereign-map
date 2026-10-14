"""UXR-3 fixes — the re-read's comparison (Pre-Deploy S12, October 13, 2026).

    .venv/Scripts/python.exe -X utf8 tools/uxr3_reread.py --before docs/audits/uxr3 \
        --after docs/audits/uxr3_s12 [--write]

Reads two `review.json` records made by `tools/uxr3_review.py aggregate`
against the SAME frozen checklist (`docs/UX_CHECKLIST_V1.json`): the S11
review (`--before`) and a re-read (`--after`). It writes `reread.json` into the
re-read's records directory:

    flips      every (surface, item) whose mark changed, ✗ → ✓ and ✓ → ✗
    items      ✓ of 145 per item, before and after
    groups     the group table after (mean, lowest, 8 of 8, under 6), and before
    rows       every BUG_FIXES §UXR-3 row (`docs/audits/uxr3/bug_rows.json`):
               FIXED when every (surface, item) it names now reads ✓, else
               OPEN with the (surface, item) pairs still ✗
    done_when  §UXR-3's: the top five groups at 8 of 8, none under 6

Nothing here judges: it compares two records the instruments and the readers
already made, under the rule the checklist states.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
ITEMS = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compare(before: dict, after: dict, rows: list[dict]) -> dict:
    b, a = before["surfaces"], after["surfaces"]
    assert list(b) == list(a), "the two readings do not cover the same surfaces in the same order"
    flips = {"fixed": [], "broke": []}
    for sid in a:
        for item in ITEMS:
            was, now = bool(b[sid]["marks"][item]["pass"]), bool(a[sid]["marks"][item]["pass"])
            if was != now:
                (flips["fixed"] if now else flips["broke"]).append(
                    {"surface": sid, "item": item, "why_before": b[sid]["marks"][item].get("why", ""),
                     "why_after": a[sid]["marks"][item].get("why", "")})
    items = {item: {"before": sum(1 for s in b.values() if s["marks"][item]["pass"]),
                    "after": sum(1 for s in a.values() if s["marks"][item]["pass"])} for item in ITEMS}
    row_state = []
    for r in rows:
        still = [(sid, item) for sid in r["surfaces"] for item in r["items"]
                 if not a[sid]["marks"][item]["pass"]]
        row_state.append({"id": r["id"], "items": r["items"], "surfaces": r["surfaces"],
                          "state": "FIXED" if not still else "OPEN",
                          "still": [f"{sid} {item}" for sid, item in still]})
    groups_after = after["groups"]
    top = [g for g in groups_after if g["top_five"]]
    done = {"top_five_all_eight": all(g["eight_of_eight"] == g["surfaces"] for g in top),
            "top_five_at_eight": sum(g["eight_of_eight"] for g in top),
            "top_five_surfaces": sum(g["surfaces"] for g in top),
            "under_six": sum(g["under_six"] for g in groups_after)}
    done["met"] = done["top_five_all_eight"] and done["under_six"] == 0
    scores_after = [s["score"] for s in a.values()]
    return {"checklist": "docs/UX_CHECKLIST_V1.json",
            "ticks": {"before": sum(sum(1 for i in ITEMS if s["marks"][i]["pass"]) for s in b.values()),
                      "after": sum(sum(1 for i in ITEMS if s["marks"][i]["pass"]) for s in a.values())},
            "items": items, "flips": flips, "groups": {"before": before["groups"], "after": groups_after},
            "score_histogram": {str(k): scores_after.count(k) for k in range(9)},
            "worst_five": after["worst_five"], "rows": row_state, "done_when": done}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", default=str(REPO / "docs" / "audits" / "uxr3"))
    ap.add_argument("--after", required=True)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    before_dir, after_dir = pathlib.Path(args.before), pathlib.Path(args.after)
    out = compare(load(before_dir / "review.json"), load(after_dir / "review.json"),
                  load(before_dir / "bug_rows.json"))
    print(f"ticks: {out['ticks']['before']} -> {out['ticks']['after']} of 1160")
    for item in ITEMS:
        print(f"  {item}: {out['items'][item]['before']:3d} -> {out['items'][item]['after']:3d}")
    print(f"flips: {len(out['flips']['fixed'])} fixed, {len(out['flips']['broke'])} broke")
    fixed = [r["id"] for r in out["rows"] if r["state"] == "FIXED"]
    print(f"rows FIXED by the re-read: {len(fixed)} of {len(out['rows'])}")
    print("done-when:", out["done_when"])
    if args.write:
        (after_dir / "reread.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                               encoding="utf-8")
        print("wrote", after_dir / "reread.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
