"""Session UI-4's blind reading, tabulated against Session UI-3's (the same rubric, the same 30 frame ids,
fresh readers each time). BASE is UI-3's final reading (HEAD e835f889, the tree this session started from);
AFTER is this session's three readers on the final tree.

Three frames are shot as the game shows them from this session on (tools/ui_rating/make_rating_set.py
STAGED_UI4): F24 the province panel over the live map, F25 the war detail over the t20 war room, F27 the menu
with the war office answering. Their marks are not comparable to UI-3's, so the summary is printed twice: all 30
frames, and the 27 whose staging never moved.

usage: python -I scores_ui4.py [--json]
"""
import json
import statistics
import sys

BASE = {
    # the three readers' reports on the final tree (tools/ui_rating/READER_PROMPT.md, verbatim; every
    # report's lines checked against the frames before tabulating — all three read them as labelled)
    "R1": ([7, 6, 6, 7, 8, 7, 7, 8, 7, 7, 8, 7, 6, 7, 6, 7, 7, 8, 7, 8, 7, 8, 7, 6, 6, 8, 7, 7, 7, 7], 7),
    "R2": ([7, 7, 7, 7, 7, 7, 7, 8, 7, 7, 8, 7, 6, 7, 7, 6, 7, 7, 7, 8, 7, 8, 7, 6, 6, 8, 7, 7, 8, 7], 7),
    "R3": ([7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 7, 7, 6, 7, 7, 7, 8, 7, 7, 7, 6, 6, 8, 6, 7, 7, 7], 7),
}
# Session UI-4's interim reading (fill from the readers' reports; empty = not yet read)
INTERIM = {
    # the interim reading on the first full shoot (before the fixes it named); all three read as labelled
    "R1": ([7, 6, 7, 7, 8, 7, 7, 8, 6, 7, 7, 8, 7, 7, 6, 7, 7, 8, 7, 8, 7, 8, 7, 7, 6, 8, 7, 6, 8, 8], 7),
    "R2": ([7, 7, 6, 7, 8, 7, 8, 7, 7, 7, 7, 8, 7, 6, 6, 6, 7, 7, 7, 8, 7, 8, 7, 7, 6, 8, 8, 6, 7, 7], 7),
    "R3": ([7, 6, 7, 7, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 7, 7, 7, 8, 7, 8, 7, 7, 6, 8, 8, 6, 7, 7], 7),
}
AFTER = {
    # the three final readers on the final tree (READER_PROMPT.md verbatim, the frozen rubric, the same 30 frame ids;
    # every report's lines checked against the frames before tabulating - all three read them as labelled)
    "R1": ([7, 7, 6, 6, 8, 7, 7, 8, 7, 7, 7, 8, 7, 7, 6, 6, 7, 7, 7, 8, 7, 8, 7, 7, 6, 8, 9, 7, 8, 7], 7),
    "R2": ([7, 7, 7, 7, 8, 7, 8, 7, 7, 7, 7, 8, 7, 7, 7, 7, 7, 8, 7, 8, 7, 8, 7, 7, 7, 8, 8, 7, 7, 7], 7),
    "R3": ([7, 7, 6, 7, 8, 7, 7, 7, 6, 6, 7, 7, 7, 6, 6, 6, 7, 7, 7, 8, 7, 7, 7, 7, 6, 8, 8, 7, 8, 7], 7),
}
RESTAGED = (23, 24, 26)   # F24, F25, F27 (zero-based)
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



def _subset(data: dict, keep: list) -> dict:
    return {r: ([data[r][0][i] for i in keep], data[r][1]) for r in data}


def _summary_n(data: dict, n: int) -> dict:
    readers = list(data)
    marks = [s for r in readers for s in data[r][0]]
    meds = [statistics.median([data[r][0][i] for r in readers]) for i in range(n)]
    return {"overall": [data[r][1] for r in readers], "mean_of_all_marks": round(statistics.mean(marks), 2),
            "median_of_frame_medians": statistics.median(meds)}


def main() -> int:
    if not AFTER:
        print("AFTER is empty — fill it from the readers' reports")
        return 1
    b, a = summary(BASE), summary(AFTER)
    if INTERIM:
        i = summary(INTERIM)
        print("interim:", i["overall"], "mean", i["mean_of_all_marks"], "median of frame medians",
              i["median_of_frame_medians"])
    if "--json" in sys.argv:
        print(json.dumps({"before": b, "after": a}, indent=1))
    print("ALL 30  overall before", b["overall"], "after", a["overall"], "| median", b["overall_median"], "->",
          a["overall_median"])
    print("ALL 30  mean of 90 marks", b["mean_of_all_marks"], "->", a["mean_of_all_marks"])
    print("ALL 30  median of frame medians", b["median_of_frame_medians"], "->", a["median_of_frame_medians"])
    keep = [i for i in range(30) if i not in RESTAGED]
    b27, a27 = _summary_n(_subset(BASE, keep), 27), _summary_n(_subset(AFTER, keep), 27)
    print("27 UNMOVED  mean of 81 marks", b27["mean_of_all_marks"], "->", a27["mean_of_all_marks"],
          "| median of frame medians", b27["median_of_frame_medians"], "->", a27["median_of_frame_medians"])
    print("per-reader means before", b["per_reader_mean"], "after", a["per_reader_mean"])
    up = down = same = 0
    for i in range(30):
        d = a["frames"][i]["median"] - b["frames"][i]["median"]
        up += d > 0
        down += d < 0
        same += d == 0
        mark = "+" if d > 0 else ("-" if d < 0 else "=")
        tag = "  (re-staged)" if i in RESTAGED else ""
        print(f"F{i + 1:02d} {NAMES[i]:15} {b['frames'][i]['median']:>4} -> {a['frames'][i]['median']:>4} {mark}"
              f"  after {a['frames'][i]['scores']}{tag}")
    print("frames up", up, "same", same, "down", down)
    spread = (sum(1 for f in a["frames"] if f["range"] == 0), sum(1 for f in a["frames"] if f["range"] == 1),
              sum(1 for f in a["frames"] if f["range"] >= 2))
    print("after spread: unanimous / 1 / 2+ =", spread)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
