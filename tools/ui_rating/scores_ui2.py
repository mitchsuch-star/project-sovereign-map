"""The blind re-rating, tabulated against the baseline (the same rubric, the same 30 frame ids, fresh readers)."""
import json
import statistics
import sys

BASE = {
    "R1": ([8, 6, 7, 7, 7, 7, 6, 6, 8, 7, 6, 7, 6, 8, 7, 6, 7, 7, 7, 8, 7, 8, 8, 5, 7, 7, 8, 7, 8, 7], 7),
    "R2": ([8, 6, 7, 7, 7, 6, 6, 6, 7, 6, 6, 6, 6, 7, 7, 5, 7, 7, 6, 8, 6, 8, 8, 5, 6, 7, 8, 7, 7, 7], 7),
    "R3": ([7, 6, 6, 7, 7, 6, 6, 6, 7, 6, 6, 6, 6, 7, 7, 6, 7, 7, 7, 8, 6, 8, 7, 5, 6, 7, 8, 7, 7, 7], 7),
}
AFTER = {
    "R1": ([7, 6, 7, 7, 8, 7, 7, 8, 7, 7, 6, 6, 6, 7, 7, 6, 7, 7, 7, 8, 6, 8, 7, 6, 6, 8, 8, 7, 7, 7], 7),
    "R2": ([8, 6, 7, 7, 8, 7, 7, 8, 7, 7, 6, 6, 6, 7, 7, 5, 7, 7, 7, 8, 6, 7, 7, 6, 6, 8, 8, 7, 8, 7], 7),
    "R3": ([7, 6, 6, 7, 8, 7, 8, 8, 7, 7, 6, 6, 6, 7, 7, 5, 7, 8, 7, 9, 5, 8, 7, 5, 6, 8, 8, 6, 8, 8], 7),
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


b, a = summary(BASE), summary(AFTER)
out = {"before": b, "after": a}
if "--json" in sys.argv:
    print(json.dumps(out, indent=1))
print("overall before", b["overall"], "after", a["overall"], "| median", b["overall_median"], "->", a["overall_median"])
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
    print(f"F{i + 1:02d} {NAMES[i]:15} {b['frames'][i]['median']:>4} -> {a['frames'][i]['median']:>4} {mark}  after {a['frames'][i]['scores']}")
print("frames up", up, "same", same, "down", down)
spread = sum(1 for f in a["frames"] if f["range"] == 0), sum(1 for f in a["frames"] if f["range"] == 1), sum(1 for f in a["frames"] if f["range"] >= 2)
print("after spread: unanimous / 1 / 2+ =", spread)
