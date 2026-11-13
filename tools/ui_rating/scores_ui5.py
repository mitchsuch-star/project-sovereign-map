"""Session UI-5's blind reading, tabulated against Session UI-4's (the same rubric, the same 30 frame ids, the
same three stagings as UI-4 — `make_rating_set.STAGED_UI4` — fresh readers each time). BASE is UI-4's final
reading (HEAD 970a534c, the tree this session started from); INTERIM is this session's reading of the first full
shoot (before the fixes it named); AFTER is three fresh readers on the final tree.

A report whose lines describe another frame is SET ASIDE, never re-mapped (README, UI-3's trap): the interim's
R2 swapped F27 and F28 (its F27 line describes the Settings page, its F28 the main menu), so the interim is
reported on R1 and R3 (`INTERIM_SET_ASIDE`) with the three-reader figure beside it.

usage: python -I scores_ui5.py [--json]
"""
import json
import statistics
import sys

# UI-4's final reading (tools/ui_rating/scores_ui4.py AFTER, verbatim)
BASE = {
    "R1": ([7, 7, 6, 6, 8, 7, 7, 8, 7, 7, 7, 8, 7, 7, 6, 6, 7, 7, 7, 8, 7, 8, 7, 7, 6, 8, 9, 7, 8, 7], 7),
    "R2": ([7, 7, 7, 7, 8, 7, 8, 7, 7, 7, 7, 8, 7, 7, 7, 7, 7, 8, 7, 8, 7, 8, 7, 7, 7, 8, 8, 7, 7, 7], 7),
    "R3": ([7, 7, 6, 7, 8, 7, 7, 7, 6, 6, 7, 7, 7, 6, 6, 6, 7, 7, 7, 8, 7, 7, 7, 7, 6, 8, 8, 7, 8, 7], 7),
}
# Session UI-5's interim reading (the first full shoot, November 13; READER_PROMPT.md verbatim, the frozen rubric)
INTERIM = {
    "R1": ([7, 7, 7, 7, 7, 7, 6, 7, 6, 6, 7, 7, 7, 7, 6, 6, 7, 7, 7, 7, 7, 6, 7, 7, 6, 8, 8, 7, 7, 6], 7),
    "R2": ([7, 7, 6, 7, 8, 8, 7, 8, 6, 6, 7, 7, 7, 7, 7, 6, 8, 8, 8, 8, 8, 7, 7, 7, 7, 8, 8, 8, 8, 7], 7),
    "R3": ([7, 6, 7, 6, 8, 7, 7, 8, 7, 7, 7, 7, 7, 7, 7, 6, 8, 8, 8, 8, 8, 7, 7, 7, 7, 8, 9, 7, 8, 7], 7),
}
INTERIM_SET_ASIDE = ("R2",)      # its F27 / F28 lines swapped (each describes the other's frame)
# Session UI-5's final reading (the final shoot, November 13; READER_PROMPT.md verbatim, the frozen rubric; every
# report's lines checked against the frames before tabulating — all three read them as labelled)
AFTER = {
    "R1": ([7, 7, 6, 7, 7, 7, 7, 7, 6, 6, 7, 6, 7, 7, 7, 6, 7, 7, 8, 8, 8, 7, 8, 6, 6, 8, 8, 7, 7, 7], 7),
    "R2": ([7, 7, 6, 7, 8, 8, 7, 8, 6, 6, 7, 6, 7, 7, 7, 6, 7, 7, 8, 8, 7, 8, 7, 7, 6, 8, 8, 7, 8, 7], 7),
    "R3": ([7, 7, 6, 7, 8, 8, 7, 8, 6, 6, 7, 7, 7, 7, 7, 6, 7, 7, 8, 7, 8, 8, 8, 6, 6, 8, 9, 7, 7, 7], 7),
}
AFTER_SET_ASIDE = ()
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
        "overall": [data[r][1] for r in readers],
        "overall_median": statistics.median([data[r][1] for r in readers]),
        "median_of_frame_medians": statistics.median([f["median"] for f in frames]),
        "mean_of_all_marks": round(statistics.mean(marks), 2),
    }


def kept(data, set_aside):
    return {r: v for r, v in data.items() if r not in set_aside}


def main() -> int:
    b = summary(BASE)
    i_all, i_kept = summary(INTERIM), summary(kept(INTERIM, INTERIM_SET_ASIDE))
    print("base (UI-4 final):", b["overall"], "mean", b["mean_of_all_marks"])
    print("interim, all three:", i_all["overall"], "mean", i_all["mean_of_all_marks"],
          "| set aside", INTERIM_SET_ASIDE, "-> kept", i_kept["overall"], "mean", i_kept["mean_of_all_marks"])
    if not AFTER:
        print("AFTER is empty — fill it from the final readers' reports")
        return 1
    a_all = summary(AFTER)
    a = summary(kept(AFTER, AFTER_SET_ASIDE))
    if "--json" in sys.argv:
        print(json.dumps({"before": b, "interim": i_all, "after": a_all}, indent=1))
    print("final, all three:", a_all["overall"], "mean", a_all["mean_of_all_marks"])
    if AFTER_SET_ASIDE:
        print("final, set aside", AFTER_SET_ASIDE, "-> kept", a["overall"], "mean", a["mean_of_all_marks"])
    print("overall before", b["overall"], "after", a_all["overall"], "| median", b["overall_median"], "->",
          a_all["overall_median"])
    print("mean of the marks", b["mean_of_all_marks"], "->", a_all["mean_of_all_marks"])
    print("median of frame medians", b["median_of_frame_medians"], "->", a_all["median_of_frame_medians"])
    up = down = same = 0
    for k in range(30):
        d = a_all["frames"][k]["median"] - b["frames"][k]["median"]
        up += d > 0
        down += d < 0
        same += d == 0
        mark = "+" if d > 0 else ("-" if d < 0 else "=")
        print(f"F{k + 1:02d} {NAMES[k]:15} {b['frames'][k]['median']:>4} -> {a_all['frames'][k]['median']:>4} {mark}"
              f"  after {a_all['frames'][k]['scores']}")
    print("frames up", up, "same", same, "down", down)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
