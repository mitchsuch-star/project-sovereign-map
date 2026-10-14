"""UXR-3 fixes — the re-read's comparison (Pre-Deploy S12, October 13, 2026).

    .venv/Scripts/python.exe -X utf8 tools/uxr3_reread.py --before docs/audits/uxr3 \
        --after docs/audits/uxr3_s12 [--write] [--rows docs/audits/uxr3_s12/new_rows.json ...]

Reads two `review.json` records made by `tools/uxr3_review.py aggregate`
against the SAME frozen checklist (`docs/UX_CHECKLIST_V1.json`): the S11
review (`--before`) and a re-read (`--after`). It writes `reread.json` into the
re-read's records directory:

    flips      every (surface, item) whose mark changed, ✗ → ✓ and ✓ → ✗
    items      ✓ of 145 per item, before and after
    groups     the group table after (mean, lowest, 8 of 8, under 6), and before
    rows       every BUG_FIXES §UXR-3 row (`docs/audits/uxr3/bug_rows.json`,
               plus any later re-read's filed rows passed with `--rows`, e.g.
               S12 part 1's `docs/audits/uxr3_s12/new_rows.json`): FIXED when
               every (surface, item) it names now reads ✓, else OPEN with the
               (surface, item) pairs still ✗
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


NAMES = {"R1": "Readable", "R2": "Hierarchy", "R3": "Contrast", "R4": "Consistency",
         "R5": "Affordance", "R6": "Feedback", "R7": "Fit", "R8": "Discoverability"}


def markdown(out: dict, after: dict, frames_dir: str) -> str:
    """The re-read's tables, for its write-up: the items, the groups, the
    scores, the flips that broke, the rows still open, and every surface."""
    sys.path.insert(0, str(REPO / "tools"))
    import uxr3_review as RV
    RV.FRAMES_DIR = frames_dir
    lines = ["### The items", "", "| Item | ✓ of 145 at S11 | ✓ of 145 now |", "|---|---|---|"]
    for item in ITEMS:
        it = out["items"][item]
        lines.append(f"| {item} {NAMES[item]} | {it['before']} | **{it['after']}** |")
    t = out["ticks"]
    lines += ["", f"Marks: **{t['before']} → {t['after']}** ✓ of 1,160.", "",
              "### The groups", "",
              "| # | Group | Surfaces | Mean (S11 → now) | Lowest | At 8/8 | Under 6/8 |",
              "|---|---|---|---|---|---|---|"]
    before = {g["key"]: g for g in out["groups"]["before"]}
    for g in out["groups"]["after"]:
        b = before[g["key"]]
        lines.append(f"| {g['order']} | `{g['key']}`{' (top five)' if g['top_five'] else ''} | {g['surfaces']} | "
                     f"{b['mean']:.2f} → **{g['mean']:.2f}** | {b['min']} → {g['min']} | "
                     f"{b['eight_of_eight']} → **{g['eight_of_eight']}** | {b['under_six']} → **{g['under_six']}** |")
    hist = out["score_histogram"]
    lines += ["", "### The scores", "", "| Score | " + " | ".join(str(k) for k in range(9)) + " |",
              "|---" * 10 + "|", "| Surfaces | " + " | ".join(str(hist[str(k)]) for k in range(9)) + " |", ""]
    broke = out["flips"]["broke"]
    lines += ["### What flipped", "",
              f"{len(out['flips']['fixed'])} marks went ✗ → ✓ and {len(broke)} went ✓ → ✗."]
    if broke:
        lines += ["", "| Surface | Item | Why now |", "|---|---|---|"]
        for f in broke:
            why = f["why_after"]
            reader = (after["surfaces"][f["surface"]].get("readers") or {}).get(f["item"])
            if reader:
                no = [v["why"] for v in reader["votes"] if not v["pass"]]
                why = f"{why}: {no[0]}" if no else why
            lines.append(f"| `{f['surface']}` | {f['item']} | {why[:240]} |")
    open_rows = [r for r in out["rows"] if r["state"] == "OPEN"]
    lines += ["", "### The rows", "",
              f"{sum(1 for r in out['rows'] if r['state'] == 'FIXED')} of {len(out['rows'])} rows read ✓ on every "
              f"(surface, item) they name; {len(open_rows)} stay open:", "",
              "| Row | Still ✗ |", "|---|---|"]
    for r in open_rows:
        still = ", ".join(r["still"][:6]) + (f" (+{len(r['still']) - 6} more)" if len(r["still"]) > 6 else "")
        lines.append(f"| {r['id']} | {still} |")
    lines += ["", "### Every surface, every item", "", RV.render_table(after)]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", default=str(REPO / "docs" / "audits" / "uxr3"))
    ap.add_argument("--after", required=True)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--markdown", default="", help="write the re-read's tables to this file")
    ap.add_argument("--frames-dir", default="docs/audits/uxr3_s12/frames")
    ap.add_argument("--rows", action="append", default=[],
                    help="a later re-read's filed rows (its new_rows.json), judged with the review's")
    args = ap.parse_args(argv)
    before_dir, after_dir = pathlib.Path(args.before), pathlib.Path(args.after)
    rows = load(before_dir / "bug_rows.json") if (before_dir / "bug_rows.json").is_file() else []
    for extra in args.rows:
        rows = rows + load(pathlib.Path(extra))
    out = compare(load(before_dir / "review.json"), load(after_dir / "review.json"), rows)
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
    if args.markdown:
        pathlib.Path(args.markdown).write_text(markdown(out, load(after_dir / "review.json"), args.frames_dir),
                                               encoding="utf-8")
        print("wrote", args.markdown)
    return 0


if __name__ == "__main__":
    sys.exit(main())
