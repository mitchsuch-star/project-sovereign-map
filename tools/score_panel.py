#!/usr/bin/env python
"""Aggregate the three blind scorers' answers (SCORE_FINISH_SPEC.md §4.5).

    .venv/Scripts/python.exe tools/score_panel.py eyes    RUN_DIR
        -> RUN_DIR/eyes_panel.json: the EYES marks two of the three scorers
           agree on (a "cannot judge" is no vote); feed it to
           `score_run.py check --eyes`. The marks are provisional: the user's
           own marks override them.
    .venv/Scripts/python.exe tools/score_panel.py publish RUN_DIR
        -> RUN_DIR/panel.json: each scorer's score = the rule's anchor (the
           low end in RUN_DIR/scores.json, read AFTER `check --eyes`) plus its
           own adjustment, clamped to ±0.25; per pillar the median and the
           spread (max − min) and every flag. `score_run.py compare` reads it.

The answers are RUN_DIR/panel_raw/agent_{1,2,3}.json, each
{"pillar": {"anchor", "adjust", "eyes": {"C2": {"pass", "cite"}}, "cite", "flag"}}.
Built for SF-R (October 5, 2026), which first ran it as a scratch script.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys

ADJUST_LIMIT = 0.25
METHOD = (
    "SCORE_FINISH_SPEC.md §4.5 — three agents with fresh contexts read only panel_packet/; "
    "per pillar: the rule's anchor (scores.json low end, AFTER the panel's majority EYES marks "
    "were applied with `check --eyes`), an adjustment of -0.25/0/+0.25 for feel with one cite; "
    "the median and the spread (max - min) are published. Known leak (as at the baseline): the "
    "agents' system context carries CLAUDE.md, which quotes old impression scores; they were "
    "told to disregard it."
)


def load_answers(run: pathlib.Path) -> list[dict]:
    return [
        json.loads((run / "panel_raw" / f"agent_{i}.json").read_text(encoding="utf-8"))
        for i in (1, 2, 3)
    ]


def majority_eyes(answers: list[dict]) -> dict:
    """{"pillar.C2": {"pass": bool, "evidence": str}} for every EYES item two of
    the three scorers judged the same way. A None mark (cannot judge) is no vote."""
    votes: dict[str, list] = {}
    for n, ans in enumerate(answers, 1):
        for key, v in ans.items():
            for iid, mark in ((v or {}).get("eyes") or {}).items():
                p = mark.get("pass") if isinstance(mark, dict) else mark
                cite = mark.get("cite", "") if isinstance(mark, dict) else ""
                votes.setdefault(f"{key}.{iid}", []).append((n, p, cite))
    out = {}
    for item, vs in votes.items():
        yes = [x for x in vs if x[1] is True]
        no = [x for x in vs if x[1] is False]
        if len(yes) >= 2 or len(no) >= 2:
            side = yes if len(yes) >= 2 else no
            out[item] = {
                "pass": len(yes) >= 2,
                "evidence": (f"panel {len(side)} of 3 (provisional — the user's mark overrides): "
                             f"{side[0][2][:160]}"),
            }
    return out


def publish(answers: list[dict], scores: dict) -> dict:
    pillars = scores.get("pillars") or scores

    def anchor_of(key):
        sc = pillars.get(key) or {}
        low = sc.get("low", sc.get("score"))
        return None if low is None else float(low)

    panels = []
    for ans in answers:
        p = {}
        for key, v in ans.items():
            anchor = anchor_of(key)
            adj = max(-ADJUST_LIMIT, min(ADJUST_LIMIT, float((v or {}).get("adjust") or 0)))
            p[key] = {**(v or {}), "anchor": anchor,
                      "score": None if anchor is None else round(anchor + adj, 2)}
        panels.append(p)
    published = {}
    for key in sorted({k for p in panels for k in p}):
        vals = [p[key]["score"] for p in panels if key in p and p[key]["score"] is not None]
        published[key] = {
            "anchor": anchor_of(key),
            "median": round(statistics.median(vals), 2) if vals else None,
            "spread": round(max(vals) - min(vals), 2) if vals else None,
            "adjustments": [p.get(key, {}).get("adjust") for p in panels],
            "flags": [p.get(key, {}).get("flag") for p in panels if p.get(key, {}).get("flag")],
        }
    return {"method": METHOD, "panels": panels, "published": published}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=("eyes", "publish"))
    ap.add_argument("run")
    args = ap.parse_args(argv)
    run = pathlib.Path(args.run)
    answers = load_answers(run)
    out = sys.stdout
    if args.mode == "eyes":
        marks = majority_eyes(answers)
        (run / "eyes_panel.json").write_text(json.dumps(marks, indent=1, ensure_ascii=False),
                                             encoding="utf-8")
        out.write(f"eyes: {len(marks)} items marked by two of three\n")
    else:
        scores = json.loads((run / "scores.json").read_text(encoding="utf-8"))
        panel = publish(answers, scores)
        (run / "panel.json").write_text(json.dumps(panel, indent=1, ensure_ascii=False),
                                        encoding="utf-8")
        out.write(f"panel: {len(panel['published'])} pillars published\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
