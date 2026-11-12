"""Session UI-3's blind reading, tabulated against Session UI-2's (the same rubric, the same 30 frame ids, fresh
readers each time). BASE is UI-2's AFTER reading (HEAD 8db8d10c, the tree this session started from); AFTER is
this session's three readers on the final tree.

usage: python -I scores_ui3.py [--json]
"""
import json
import statistics
import sys

BASE = {
    "R1": ([7, 6, 7, 7, 8, 7, 7, 8, 7, 7, 6, 6, 6, 7, 7, 6, 7, 7, 7, 8, 6, 8, 7, 6, 6, 8, 8, 7, 7, 7], 7),
    "R2": ([8, 6, 7, 7, 8, 7, 7, 8, 7, 7, 6, 6, 6, 7, 7, 5, 7, 7, 7, 8, 6, 7, 7, 6, 6, 8, 8, 7, 8, 7], 7),
    "R3": ([7, 6, 6, 7, 8, 7, 8, 8, 7, 7, 6, 6, 6, 7, 7, 5, 7, 8, 7, 9, 5, 8, 7, 5, 6, 8, 8, 6, 8, 8], 7),
}
# The interim reading (the same protocol, on the shoot before the four fixes the record names). Its first
# reader's labels slipped a frame from F15 on (its F15 describes the settlement, its F30 a frame that does
# not exist): set aside, not re-mapped. The two readers below read the frames as labelled.
INTERIM = {
    "R2": ([7, 6, 7, 7, 7, 6, 6, 7, 7, 6, 7, 6, 5, 6, 5, 5, 7, 7, 6, 8, 7, 8, 7, 5, 5, 8, 7, 6, 7, 7], 7),
    "R3": ([7, 6, 7, 7, 7, 7, 7, 8, 6, 6, 7, 7, 6, 7, 6, 6, 7, 7, 7, 8, 7, 7, 7, 5, 6, 8, 7, 7, 7, 7], 7),
}
AFTER = {
    # the three readers' reports on the final tree (tools/ui_rating/READER_PROMPT.md, verbatim; every
    # report's lines checked against the frames before tabulating — all three read them as labelled)
    "R1": ([7, 6, 6, 7, 8, 7, 7, 8, 7, 7, 8, 7, 6, 7, 6, 7, 7, 8, 7, 8, 7, 8, 7, 6, 6, 8, 7, 7, 7, 7], 7),
    "R2": ([7, 7, 7, 7, 7, 7, 7, 8, 7, 7, 8, 7, 6, 7, 7, 6, 7, 7, 7, 8, 7, 8, 7, 6, 6, 8, 7, 7, 8, 7], 7),
    "R3": ([7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 7, 7, 6, 7, 7, 7, 8, 7, 7, 7, 6, 6, 8, 6, 7, 7, 7], 7),
}
NAMES = ["war room", "war room 5120", "war room 2.0", "School of War", "Forces", "Economy", "Territories",
         "Manpower", "Generals boot", "Generals T20", "Nations", "Vassals", "Balance", "Cabinet 1", "Cabinet 2",
         "settlement", "Dispatch", "Moniteur", "enemy phase", "diorama", "petition", "affair letter",
         "objection", "region panel", "war detail", "campaign end", "main menu", "Campaign Menu", "mailbox",
         "Correspondence"]


def summary(data):
    readers = list(data)
    frames = []
    for i in range(30):
        vals = [data[r][0][i] for r in readers]
        frames.append({"median": statistics.median(vals), "scores": vals, "range": max(vals) - min(vals)})
    marks = [s for r in readers for s in data[r][0]]
    return {
        "frames": frames,
        "per_reader_mean": {r: round(statistics.mean(data[r][0]), 2) for r in readers},
        "per_reader_median": {r: statistics.median(data[r][0]) for r in readers},
        "overall": [data[r][1] for r in readers],
        "overall_median": statistics.median([data[r][1] for r in readers]),
        "median_of_frame_medians": statistics.median([f["median"] for f in frames]),
        "mean_of_all_marks": round(statistics.mean(marks), 2),
    }


def main() -> int:
    if not AFTER:
        print("AFTER is empty — fill it from the readers' reports")
        return 1
    b, a = summary(BASE), summary(AFTER)
    i = summary(INTERIM)
    print("interim (two readers):", i["overall"], "mean", i["mean_of_all_marks"],
          "median of frame medians", i["median_of_frame_medians"])
    if "--json" in sys.argv:
        print(json.dumps({"before": b, "after": a}, indent=1))
    print("overall before", b["overall"], "after", a["overall"], "| median", b["overall_median"], "->",
          a["overall_median"])
    print("mean of 90 marks", b["mean_of_all_marks"], "->", a["mean_of_all_marks"])
    print("median of frame medians", b["median_of_frame_medians"], "->", a["median_of_frame_medians"])
    print("per-reader means before", b["per_reader_mean"], "after", a["per_reader_mean"])
    up = down = same = 0
    for i in range(30):
        d = a["frames"][i]["median"] - b["frames"][i]["median"]
        up += d > 0
        down += d < 0
        same += d == 0
        mark = "+" if d > 0 else ("-" if d < 0 else "=")
        print(f"F{i + 1:02d} {NAMES[i]:15} {b['frames'][i]['median']:>4} -> {a['frames'][i]['median']:>4} {mark}"
              f"  after {a['frames'][i]['scores']}")
    print("frames up", up, "same", same, "down", down)
    spread = (sum(1 for f in a["frames"] if f["range"] == 0), sum(1 for f in a["frames"] if f["range"] == 1),
              sum(1 for f in a["frames"] if f["range"] >= 2))
    print("after spread: unanimous / 1 / 2+ =", spread)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
